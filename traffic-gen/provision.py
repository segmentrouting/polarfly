#!/usr/bin/env python3
"""
WMP-PolarFly host route provisioning.

For a curated list of (source switch, destination switch) pairs, this
installs a *single weighted IPv6 multipath route* per pair on the source
host, targeting the destination host's one real, existing address --
analogous to how multi-tenant frontend-DC traffic gets encapsulated toward
a single remote VTEP-like address. Each nexthop in that multipath route
carries its own `seg6` encap (a different SP/NSP segment list) and its own
integer weight (derived from the WMP weights), so the kernel's own
per-flow hash picks a path per flow, distributed according to those
weights -- rather than us picking a path by addressing a different
destination per path.

For each `--pair`, this:
  1. Bumps both hosts' `eth1` (the host-to-switch link) to jumbo MTU 9100,
     matching the switch-side host-facing port (`q7-config.sh` already
     bumps every switch `Ethernet<N>`, fabric and host-facing alike, to
     9100 -- the host side of that same link was never touched and
     defaults to 1500). SRv6's per-hop SID overhead (~32-48 bytes for a
     2-3 SID path) can push an encap.red-encapsulated packet over 1500,
     and Linux's seg6 LWT encap doesn't reliably surface that overhead to
     the TCP stack's MSS/PMTU calculation -- causing fragmentation-driven
     retransmits and depressed throughput, confirmed via retransmits seen
     in earlier single-stream tests.
  2. Sets `net.ipv6.fib_multipath_hash_policy=1` on the source host, so the
     kernel's ECMP/multipath hash includes L4 ports (TCP/UDP source and
     dest port), not just the L3 addresses. This is *required*: the
     default policy (0, L3-only) means every flow between the same two
     hosts always picks the same nexthop no matter how many flows you
     open, since the source/dest addresses never change between paths in
     this design. Confirmed empirically: with the default policy, 100
     different source ports all resolved to the same nexthop; with L4
     hashing enabled, the same 100 ports split ~84/16 against a 4:1 target
     weight.
  3. Installs one multipath route on the source host to the destination's
     real address (`ip -6 route replace <dst>/128 nexthop via <sw-on-link-addr>
     encap seg6 mode encap.red segs ... weight W ...`, one nexthop per
     forward path). IPv6's multipath API requires an explicit `via`
     gateway per nexthop (a bare `dev`-only nexthop is rejected) -- the
     gateway is always the source switch's own address on the host link,
     regardless of which SRv6 path a given nexthop's segments describe.
  4. Installs a single SP-only *return* route (source's real address, one
     nexthop, no multipath) on the destination host, for basic two-way
     reachability only (iperf3's control channel is TCP even for UDP
     tests) -- not part of what's under test.

Mirrors q7/sonic/q7-config.sh's deploy-time push pattern: runs AFTER
containerlab deploy against already-running containers.

Usage:
  python3 traffic-gen/provision.py --q 7 --pair sw001 sw019 --pair sw002 sw033
  python3 traffic-gen/provision.py --q 7 --pair sw001 sw019 --dry-run
  python3 traffic-gen/provision.py --q 7 --pairs-file pairs.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, List, Tuple

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "topogen2")
)
from polarfly_clab import (  # noqa: E402
    is_prime,
    projective_points,
    polarity_edges,
    verify,
    build_wiring,
)
from path_calculator import (  # noqa: E402
    build_adjacency,
    common_neighbor,
    usid_carrier,
    wmp_weights,
)

HOST_IFACE = "eth1"  # matches topogen2/polarfly_clab.py's host exec commands


def sh(cmd: List[str], dry_run: bool) -> None:
    print("+ " + " ".join(cmd))
    if not dry_run:
        subprocess.run(cmd, check=True)


def docker_exec(container: str, inner_cmd: List[str], dry_run: bool) -> None:
    sh(["docker", "exec", container] + inner_cmd, dry_run)


def forward_paths(adj, u: int, v: int) -> Tuple[List[int], List[List[int]]]:
    """Return (sp_relay_as_single_elem_list, list_of_nsp_mid_pairs) for u->v,
    excluding candidates that collide with the relay (see
    path_calculator.compute_pair_paths for why)."""
    w = common_neighbor(adj, u, v)
    nsps: List[List[int]] = []
    for a in sorted(adj[u]):
        if a == w:
            continue
        b = common_neighbor(adj, a, v)
        if b == w:
            continue
        nsps.append([a, b])
    return [w], nsps


def integer_weights(num_nsp: int) -> List[int]:
    """WMP fractions -> small positive integers for `nexthop ... weight N`,
    in [sp, nsp0, nsp1, ...] order. Scales so the smallest weight rounds to
    1 (e.g. 0.4/0.1*6 -> [4,1,1,1,1,1,1])."""
    w = wmp_weights(num_nsp)
    keys = ["sp"] + [f"nsp{i}" for i in range(num_nsp)]
    min_w = min(w[k] for k in keys)
    return [max(1, round(w[k] / min_w)) for k in keys]


def provision_pair(
    switches: List[Dict], adj, u: int, v: int, dry_run: bool, use_uA: bool = False
) -> None:
    u_name = switches[u]["name"]
    v_name = switches[v]["name"]
    u_host = switches[u]["host_name"]
    v_host = switches[v]["host_name"]
    u_via = switches[u]["host_sw_addr"]   # sw's own addr on the u-host link
    v_addr = switches[v]["host_host_addr"]  # destination's one real address
    u_addr = switches[u]["host_host_addr"]  # source's one real address

    print(f"\n=== provisioning {u_name} ({u_host}) -> {v_name} ({v_host}) ===")

    sp, nsps = forward_paths(adj, u, v)
    all_paths: List[List[int]] = [sp] + nsps
    weights = integer_weights(len(nsps))

    # 0a. Jumbo MTU on the host's link to its switch, matching the switch's
    #     own host-facing port (q7-config.sh bumps every switch Ethernet<N>,
    #     fabric and host-facing alike, to 9100). The host side of that same
    #     link was never touched and defaults to 1500 -- SRv6's per-hop SID
    #     overhead (~32-48 bytes for a 2-3 SID path) can push an
    #     encap.red-encapsulated packet over 1500, and Linux's seg6 LWT
    #     encap doesn't reliably surface that overhead to the TCP stack's
    #     MSS/PMTU calculation, causing fragmentation-driven retransmits and
    #     depressed throughput -- confirmed via retransmits seen in earlier
    #     single-stream tests.
    docker_exec(u_host, ["ip", "link", "set", HOST_IFACE, "mtu", "9100", "up"], dry_run)
    docker_exec(v_host, ["ip", "link", "set", HOST_IFACE, "mtu", "9100", "up"], dry_run)

    # 0b. L4-aware ECMP hashing -- required, see module docstring point 1.
    docker_exec(
        u_host,
        ["sysctl", "-w", "net.ipv6.fib_multipath_hash_policy=1"],
        dry_run,
    )

    # 1. One weighted multipath route on the source host, one nexthop per
    #    forward path, all targeting the destination's single real address.
    route_cmd = ["ip", "-6", "route", "replace", f"{v_addr}/128"]
    for i, mids in enumerate(all_paths):
        carrier = usid_carrier(switches, u, mids, v, use_uA)
        route_cmd += [
            "nexthop", "via", u_via,
            "encap", "seg6", "mode", "encap.red",
            "segs", carrier,
            "dev", HOST_IFACE,
            "weight", str(weights[i]),
        ]
        label = "SP" if i == 0 else f"NSP{i - 1}"
        print(f"    {label}: weight={weights[i]} via {'->'.join(switches[m]['name'] for m in mids)} "
              f"segs={carrier}")
    docker_exec(u_host, route_cmd, dry_run)

    # 2. Return direction: single SP-only route, for reachability only.
    w = sp[0]
    return_carrier = usid_carrier(switches, v, [w], u, use_uA)
    docker_exec(
        v_host,
        [
            "ip", "-6", "route", "replace", f"{u_addr}/128",
            "encap", "seg6", "mode", "encap.red",
            "segs", return_carrier,
            "dev", HOST_IFACE,
        ],
        dry_run,
    )
    print(f"    return path (reachability only): {u_addr} "
          f"via {switches[w]['name']} segs={return_carrier}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--q", type=int, default=7)
    ap.add_argument(
        "--pair", nargs=2, action="append", metavar=("SRC", "DST"), default=[],
        help="a switch pair to provision, e.g. --pair sw001 sw019 "
             "(repeatable)",
    )
    ap.add_argument(
        "--pairs-file",
        help="JSON file: a list of [SRC, DST] pairs, e.g. "
             '[["sw001","sw019"], ["sw002","sw033"]] -- combined with any --pair flags',
    )
    ap.add_argument("--dry-run", action="store_true", help="print commands, don't run them")
    ap.add_argument(
        "--uA", action="store_true",
        help="use uA (interface-bound End.X) segments per hop instead of the "
             "default uN (node SID, BGP-routed)",
    )
    args = ap.parse_args()

    pairs = [tuple(p) for p in args.pair]
    if args.pairs_file:
        with open(args.pairs_file) as f:
            pairs.extend(tuple(p) for p in json.load(f))
    args.pair = pairs

    if not args.pair:
        print("error: at least one --pair SRC DST (or --pairs-file) is required", file=sys.stderr)
        return 2
    if not is_prime(args.q):
        print(f"error: q={args.q} is not prime", file=sys.stderr)
        return 2

    points = projective_points(args.q)
    edges, absolute = polarity_edges(points, args.q)
    verify(points, edges, absolute, args.q)
    wiring = build_wiring(points, edges, absolute, args.q, variant="sonic-vs")
    switches = wiring["switches"]
    adj = build_adjacency(wiring["n"], edges)
    name_to_idx = {sw["name"]: sw["idx"] for sw in switches}

    for src_name, dst_name in args.pair:
        if src_name not in name_to_idx or dst_name not in name_to_idx:
            print(f"error: unknown switch name in --pair {src_name} {dst_name}", file=sys.stderr)
            return 2
        u, v = name_to_idx[src_name], name_to_idx[dst_name]
        if v in adj[u]:
            print(f"error: {src_name} and {dst_name} are directly adjacent -- "
                  f"no SP/NSP split to provision for an adjacent pair", file=sys.stderr)
            return 2
        provision_pair(switches, adj, u, v, args.dry_run, args.uA)

    return 0


if __name__ == "__main__":
    sys.exit(main())
