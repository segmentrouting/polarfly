#!/usr/bin/env python3
"""
WMP-PolarFly per-path protocol correctness check.

For a pair already provisioned by provision.py with a single weighted
multipath route, this checks each forward path (SP + each NSP) in
isolation: it temporarily *replaces* the source host's route to the
destination with a single-nexthop route carrying just that one path's
seg6 encap (no multipath, so there's no ambiguity about which path a test
packet takes), sends one UDP packet, and confirms via a `tcpdump` capture
on the destination that it arrives with its expected payload -- a real
end-to-end proof that path_calculator.py's segment list for that path is
correct and the fabric processes it as expected, not just a local
address-format check.

After testing every path, restores the real weighted multipath route (the
same one provision.py installs) so the pair is left as it was for
run_test.py.

Sends use a plain kernel-routed UDP socket (Python's `socket` module), not
scapy's `send()` -- scapy builds and injects packets itself, bypassing the
kernel's routing table entirely, so it never picks up the `encap seg6`
lightweight tunnel route this checks against (confirmed empirically: scapy
`send()` logs "No route found for IPv6 destination" for exactly this
reason, while a plain `socket.sendto()` correctly takes the seg6-encapped
route and the SRH is visible in the capture). Each path's packet carries a
distinctive payload (source name + path label), making capture output
unambiguous about which path succeeded.

Usage:
  python3 traffic-gen/verify_packet.py --q 7 --pair sw001 sw019
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from typing import List

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
from path_calculator import build_adjacency, usid_carrier  # noqa: E402
from provision import HOST_IFACE, forward_paths, integer_weights  # noqa: E402
from run_test import path_label  # noqa: E402

TEST_PORT = 9999


def install_single_path_route(src_host: str, v_addr: str, carrier: str) -> None:
    subprocess.run(
        [
            "docker", "exec", src_host, "ip", "-6", "route", "replace", f"{v_addr}/128",
            "encap", "seg6", "mode", "encap.red", "segs", carrier,
            "dev", HOST_IFACE,
        ],
        check=True,
    )


def install_multipath_route(
    src_host: str, u_via: str, v_addr: str, all_paths, weights: List[int], switches, u, v, use_uA
) -> None:
    route_cmd = ["docker", "exec", src_host, "ip", "-6", "route", "replace", f"{v_addr}/128"]
    for i, mids in enumerate(all_paths):
        carrier = usid_carrier(switches, u, mids, v, use_uA)
        route_cmd += [
            "nexthop", "via", u_via,
            "encap", "seg6", "mode", "encap.red",
            "segs", carrier,
            "dev", HOST_IFACE,
            "weight", str(weights[i]),
        ]
    subprocess.run(route_cmd, check=True)


def check_path(src_host: str, dst_host: str, addr: str, label: str) -> bool:
    payload = f"{src_host}:{label}"
    # Capture on the destination in the background, then send from source.
    capture = subprocess.Popen(
        [
            "docker", "exec", dst_host, "timeout", "3",
            "tcpdump", "-i", HOST_IFACE, "-A", "-c", "1",
            "-w", "-", "udp", "and", "port", str(TEST_PORT),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    time.sleep(0.3)  # let tcpdump attach before we send

    send_script = (
        "import socket; "
        "s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM); "
        f"s.sendto({payload!r}.encode(), ('{addr}', {TEST_PORT}))"
    )
    subprocess.run(
        ["docker", "exec", src_host, "python3", "-c", send_script], check=True,
    )

    out, _ = capture.communicate(timeout=5)
    ok = payload.encode() in out
    print(f"  {label:<6} -> {addr}: {'OK, payload confirmed' if ok else 'FAILED, no matching capture'}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--q", type=int, default=7)
    ap.add_argument("--pair", nargs=2, required=True, metavar=("SRC", "DST"))
    ap.add_argument(
        "--uA", action="store_true",
        help="test uA segments instead of the default uN -- must match "
             "whatever provision.py used for this pair",
    )
    args = ap.parse_args()

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

    src_name, dst_name = args.pair
    u, v = name_to_idx[src_name], name_to_idx[dst_name]
    src_host = switches[u]["host_name"]
    dst_host = switches[v]["host_name"]
    u_via = switches[u]["host_sw_addr"]
    v_addr = switches[v]["host_host_addr"]

    sp, nsps = forward_paths(adj, u, v)
    all_paths = [sp] + nsps
    num_paths = len(all_paths)
    weights = integer_weights(len(nsps))

    print(f"=== verifying {src_name} -> {dst_name}: {num_paths} paths ===")
    results: List[bool] = []
    for i, mids in enumerate(all_paths):
        carrier = usid_carrier(switches, u, mids, v, args.uA)
        install_single_path_route(src_host, v_addr, carrier)
        results.append(check_path(src_host, dst_host, v_addr, path_label(i)))

    print("\nrestoring weighted multipath route ...")
    install_multipath_route(src_host, u_via, v_addr, all_paths, weights, switches, u, v, args.uA)

    ok_count = sum(results)
    print(f"\n{ok_count}/{num_paths} paths confirmed delivered")
    return 0 if ok_count == num_paths else 1


if __name__ == "__main__":
    sys.exit(main())
