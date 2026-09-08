#!/usr/bin/env python3
"""
WMP-PolarFly traffic generation + weighted-split measurement.

For a pair already provisioned by provision.py, this:
  1. Starts one iperf3 server per forward path (SP + each NSP) on the
     destination host, each on its own port (5201, 5202, ...) -- iperf3's
     default server doesn't multiplex concurrent clients on one port, so
     distinct ports let every path's stream run at the same time.
  2. Launches iperf3 clients on the source host concurrently, one per
     path, each targeting that path's specific destination address (whose
     kernel route -- installed by provision.py -- determines which SP/NSP
     segment list actually carries it) and port. Parallel-stream count
     per client (`-P`) is set proportional to that path's target W-CMP
     weight, so the achieved traffic split approximates the intended
     ratio (e.g. -P 4 for SP, -P 1 for each NSP at the whitepaper's 40/10
     split for q=7).
  3. Collects each client's `--json` output, sums bytes transferred per
     path, and reports the achieved split against the target weights.

Usage:
  python3 traffic-gen/run_test.py --q 7 --pair sw001 sw019 --duration 10
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Dict, List

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
from path_calculator import build_adjacency, wmp_weights  # noqa: E402
from provision import forward_paths, PATH_ADDR_BASE  # noqa: E402

BASE_PORT = 5201


def path_label(i: int) -> str:
    return "SP" if i == 0 else f"NSP{i - 1}"


def start_servers(dst_host: str, num_paths: int) -> None:
    for i in range(num_paths):
        port = BASE_PORT + i
        subprocess.run(
            ["docker", "exec", "-d", dst_host, "iperf3", "-s", "-p", str(port)],
            check=True,
        )
    time.sleep(1.0)  # let servers bind before clients connect


def stop_servers(dst_host: str) -> None:
    subprocess.run(["docker", "exec", dst_host, "pkill", "-f", "iperf3 -s"], check=False)


def run_clients(
    src_host: str, v_prefix: str, num_paths: int, weights: Dict[str, float],
    duration: int,
) -> List[Dict]:
    weight_keys = ["sp"] + [f"nsp{i}" for i in range(num_paths - 1)]
    max_w = max(weights[k] for k in weight_keys)
    # Parallel-stream count per path, proportional to its weight relative to
    # the largest (so the biggest-weight path gets the most streams).
    streams = {k: max(1, round(4 * weights[k] / max_w)) for k in weight_keys}

    procs = []
    for i in range(num_paths):
        addr = f"{v_prefix}{PATH_ADDR_BASE + i:x}"
        port = BASE_PORT + i
        key = weight_keys[i]
        cmd = [
            "docker", "exec", src_host, "iperf3",
            "-c", addr, "-p", str(port),
            "-P", str(streams[key]),
            "-t", str(duration),
            "--json",
        ]
        print(f"+ {' '.join(cmd)}  (target weight={weights[key]:.3f}, streams={streams[key]})")
        procs.append((path_label(i), key, subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)))

    results = []
    for label, key, proc in procs:
        out, err = proc.communicate()
        if proc.returncode != 0:
            print(f"  ! {label} iperf3 client failed: {err.decode(errors='replace')[:300]}", file=sys.stderr)
            results.append(dict(label=label, key=key, bytes=0, ok=False))
            continue
        data = json.loads(out)
        total_bytes = data["end"]["sum_received"]["bytes"] if "sum_received" in data["end"] else data["end"]["sum_sent"]["bytes"]
        results.append(dict(label=label, key=key, bytes=total_bytes, ok=True))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--q", type=int, default=7)
    ap.add_argument("--pair", nargs=2, required=True, metavar=("SRC", "DST"))
    ap.add_argument("--duration", type=int, default=10, help="seconds per iperf3 client (default: 10)")
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
    weights = wmp_weights(len(nsps))

    print(f"=== testing {src_name} -> {dst_name}: {num_paths} paths, "
          f"{args.duration}s per client ===")
    start_servers(dst_host, num_paths)
    try:
        results = run_clients(src_host, v_prefix, num_paths, weights, args.duration)
    finally:
        stop_servers(dst_host)

    total = sum(r["bytes"] for r in results)
    weight_keys = ["sp"] + [f"nsp{i}" for i in range(num_paths - 1)]
    print(f"\n{'path':<8}{'target %':>10}{'achieved %':>12}{'bytes':>14}")
    for r, key in zip(results, weight_keys):
        target_pct = 100 * weights[key]
        achieved_pct = 100 * r["bytes"] / total if total else 0.0
        flag = "" if r["ok"] else "  (FAILED)"
        print(f"{r['label']:<8}{target_pct:>9.1f}%{achieved_pct:>11.1f}%{r['bytes']:>14d}{flag}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
