#!/usr/bin/env python3
"""
WMP-PolarFly path calculator.

For every switch pair in a q-PolarFly fabric, computes:
  - whether the pair is directly adjacent (fabric-connected)
  - the unique 2-hop shortest path (SP) relay, for non-adjacent pairs
  - the set of 3-hop next-shortest-paths (NSP), each via a first-hop
    neighbor other than the SP relay
  - the per-path SRv6 uSID segment list (reusing this repo's existing
    global uA-block addressing scheme)
  - W-CMP weights (fixed 40% SP / evenly split remainder across NSPs,
    per docs/wmp-polarfly-whitepaper-v06.md Section 3.3's stated
    starting point for small q)

Path derivation here uses direct graph traversal over the adjacency list
(computed once from PG(2,q) coordinates via polarity_edges), rather than
re-solving the GF(q) linear system per pair. This computes the identical
path set the whitepaper calls "algebraically derivable" -- the "no path
computation protocol" claim in the paper is about the *switches* not
running a distributed routing protocol at forwarding time, not about how
this offline calculator is implemented. The whitepaper's own worked
example (Section 3.2) is used below as a correctness cross-check against
this graph-traversal approach.

Usage:
  python3 traffic-gen/path_calculator.py --q 7
  python3 traffic-gen/path_calculator.py --q 7 --pair sw001 sw019
  python3 traffic-gen/path_calculator.py --q 7 --out paths-q7.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Set, Tuple

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


# -----------------------------------------------------------------------------
# Graph helpers
# -----------------------------------------------------------------------------

def build_adjacency(n: int, edges: List[Tuple[int, int]]) -> List[Set[int]]:
    adj: List[Set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def common_neighbor(adj: List[Set[int]], a: int, b: int) -> int:
    """Unique common neighbor of a and b. PolarFly's C4-free + diameter-2
    structure guarantees exactly one for any non-adjacent pair."""
    common = adj[a] & adj[b]
    assert len(common) == 1, (
        f"expected exactly one common neighbor of {a},{b}, got {common}"
    )
    return next(iter(common))


def compute_pair_paths(
    n: int, adj: List[Set[int]]
) -> Dict[Tuple[int, int], Dict]:
    """For every unordered pair (u, v) with u < v:
      - adjacent pairs: {"adjacent": True, "sp": None, "nsps": []}
      - non-adjacent pairs: {"adjacent": False, "sp": [relay],
        "nsps": [[a, b], ...]} where each NSP is u -a-> a -b-> b -> v.
    """
    result: Dict[Tuple[int, int], Dict] = {}
    for u in range(n):
        for v in range(u + 1, n):
            if v in adj[u]:
                result[(u, v)] = dict(adjacent=True, sp=None, nsps=[])
                continue
            w = common_neighbor(adj, u, v)
            nsps: List[List[int]] = []
            for a in sorted(adj[u]):
                if a == w:
                    continue
                b = common_neighbor(adj, a, v)
                if b == w:
                    # This candidate's last hop (b -> v) is the same edge the
                    # SP path uses (relay -> v) -- not edge-disjoint from SP,
                    # so it doesn't count as a distinct NSP. This is why
                    # non-absolute vertices (degree q+1) yield q-1 true NSPs,
                    # not q: exactly one of the q non-relay first-hops routes
                    # back through the relay as its second hop.
                    continue
                nsps.append([a, b])
            result[(u, v)] = dict(adjacent=False, sp=[w], nsps=nsps)
    return result


# -----------------------------------------------------------------------------
# SRv6 segment-list synthesis
# -----------------------------------------------------------------------------

def uA_sid(sw: Dict, peer_idx: int) -> str:
    """The uA SID on switch `sw` for its fabric port facing `peer_idx`.
    Reuses the global uA block already established by
    topogen2/polarfly_clab.py's build_frr_conf: fc00:0:f<local_idx>::/48,
    locally scoped/interface-bound (End.X-style adjacency, not routed)."""
    for fp in sw["fabric"]:
        if fp["peer_sw"] == peer_idx:
            return f"fc00:0:f{fp['local_idx']:03x}::"
    raise ValueError(f"{sw['name']} has no fabric port toward peer index {peer_idx}")


def segment_list(switches: List[Dict], u: int, mids: List[int], v: int) -> List[str]:
    """uSID chain for path u -> mids... -> v, terminating in v's uDT6 SID
    (destination decap into the tenant VRF)."""
    hops = [u] + mids + [v]
    segs: List[str] = []
    for i in range(len(hops) - 1):
        segs.append(uA_sid(switches[hops[i]], hops[i + 1]))
    segs.append(switches[v]["udt6_sid"].split("/")[0])
    return segs


# -----------------------------------------------------------------------------
# W-CMP weights
# -----------------------------------------------------------------------------

def wmp_weights(num_nsp: int, w_sp: float = 0.4) -> Dict[str, float]:
    """Fixed 40% SP / evenly split remainder across NSPs -- the whitepaper's
    stated starting point for small q (Section 3.3). `w_sp` is a parameter,
    not hardcoded, so swapping in the full derived-as-f(q) formula later
    doesn't require touching call sites."""
    if num_nsp == 0:
        return dict(sp=1.0)
    return dict(sp=w_sp, **{f"nsp{i}": (1.0 - w_sp) / num_nsp for i in range(num_nsp)})


# -----------------------------------------------------------------------------
# Correctness self-test: whitepaper's own worked example (Section 3.2)
# -----------------------------------------------------------------------------

def whitepaper_worked_example(points: List[Tuple[int, int, int]], adj: List[Set[int]]) -> None:
    """A=(1,0,2), C=(1,4,6): whitepaper solves b0+2b2=0, b0+4b1+6b2=0 (mod 7)
    for relay B, giving B ~ (5,6,1) ~ canonical (1,4,3). Verify our
    graph-based common_neighbor() agrees, independent of the linear-algebra
    derivation."""
    a_idx = points.index((1, 0, 2))
    c_idx = points.index((1, 4, 6))
    expected_b_idx = points.index((1, 4, 3))
    assert c_idx not in adj[a_idx], "A and C were expected to be non-adjacent"
    got = common_neighbor(adj, a_idx, c_idx)
    assert got == expected_b_idx, (
        f"whitepaper worked example failed: expected relay index "
        f"{expected_b_idx} {points[expected_b_idx]}, got {got} {points[got]}"
    )
    print(f"[self-test] whitepaper worked example OK: "
          f"A={points[a_idx]} C={points[c_idx]} -> relay B={points[got]}")


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--q", type=int, default=7, help="prime order (default: 7)")
    ap.add_argument(
        "--pair", nargs=2, metavar=("SW_A", "SW_B"),
        help="print full detail (paths, segment lists, weights) for one pair, "
             "e.g. --pair sw001 sw019",
    )
    ap.add_argument(
        "--out", default=None,
        help="write all-pairs path/segment/weight data as JSON to this path",
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
    n = wiring["n"]

    adj = build_adjacency(n, edges)
    whitepaper_worked_example(points, adj)

    pair_paths = compute_pair_paths(n, adj)

    # Sanity: after excluding both (a) the relay as first hop and (b) any
    # candidate whose second hop lands back on the relay (not edge-disjoint
    # from SP -- see compute_pair_paths), empirically the NSP count is q-1
    # for almost all pairs, and q for a minority of non-absolute<->
    # non-absolute pairs where none of the q candidates (u non-absolute has
    # degree q+1, minus 1 for the relay-as-first-hop exclusion) happen to
    # collide with the relay as a second hop. Pairs with at least one
    # absolute (degree-q) endpoint always land on exactly q-1. This matches
    # whitepaper Section 3.2's "on the order of q edge-disjoint 3-hop
    # paths... exact counts varying" -- an approximate count by the paper's
    # own framing, not a fixed formula.
    abs_set = set(absolute)
    for (u, v), data in pair_paths.items():
        if data["adjacent"]:
            continue
        both_nonabs = u not in abs_set and v not in abs_set
        expected = {args.q - 1, args.q} if both_nonabs else {args.q - 1}
        assert len(data["nsps"]) in expected, (
            f"pair ({switches[u]['name']},{switches[v]['name']}): "
            f"expected {expected} NSPs, got {len(data['nsps'])}"
        )
    n_nonadj = sum(1 for d in pair_paths.values() if not d["adjacent"])
    print(f"[self-test] NSP count sanity OK across {n_nonadj} non-adjacent pairs")

    def name_of(i: int) -> str:
        return switches[i]["name"]

    def enrich(u: int, v: int, data: Dict) -> Dict:
        out = dict(
            u=name_of(u), v=name_of(v), adjacent=data["adjacent"],
        )
        if data["adjacent"]:
            out["sp_segments"] = [switches[v]["udt6_sid"].split("/")[0]]
            out["weights"] = {"sp": 1.0}
            return out
        w = data["sp"][0]
        nsps = data["nsps"]
        out["sp"] = dict(relay=name_of(w), segments=segment_list(switches, u, [w], v))
        out["nsps"] = [
            dict(mids=[name_of(a), name_of(b)], segments=segment_list(switches, u, [a, b], v))
            for a, b in nsps
        ]
        out["weights"] = wmp_weights(len(nsps))
        return out

    if args.pair:
        name_to_idx = {sw["name"]: sw["idx"] for sw in switches}
        a_name, b_name = args.pair
        if a_name not in name_to_idx or b_name not in name_to_idx:
            print(f"error: unknown switch name(s) in --pair {args.pair}", file=sys.stderr)
            return 2
        u, v = sorted((name_to_idx[a_name], name_to_idx[b_name]))
        data = pair_paths[(u, v)]
        print(json.dumps(enrich(u, v, data), indent=2))

    if args.out:
        all_data = [enrich(u, v, data) for (u, v), data in sorted(pair_paths.items())]
        with open(args.out, "w") as fh:
            json.dump(all_data, fh, indent=2)
        print(f"wrote {len(all_data)} pairs to {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
