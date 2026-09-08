#!/usr/bin/env python3
"""
WMP-PolarFly per-path protocol correctness check.

For a pair already provisioned by provision.py, sends one UDP packet per
forward path (SP + each NSP) from the source host to that path's specific
destination address -- letting the *kernel's own* seg6 encapsulation (via
the route provision.py installed) do the real SRv6 work, rather than
hand-building the SRv6 header in scapy. A `tcpdump` capture on the
destination confirms each packet actually arrives with its expected
payload, which is a real end-to-end proof that path_calculator.py's
segment list for that path is correct and the fabric processes it as
expected -- not just a local address-format check.

Sends are via scapy so each path's packet carries a distinctive payload
(source name + path label), making capture output unambiguous about which
path succeeded.

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
from path_calculator import build_adjacency  # noqa: E402
from provision import forward_paths, PATH_ADDR_BASE, HOST_IFACE  # noqa: E402
from run_test import path_label  # noqa: E402

TEST_PORT = 9999


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
        "from scapy.all import IPv6, UDP, send; "
        f"send(IPv6(dst='{addr}')/UDP(dport={TEST_PORT})/'{payload}', verbose=0)"
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
    v_prefix = switches[v]["host_subnet"].split("/")[0]

    sp, nsps = forward_paths(adj, u, v)
    num_paths = 1 + len(nsps)

    print(f"=== verifying {src_name} -> {dst_name}: {num_paths} paths ===")
    results: List[bool] = []
    for i in range(num_paths):
        addr = f"{v_prefix}{PATH_ADDR_BASE + i:x}"
        results.append(check_path(src_host, dst_host, addr, path_label(i)))

    ok_count = sum(results)
    print(f"\n{ok_count}/{num_paths} paths confirmed delivered")
    return 0 if ok_count == num_paths else 1


if __name__ == "__main__":
    sys.exit(main())
