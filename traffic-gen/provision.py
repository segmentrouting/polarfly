#!/usr/bin/env python3
"""
WMP-PolarFly host route/address provisioning.

For a curated list of (source switch, destination switch) pairs, this:
  1. Computes each pair's SP + NSP paths and segment lists (reusing
     path_calculator.py's graph logic and topogen2's wiring/addressing).
  2. Assigns the destination host one additional IPv6 address per forward
     path (within its existing host /64 subnet).
  3. Pushes, via `docker exec` against already-running containers:
       - destination host: the extra `ip -6 addr add` commands
       - source host: one `ip -6 route ... encap seg6 mode encap.red
         segs ...` per forward path (SP + each NSP)
       - destination host: a *single* return route via the SP path only,
         targeting the source host's existing primary address -- this is
         just for basic two-way reachability (iperf3's control channel is
         TCP even for UDP throughput tests), not part of what's being
         measured. Only the forward direction's split across SP+NSP is
         under test.

Mirrors q7/sonic/q7-config.sh's deploy-time push pattern: runs AFTER
containerlab deploy against already-running containers, not baked into the
static topogen2-generated clab.yaml, since which pairs get tested varies
per experiment.

Usage:
  python3 traffic-gen/provision.py --q 7 --pair sw001 sw019 --pair sw002 sw033
  python3 traffic-gen/provision.py --q 7 --pair sw001 sw019 --dry-run
"""

from __future__ import annotations

import argparse
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
    segment_list,
)

HOST_IFACE = "eth1"  # matches topogen2/polarfly_clab.py's host exec commands
PATH_ADDR_BASE = 0x10  # forward per-path addrs start at ::10 within the /64


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


def provision_pair(
    switches: List[Dict], adj, u: int, v: int, dry_run: bool, use_uA: bool = False
) -> None:
    u_name = switches[u]["name"]
    v_name = switches[v]["name"]
    u_host = switches[u]["host_name"]
    v_host = switches[v]["host_name"]
    v_prefix = switches[v]["host_subnet"].split("/")[0]  # e.g. "2001:db8:a013::"
    u_primary_addr = switches[u]["host_host_addr"]

    print(f"\n=== provisioning {u_name} ({u_host}) -> {v_name} ({v_host}) ===")

    sp, nsps = forward_paths(adj, u, v)
    all_paths: List[List[int]] = [sp] + nsps

    # 1. Destination host: one extra address per forward path.
    for i, _mids in enumerate(all_paths):
        addr = f"{v_prefix}{PATH_ADDR_BASE + i:x}"
        docker_exec(
            v_host,
            ["ip", "-6", "addr", "add", f"{addr}/64", "dev", HOST_IFACE, "nodad"],
            dry_run,
        )

    # 2. Source host: one seg6 route per forward path.
    for i, mids in enumerate(all_paths):
        addr = f"{v_prefix}{PATH_ADDR_BASE + i:x}"
        segs = segment_list(switches, u, mids, v, use_uA)
        docker_exec(
            u_host,
            [
                "ip", "-6", "route", "add", f"{addr}/128",
                "encap", "seg6", "mode", "encap.red",
                "segs", ",".join(segs),
                "dev", HOST_IFACE,
            ],
            dry_run,
        )
        label = "SP" if i == 0 else f"NSP{i - 1}"
        print(f"    {label}: {addr} via {'->'.join(switches[m]['name'] for m in mids)} "
              f"segs={segs}")

    # 3. Return direction: single SP-only route, for reachability only.
    w = sp[0]
    return_segs = segment_list(switches, v, [w], u, use_uA)
    docker_exec(
        v_host,
        [
            "ip", "-6", "route", "add", f"{u_primary_addr}/128",
            "encap", "seg6", "mode", "encap.red",
            "segs", ",".join(return_segs),
            "dev", HOST_IFACE,
        ],
        dry_run,
    )
    print(f"    return path (reachability only): {u_primary_addr} "
          f"via {switches[w]['name']} segs={return_segs}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--q", type=int, default=7)
    ap.add_argument(
        "--pair", nargs=2, action="append", metavar=("SRC", "DST"), default=[],
        help="a switch pair to provision, e.g. --pair sw001 sw019 "
             "(repeatable)",
    )
    ap.add_argument("--dry-run", action="store_true", help="print commands, don't run them")
    ap.add_argument(
        "--uA", action="store_true",
        help="use uA (interface-bound End.X) segments per hop instead of the "
             "default uN (node SID, BGP-routed)",
    )
    args = ap.parse_args()

    if not args.pair:
        print("error: at least one --pair SRC DST is required", file=sys.stderr)
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
