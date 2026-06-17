#!/usr/bin/env python3
"""
Polarfly -> SDN-controller fabric JSON exporter.

Reuses the wiring produced by polarfly_clab.py and emits a JSON document
that follows the same data model as clos-fabric.json (nodes / interfaces /
endpoints / edges with igp_adjacency + attachment edge types).

Output for q=7 (default): 57 switches, 57 hosts, 224 fabric edges (448 directed),
                          57 attachments, 224*2 + 57 = 505 directed edges total.

Usage:
  python3 polarfly_fabric_json.py                        # q=7 -> ../q7/q7-fabric.json
  python3 polarfly_fabric_json.py --q 13                 # -> ../q13/q13-fabric.json
  python3 polarfly_fabric_json.py --q 7 --out path.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from polarfly_clab import (
    build_wiring,
    is_prime,
    polarity_edges,
    projective_points,
    verify,
)


SRV6_BLOCK_LEN = 32
SRV6_NODE_LEN = 16
SRV6_FUNC_LEN = 16


def srv6_struct(func_len: int = 0) -> dict:
    return {
        "locator_block_len": SRV6_BLOCK_LEN,
        "locator_node_len": SRV6_NODE_LEN,
        "function_len": func_len,
        "argument_len": 0,
    }


def node_sid(loc_id: str) -> str:
    """Node SID = locator prefix base address (uN). e.g. fc00:0:1001::"""
    return f"fc00:0:{loc_id}::"


def ua_sid(loc_id: str, local_idx: int) -> str:
    """uA (End.X) SID per fabric port: fc00:0:<loc>:f<idx>::, function 16-bit."""
    return f"fc00:0:{loc_id}:f{local_idx:03x}::"


def build_fabric_json(q: int) -> dict:
    if not is_prime(q):
        raise SystemExit(f"q={q} is not prime")

    points = projective_points(q)
    edges, absolute = polarity_edges(points, q)
    verify(points, edges, absolute, q)
    w = build_wiring(points, edges, absolute, q)

    switches = w["switches"]
    n = w["n"]

    # ---- vertex classification (for visualizer/SYD layout) ----
    # W  (vType=0): absolute / quadric points (a^2+b^2+c^2 == 0 mod q).
    # V1 (vType=1): off-quadric vertices adjacent to >=1 quadric (petal hubs).
    # V2 (vType=2): off-quadric vertices with no quadric neighbor (pure fins).
    # Cluster: each V1 anchors a cluster named by its switch (e.g. "sw014").
    #          Each V2 is assigned to the lowest-indexed V1 neighbor (stable
    #          across regenerations). W vertices have no cluster ("").
    abs_set = set(absolute)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    v_type = [0] * n  # 0=W, 1=V1, 2=V2
    for i in range(n):
        if i in abs_set:
            v_type[i] = 0
        elif any(j in abs_set for j in adj[i]):
            v_type[i] = 1
        else:
            v_type[i] = 2

    cluster = [""] * n
    for i in range(n):
        if v_type[i] == 1:
            cluster[i] = switches[i]["name"]
    for i in range(n):
        if v_type[i] == 2:
            v1_neighbors = sorted(j for j in adj[i] if v_type[j] == 1)
            if v1_neighbors:
                cluster[i] = switches[v1_neighbors[0]]["name"]

    nodes = []
    interfaces = []
    endpoints = []
    edge_records = []

    # ---- nodes (switches) ----
    for s in switches:
        i = s["idx"]
        nodes.append({
            "id": s["name"],
            "name": s["name"],
            "subtype": "switch",
            "labels": {
                "tier": "fabric",
                "topology": f"polarfly-q{q}",
                "absolute": "true" if s["is_absolute"] else "false",
                "asn": str(s["asn"]),
                "vType": str(v_type[i]),
                "cluster": cluster[i],
            },
            "srv6_node_sid": {
                "sid": node_sid(s["loc_id"]),
                "behavior": "End",
                "structure": srv6_struct(func_len=0),
            },
        })

    # ---- endpoints (hosts) ----
    for s in switches:
        endpoints.append({
            "id": s["host_name"],
            "name": s["host_name"],
            "subtype": "host",
            "labels": {
                "tier": "host",
                "switch": s["name"],
            },
        })

    # ---- interfaces + igp_adjacency edges ----
    # For every fabric port on every switch, emit one interface record and
    # one directed igp_adjacency edge. Each undirected fabric link in the
    # graph thus produces two interfaces and two directed edges (mirroring
    # clos-fabric.json).
    for s in switches:
        for fp in s["fabric"]:
            peer = switches[fp["peer_sw"]]
            iface_id = f"iface:{s['name']}/{peer['name']}"
            edge_id = f"link:{s['name']}:{peer['name']}"

            interfaces.append({
                "id": iface_id,
                "owner_node_id": s["name"],
                "name": f"{s['name']}-{fp['port']}",
                "srv6_ua_sids": [{
                    "sid": ua_sid(s["loc_id"], fp["local_idx"]),
                    "behavior": "End.X",
                    "structure": srv6_struct(func_len=SRV6_FUNC_LEN),
                }],
            })

            edge_records.append({
                "id": edge_id,
                "type": "igp_adjacency",
                "src_id": s["name"],
                "dst_id": peer["name"],
                "directed": True,
                "local_iface_id": iface_id,
                "igp_metric": 1,
                "max_bw_bps": 400_000_000_000,
                "unidir_delay_us": 1,
            })

    # ---- attachment edges (host -> switch) ----
    for s in switches:
        edge_records.append({
            "id": f"attach:{s['host_name']}:{s['name']}",
            "type": "attachment",
            "src_id": s["host_name"],
            "dst_id": s["name"],
            "directed": True,
        })

    fabric_edges_directed = sum(len(s["fabric"]) for s in switches)
    n_undirected = fabric_edges_directed // 2
    description = (
        f"Polarfly PG(2,{q}) fabric: {n} switches, "
        f"{n_undirected} fabric links, {n} hosts (one per switch). "
        f"{len(absolute)} absolute points."
    )

    return {
        "topology_id": f"polarfly-q{q}",
        "description": description,
        "nodes": nodes,
        "interfaces": interfaces,
        "endpoints": endpoints,
        "edges": edge_records,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", type=int, default=7)
    ap.add_argument("--out", default=None,
                    help="output path (default: ../q<q>/q<q>-fabric.json)")
    args = ap.parse_args()

    doc = build_fabric_json(args.q)

    if args.out:
        out = args.out
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        out = os.path.join(here, "..", f"q{args.q}", f"q{args.q}-fabric.json")
        out = os.path.normpath(out)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")

    print(
        f"wrote {out}: "
        f"{len(doc['nodes'])} nodes, "
        f"{len(doc['interfaces'])} interfaces, "
        f"{len(doc['endpoints'])} endpoints, "
        f"{len(doc['edges'])} edges"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
