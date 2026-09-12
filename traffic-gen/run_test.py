#!/usr/bin/env python3
"""
WMP-PolarFly traffic generation + weighted-split measurement.

For one or more pairs already provisioned by provision.py's single
weighted multipath route, this:
  1. Starts one iperf3 server per involved destination host (one port --
     there's only one destination address per pair now, not one per path).
  2. Launches one iperf3 client per pair, ALL CONCURRENTLY (each pair's
     client is a separate `docker exec` against a different source
     container, so they run in true parallel, not just interleaved) --
     this is what exercises real fabric-wide load, multiple source/dest
     hosts contending for shared links at once, rather than one pair's
     traffic in isolation. Each client opens many parallel streams
     (`-P N`) to its own pair's single destination address/port; each
     stream gets its own ephemeral source port from the OS, which is
     exactly the entropy the kernel's (now L4-aware, per provision.py)
     multipath hash needs to spread streams across that pair's weighted
     nexthops.
  3. Since every stream within a pair targets the *same* address, paths
     can't be told apart by destination. Instead: for each stream,
     `--json` gives us its local (source) port (from `start.connected[]`)
     and its byte count (matched by socket id). For each stream's source
     port, `ip -6 route get ... sport <port> dport <port>` on the source
     host performs the exact same hash lookup real forwarding uses (this
     is the standard, reliable way to predict/attribute ECMP decisions in
     Linux -- it's not a separate mechanism from real forwarding, same FIB
     lookup code path), returning which nexthop's single compressed uSID
     carrier (see path_calculator.usid_carrier) that stream actually
     resolved to. Matching that carrier against each path's precomputed
     carrier (unique per path, since every path's hop chain differs)
     attributes that stream's bytes to a path.
  4. Prints each pair's achieved-vs-target split, then a grand aggregate
     across all pairs.

`--udp` switches every client to UDP mode (`-u -b <bandwidth>`, `-l
<length>` if given). TCP's retransmits mask real drop rate (a lost
segment just gets resent, so sent==received eventually regardless of
loss); UDP has no such recovery, so iperf3's receiver-side
`lost_packets`/`lost_percent` -- reported per path and in aggregate -- are
a direct, unmasked loss measurement. UDP's route-hash lookup also needs
an explicit `ipproto udp` on the `ip route get` probe -- confirmed
empirically that omitting it (which is what the TCP path relies on, since
TCP happens to be `ip route get`'s implicit default protocol) resolves to
a *different*, wrong nexthop for a UDP 5-tuple.

`--sweep START STOP STEP` (Mbps per stream, UDP only) repeats the whole
concurrent multi-pair test at each bandwidth step from START to STOP,
reporting aggregate throughput/loss at each and flagging the first step
where loss exceeds `--loss-threshold` (default 1.0%) -- a way to find
where this lab's software dataplane actually saturates, since a fixed
UDP send rate (unlike TCP, which self-paces via ACKs) will happily exceed
real capacity and just drop the difference.

Usage:
  python3 traffic-gen/run_test.py --q 7 --pair sw001 sw019
  python3 traffic-gen/run_test.py --q 7 --pairs-file pairs.json --duration 5
  python3 traffic-gen/run_test.py --q 7 --pairs-file pairs.json --udp --bandwidth 100M
  python3 traffic-gen/run_test.py --q 7 --pairs-file pairs.json --udp --sweep 25 200 25
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

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
from path_calculator import build_adjacency, usid_carrier, wmp_weights  # noqa: E402
from provision import forward_paths  # noqa: E402

SERVER_PORT = 5201
SEGS_RE = re.compile(r"segs \d+ \[ ([a-f0-9:, ]+?) \]")


def path_label(i: int) -> str:
    return "SP" if i == 0 else f"NSP{i - 1}"


@dataclass
class PairCtx:
    src_name: str
    dst_name: str
    src_host: str
    dst_host: str
    src_addr: str
    dst_addr: str
    all_paths: List[List[int]]
    weights: Dict[str, float]
    weight_keys: List[str] = field(default_factory=list)
    carrier_to_label: Dict[str, str] = field(default_factory=dict)

    @property
    def num_paths(self) -> int:
        return len(self.all_paths)

    @property
    def label(self) -> str:
        return f"{self.src_name}->{self.dst_name}"


def build_pair_ctx(switches, adj, name_to_idx, src_name: str, dst_name: str, use_uA: bool) -> PairCtx:
    if src_name not in name_to_idx or dst_name not in name_to_idx:
        raise ValueError(f"unknown switch name in pair {src_name} {dst_name}")
    u, v = name_to_idx[src_name], name_to_idx[dst_name]
    if v in adj[u]:
        raise ValueError(
            f"{src_name} and {dst_name} are directly adjacent -- "
            f"no SP/NSP split to test for an adjacent pair"
        )
    sp, nsps = forward_paths(adj, u, v)
    all_paths = [sp] + nsps
    weights = wmp_weights(len(nsps))
    weight_keys = ["sp"] + [f"nsp{i}" for i in range(len(nsps))]
    carrier_to_label = {
        usid_carrier(switches, u, mids, v, use_uA): path_label(i)
        for i, mids in enumerate(all_paths)
    }
    return PairCtx(
        src_name=src_name, dst_name=dst_name,
        src_host=switches[u]["host_name"], dst_host=switches[v]["host_name"],
        src_addr=switches[u]["host_host_addr"], dst_addr=switches[v]["host_host_addr"],
        all_paths=all_paths, weights=weights, weight_keys=weight_keys,
        carrier_to_label=carrier_to_label,
    )


def start_servers(dst_hosts: List[str]) -> None:
    for h in sorted(set(dst_hosts)):
        subprocess.run(["docker", "exec", "-d", h, "iperf3", "-s", "-p", str(SERVER_PORT)], check=True)
    time.sleep(1.0)


def stop_servers(dst_hosts: List[str]) -> None:
    for h in sorted(set(dst_hosts)):
        subprocess.run(["docker", "exec", h, "pkill", "-f", "iperf3 -s"], check=False)


def launch_client(
    ctx: PairCtx, streams: int, duration: int,
    udp: bool, bandwidth: str, length: Optional[int],
) -> subprocess.Popen:
    cmd = [
        "docker", "exec", ctx.src_host, "iperf3",
        "-c", ctx.dst_addr, "-p", str(SERVER_PORT),
        "-P", str(streams), "-t", str(duration),
    ]
    if udp:
        cmd += ["-u", "-b", bandwidth]
    if length:
        cmd += ["-l", str(length)]
    cmd += ["--json"]
    print(f"+ {' '.join(cmd)}")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def resolve_path_for_port(
    src_host: str, src_addr: str, dst_addr: str, sport: int, proto: str = "tcp"
) -> Optional[str]:
    """Which nexthop's single compressed uSID carrier would a flow from this
    source port actually take, per the kernel's own FIB lookup. `proto`
    must match the real flow's protocol -- confirmed empirically that a UDP
    5-tuple resolves to a different (wrong) nexthop if `ipproto udp` isn't
    given explicitly."""
    out = subprocess.run(
        [
            "docker", "exec", src_host, "ip", "-6", "route", "get", dst_addr,
            "from", src_addr, "ipproto", proto,
            "sport", str(sport), "dport", str(SERVER_PORT),
        ],
        capture_output=True, text=True,
    ).stdout
    m = SEGS_RE.search(out)
    if not m:
        return None
    return m.group(1).split()[0]  # each nexthop carries exactly one seg now


def _launch_and_collect(
    pairs_ctx: List[PairCtx], streams: int, duration: int,
    udp: bool, bandwidth: str, length: Optional[int],
) -> List[Tuple[PairCtx, Optional[Dict]]]:
    procs = [(c, launch_client(c, streams, duration, udp, bandwidth, length)) for c in pairs_ctx]
    results: List[Tuple[PairCtx, Optional[Dict]]] = []
    for c, proc in procs:
        out, err = proc.communicate()
        if proc.returncode != 0:
            print(f"  ! {c.label} iperf3 client failed: {err.decode(errors='replace')[:300]}",
                  file=sys.stderr)
            results.append((c, None))
            continue
        results.append((c, json.loads(out)))
    return results


def run_once(
    pairs_ctx: List[PairCtx], streams: int, duration: int,
    udp: bool, bandwidth: str, length: Optional[int],
) -> List[Tuple[PairCtx, Optional[Dict]]]:
    """Run one concurrent test across all pairs; return each pair's parsed
    iperf3 JSON (None if that pair's client still failed after one retry).

    A client occasionally fails with an empty-stderr "unable to read from
    stream socket: Resource temporarily unavailable" under heavy
    concurrent `docker exec` load -- confirmed transient (contention on
    the orchestrating host itself, not the fabric), and more likely on a
    container doing double duty as both a client for one pair and the
    iperf3 server for another pair in the same batch. Failed pairs get
    one retry (after a short pause) before being reported as failed."""
    dst_hosts = [c.dst_host for c in pairs_ctx]
    start_servers(dst_hosts)
    try:
        results = _launch_and_collect(pairs_ctx, streams, duration, udp, bandwidth, length)
        failed = [c for c, d in results if d is None]
        if failed:
            print(f"  retrying {len(failed)} failed client(s) after 1s: "
                  f"{', '.join(c.label for c in failed)}")
            time.sleep(1.0)
            retried_by_label = {
                c.label: d
                for c, d in _launch_and_collect(failed, streams, duration, udp, bandwidth, length)
            }
            results = [
                (c, retried_by_label.get(c.label, d) if d is None else d)
                for c, d in results
            ]
    finally:
        stop_servers(dst_hosts)
    return results


def attribute(ctx: PairCtx, data: Dict, proto: str, udp: bool) -> Dict:
    local_port = {c["socket"]: c["local_port"] for c in data["start"]["connected"]}
    if udp:
        bytes_by_socket = {s["udp"]["socket"]: s["udp"]["bytes"] for s in data["end"]["streams"]}
        packets_by_socket = {s["udp"]["socket"]: s["udp"]["packets"] for s in data["end"]["streams"]}
        lost_by_socket = {s["udp"]["socket"]: s["udp"]["lost_packets"] for s in data["end"]["streams"]}
    else:
        bytes_by_socket = {s["sender"]["socket"]: s["sender"]["bytes"] for s in data["end"]["streams"]}
        packets_by_socket = {}
        lost_by_socket = {}

    bytes_by_label = {path_label(i): 0 for i in range(ctx.num_paths)}
    packets_by_label = {path_label(i): 0 for i in range(ctx.num_paths)}
    lost_by_label = {path_label(i): 0 for i in range(ctx.num_paths)}
    unresolved = 0
    for sock, port in local_port.items():
        carrier = resolve_path_for_port(ctx.src_host, ctx.src_addr, ctx.dst_addr, port, proto)
        label = ctx.carrier_to_label.get(carrier)
        if label is None:
            unresolved += 1
            continue
        bytes_by_label[label] += bytes_by_socket.get(sock, 0)
        packets_by_label[label] += packets_by_socket.get(sock, 0)
        lost_by_label[label] += lost_by_socket.get(sock, 0)

    return dict(
        bytes_by_label=bytes_by_label, packets_by_label=packets_by_label,
        lost_by_label=lost_by_label, unresolved=unresolved, num_streams=len(local_port),
    )


def print_pair_report(ctx: PairCtx, attr: Dict, udp: bool) -> None:
    total = sum(attr["bytes_by_label"].values())
    header = f"\n{ctx.label} ({ctx.num_paths} paths):"
    print(header)
    row_header = f"{'path':<8}{'target %':>10}{'achieved %':>12}{'bytes':>14}"
    if udp:
        row_header += f"{'lost pkts':>12}{'lost %':>9}"
    print(row_header)
    for i, key in enumerate(ctx.weight_keys):
        label = path_label(i)
        target_pct = 100 * ctx.weights[key]
        b = attr["bytes_by_label"][label]
        achieved_pct = 100 * b / total if total else 0.0
        row = f"{label:<8}{target_pct:>9.1f}%{achieved_pct:>11.1f}%{b:>14d}"
        if udp:
            pkts, lost = attr["packets_by_label"][label], attr["lost_by_label"][label]
            lost_pct = 100 * lost / pkts if pkts else 0.0
            row += f"{lost:>12d}{lost_pct:>8.1f}%"
        print(row)
    if attr["unresolved"]:
        print(f"  ({attr['unresolved']}/{attr['num_streams']} streams could not be attributed to a path)")


def aggregate_stats(data: Dict, udp: bool) -> Dict:
    if udp:
        s = data["end"].get("sum", {})
        return dict(bytes=s.get("bytes", 0), packets=s.get("packets", 0), lost=s.get("lost_packets", 0))
    sum_sent = data["end"].get("sum_sent", {})
    sum_received = data["end"].get("sum_received", {})
    return dict(
        sent_bytes=sum_sent.get("bytes", 0), retransmits=sum_sent.get("retransmits", 0),
        received_bytes=sum_received.get("bytes", 0),
    )


def print_grand_summary(results: List[Tuple[PairCtx, Optional[Dict]]], duration: int, udp: bool) -> None:
    ok = [(c, d) for c, d in results if d is not None]
    print(f"\n=== grand aggregate across {len(ok)}/{len(results)} pairs, {duration}s window ===")
    if udp:
        total_bytes = total_packets = total_lost = 0
        for c, data in ok:
            s = aggregate_stats(data, True)
            total_bytes += s["bytes"]
            total_packets += s["packets"]
            total_lost += s["lost"]
        lost_pct = 100 * total_lost / total_packets if total_packets else 0.0
        print(f"  transferred: {total_bytes:>14d} bytes  ({8 * total_bytes / duration / 1e9:.2f} Gbps)")
        print(f"  packets: {total_packets}  lost: {total_lost} ({lost_pct:.2f}%)")
    else:
        total_sent = total_received = total_retransmits = 0
        for c, data in ok:
            s = aggregate_stats(data, False)
            total_sent += s["sent_bytes"]
            total_received += s["received_bytes"]
            total_retransmits += s["retransmits"]
        print(f"  sent:      {total_sent:>14d} bytes  ({8 * total_sent / duration / 1e9:.2f} Gbps)"
              f"   retransmits={total_retransmits}")
        print(f"  received:  {total_received:>14d} bytes  ({8 * total_received / duration / 1e9:.2f} Gbps)")


def load_pairs(args) -> List[Tuple[str, str]]:
    pairs = [tuple(p) for p in args.pair]
    if args.pairs_file:
        with open(args.pairs_file) as f:
            pairs.extend(tuple(p) for p in json.load(f))
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[1], formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--q", type=int, default=7)
    ap.add_argument(
        "--pair", nargs=2, action="append", default=[], metavar=("SRC", "DST"),
        help="a switch pair to test (repeatable) -- combined with --pairs-file",
    )
    ap.add_argument(
        "--pairs-file",
        help="JSON file: a list of [SRC, DST] pairs, e.g. "
             '[["sw001","sw019"], ["sw002","sw033"]]',
    )
    ap.add_argument(
        "--streams", type=int, default=40,
        help="parallel iperf3 streams per pair (default: 40 -- empirically the "
             "largest -P this lab's veth/seg6-encap path reliably sustains; "
             "higher values (tested up to 100) intermittently fail with "
             "'unable to receive results' under this containerlab setup's "
             "overhead)",
    )
    ap.add_argument("--duration", type=int, default=5, help="seconds per run (default: 5)")
    ap.add_argument(
        "--uA", action="store_true",
        help="match against uA segments instead of the default uN -- must match "
             "whatever provision.py used for these pairs",
    )
    ap.add_argument(
        "--udp", action="store_true",
        help="use UDP instead of TCP -- gives a direct, unmasked lost_packets/"
             "lost_percent reading (TCP's retransmits recover loss instead of "
             "reporting it)",
    )
    ap.add_argument(
        "--bandwidth", default="100M",
        help="per-stream target bandwidth for --udp, iperf3 -b syntax "
             "(default: 100M -- ignored for TCP, ignored if --sweep given)",
    )
    ap.add_argument(
        "--length", type=int, default=None,
        help="datagram/write size in bytes (iperf3 -l) -- combined with "
             "--bandwidth this sets pps (pps = bandwidth / (8 x length)); "
             "default: iperf3's own default",
    )
    ap.add_argument(
        "--sweep", nargs=3, type=float, default=None, metavar=("START", "STOP", "STEP"),
        help="UDP only: repeat the test at each per-stream bandwidth from "
             "START to STOP Mbps in steps of STEP, reporting aggregate "
             "throughput/loss at each and flagging where loss first exceeds "
             "--loss-threshold, e.g. --sweep 25 200 25",
    )
    ap.add_argument(
        "--loss-threshold", type=float, default=1.0,
        help="percent lost packets considered the saturation point for "
             "--sweep (default: 1.0)",
    )
    args = ap.parse_args()

    if args.sweep and not args.udp:
        print("error: --sweep requires --udp", file=sys.stderr)
        return 2
    proto = "udp" if args.udp else "tcp"

    if not is_prime(args.q):
        print(f"error: q={args.q} is not prime", file=sys.stderr)
        return 2

    pairs = load_pairs(args)
    if not pairs:
        print("error: at least one --pair SRC DST (or --pairs-file) is required", file=sys.stderr)
        return 2

    points = projective_points(args.q)
    edges, absolute = polarity_edges(points, args.q)
    verify(points, edges, absolute, args.q)
    wiring = build_wiring(points, edges, absolute, args.q, variant="sonic-vs")
    switches = wiring["switches"]
    adj = build_adjacency(wiring["n"], edges)
    name_to_idx = {sw["name"]: sw["idx"] for sw in switches}

    try:
        pairs_ctx = [build_pair_ctx(switches, adj, name_to_idx, s, d, args.uA) for s, d in pairs]
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.sweep:
        start, stop, step = args.sweep
        print(f"=== sweep: {len(pairs_ctx)} pair(s), {args.streams} streams/pair, "
              f"{args.duration}s/step, bandwidth {start:g}..{stop:g}M step {step:g}M per stream ===")
        print(f"{'bw/stream':>12}{'aggregate Gbps':>16}{'lost %':>10}{'pairs ok':>10}")
        bw = start
        threshold_hit = None
        degraded_steps = 0
        while bw <= stop + 1e-9:
            bandwidth = f"{bw:g}M"
            results = run_once(pairs_ctx, args.streams, args.duration, True, bandwidth, args.length)
            ok = [(c, d) for c, d in results if d is not None]
            total_bytes = total_packets = total_lost = 0
            for c, data in ok:
                s = aggregate_stats(data, True)
                total_bytes += s["bytes"]
                total_packets += s["packets"]
                total_lost += s["lost"]
            gbps = 8 * total_bytes / args.duration / 1e9
            lost_pct = 100 * total_lost / total_packets if total_packets else 0.0
            degraded = len(ok) < len(pairs_ctx)
            flag = "  !" if degraded else ""
            print(f"{bandwidth:>12}{gbps:>16.2f}{lost_pct:>9.1f}%{len(ok):>7d}/{len(pairs_ctx)}{flag}")
            if degraded:
                # a client failed for a resource reason unrelated to this
                # step's bandwidth (seen: "unable to read from stream
                # socket" under heavy concurrent docker exec load on the
                # orchestrating host itself) -- don't let a partial sample
                # trigger a false threshold.
                degraded_steps += 1
            elif threshold_hit is None and lost_pct > args.loss_threshold:
                threshold_hit = bandwidth
            bw += step
        if degraded_steps:
            print(f"\n({degraded_steps} step(s) marked '!' had at least one pair's iperf3 client fail "
                  f"-- excluded from threshold detection since their numbers are a partial sample, "
                  f"not necessarily a real loss/capacity signal)")
        if threshold_hit is not None:
            print(f"loss exceeded {args.loss_threshold}% starting at {threshold_hit}/stream "
                  f"({len(pairs_ctx)} pair(s) concurrently)")
        else:
            print(f"loss stayed under {args.loss_threshold}% across all non-degraded steps")
        return 0

    print(f"=== testing {len(pairs_ctx)} pair(s) concurrently, {args.streams} streams/pair, "
          f"{args.duration}s ===")
    results = run_once(pairs_ctx, args.streams, args.duration, args.udp, args.bandwidth, args.length)
    for ctx, data in results:
        if data is None:
            continue
        attr = attribute(ctx, data, proto, args.udp)
        print_pair_report(ctx, attr, args.udp)

    if len(results) > 1:
        print_grand_summary(results, args.duration, args.udp)
    elif results and results[0][1] is not None:
        print_grand_summary(results, args.duration, args.udp)

    return 0


if __name__ == "__main__":
    sys.exit(main())
