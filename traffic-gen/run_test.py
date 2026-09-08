#!/usr/bin/env python3
"""
WMP-PolarFly traffic generation + weighted-split measurement.

For a pair already provisioned by provision.py's single weighted multipath
route, this:
  1. Starts one iperf3 server on the destination host (one port -- there's
     only one destination address now, not one per path).
  2. Runs one iperf3 client on the source host with many parallel streams
     (`-P N`), all targeting that single destination address/port. Each
     stream gets its own ephemeral source port from the OS, which is
     exactly the entropy the kernel's (now L4-aware, per provision.py)
     multipath hash needs to spread streams across the weighted nexthops.
  3. Since every stream now goes to the *same* address, we can't tell
     paths apart by destination the way the old design did. Instead: for
     each stream, `--json` gives us its local (source) port (from
     `start.connected[]`) and its byte count (from `end.streams[].sender`,
     matched by socket id). For each stream's source port, `ip -6 route
     get ... sport <port> dport <port>` on the source host performs the
     exact same hash lookup real forwarding uses (this is the standard,
     reliable way to predict/attribute ECMP decisions in Linux -- it's not
     a separate mechanism from real forwarding, same FIB lookup code
     path), returning which nexthop's segment list that stream actually
     used. Matching the resolved segment list's first segment against
     each path's precomputed first segment (unique per path, since every
     path's first hop differs) attributes that stream's bytes to a path.
  4. Sums attributed bytes per path and reports achieved-vs-target split.

Usage:
  python3 traffic-gen/run_test.py --q 7 --pair sw001 sw019
  python3 traffic-gen/run_test.py --q 7 --pair sw001 sw019 --streams 200 --duration 5
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from typing import Dict, List, Optional

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
from path_calculator import build_adjacency, segment_list, wmp_weights  # noqa: E402
from provision import forward_paths  # noqa: E402

SERVER_PORT = 5201
SEGS_RE = re.compile(r"segs \d+ \[ ([a-f0-9:, ]+?) \]")


def path_label(i: int) -> str:
    return "SP" if i == 0 else f"NSP{i - 1}"


def start_server(dst_host: str) -> None:
    subprocess.run(["docker", "exec", "-d", dst_host, "iperf3", "-s", "-p", str(SERVER_PORT)], check=True)
    time.sleep(1.0)


def stop_server(dst_host: str) -> None:
    subprocess.run(["docker", "exec", dst_host, "pkill", "-f", "iperf3 -s"], check=False)


def run_client(src_host: str, dst_addr: str, streams: int, duration: int) -> Dict:
    cmd = [
        "docker", "exec", src_host, "iperf3",
        "-c", dst_addr, "-p", str(SERVER_PORT),
        "-P", str(streams), "-t", str(duration), "--json",
    ]
    print(f"+ {' '.join(cmd)}")
    out = subprocess.run(cmd, capture_output=True, check=True).stdout
    return json.loads(out)


def resolve_path_for_port(
    src_host: str, src_addr: str, dst_addr: str, sport: int
) -> Optional[str]:
    """Which nexthop (as a raw comma/space-joined segs string) would a flow
    from this source port actually take, per the kernel's own FIB lookup."""
    out = subprocess.run(
        [
            "docker", "exec", src_host, "ip", "-6", "route", "get", dst_addr,
            "from", src_addr, "sport", str(sport), "dport", str(SERVER_PORT),
        ],
        capture_output=True, text=True,
    ).stdout
    m = SEGS_RE.search(out)
    if not m:
        return None
    return m.group(1).split()[0]  # first segment, unique per path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--q", type=int, default=7)
    ap.add_argument("--pair", nargs=2, required=True, metavar=("SRC", "DST"))
    ap.add_argument(
        "--streams", type=int, default=40,
        help="parallel iperf3 streams (default: 40 -- empirically the largest "
             "-P this lab's veth/seg6-encap path reliably sustains; higher "
             "values (tested up to 100) intermittently fail with 'unable to "
             "receive results' under this containerlab setup's overhead)",
    )
    ap.add_argument("--duration", type=int, default=5, help="seconds (default: 5)")
    ap.add_argument(
        "--uA", action="store_true",
        help="match against uA segments instead of the default uN -- must match "
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
    src_addr = switches[u]["host_host_addr"]
    dst_addr = switches[v]["host_host_addr"]

    sp, nsps = forward_paths(adj, u, v)
    all_paths = [sp] + nsps
    num_paths = len(all_paths)
    weights = wmp_weights(len(nsps))
    weight_keys = ["sp"] + [f"nsp{i}" for i in range(len(nsps))]

    # First segment of each path's segment list -> path label. Unique per
    # path since every path's first hop is different.
    first_seg_to_label: Dict[str, str] = {}
    for i, mids in enumerate(all_paths):
        segs = segment_list(switches, u, mids, v, args.uA)
        first_seg_to_label[segs[0]] = path_label(i)

    print(f"=== testing {src_name} -> {dst_name}: {num_paths} paths, "
          f"{args.streams} streams, {args.duration}s ===")

    start_server(dst_host)
    try:
        data = run_client(src_host, dst_addr, args.streams, args.duration)
    finally:
        stop_server(dst_host)

    local_port = {c["socket"]: c["local_port"] for c in data["start"]["connected"]}
    bytes_by_socket = {s["sender"]["socket"]: s["sender"]["bytes"] for s in data["end"]["streams"]}

    bytes_by_label: Dict[str, int] = {path_label(i): 0 for i in range(num_paths)}
    unresolved = 0
    for sock, port in local_port.items():
        first_seg = resolve_path_for_port(src_host, src_addr, dst_addr, port)
        label = first_seg_to_label.get(first_seg)
        if label is None:
            unresolved += 1
            continue
        bytes_by_label[label] += bytes_by_socket.get(sock, 0)

    total = sum(bytes_by_label.values())
    print(f"\n{'path':<8}{'target %':>10}{'achieved %':>12}{'bytes':>14}")
    for i, key in enumerate(weight_keys):
        label = path_label(i)
        target_pct = 100 * weights[key]
        b = bytes_by_label[label]
        achieved_pct = 100 * b / total if total else 0.0
        print(f"{label:<8}{target_pct:>9.1f}%{achieved_pct:>11.1f}%{b:>14d}")
    if unresolved:
        print(f"\n({unresolved}/{len(local_port)} streams could not be attributed to a path)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
