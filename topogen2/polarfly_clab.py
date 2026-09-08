#!/usr/bin/env python3
"""
Polarfly containerlab topology generator.

Builds the Erdős–Rényi polarity graph of the projective plane PG(2, q)
for prime q, and emits a containerlab YAML wiring `docker-sonic-vs:latest`
switches according to that graph, with one `bmcdougall/alpine-srv6-scapy:1.0`
host attached to each switch (iperf3/scapy/encap.red-capable iproute2 --
a superset of the plain iejalapeno/alpine-srv6:1.0 base it's built from).

For q = 13 (default):
  - Nodes (switches):     q^2 + q + 1                  = 183
  - Fabric radix:         q + 1                        = 14
  - Absolute points:      q + 1                        = 14
  - Fabric links:         (n*(q+1) - absolute_count)/2 = 1274
  - Host links (1/sw):                                 = 183
  - Total containers:                                  = 366
  - Total links:                                       = 1457

Polarity (self-duality): point P=(a,b,c) is adjacent to Q=(d,e,f) iff
  a*d + b*e + c*f ≡ 0 (mod q).
A point is "absolute" iff a^2 + b^2 + c^2 ≡ 0 (mod q); these contribute
a self-loop in the abstract graph, which we drop physically (one less
fabric port used on those switches).

Usage:
  python3 polarfly_clab.py            # q=13, writes ../sonic-polarfly.clab.yaml
  python3 polarfly_clab.py --q 5      # smaller test fabric
  python3 polarfly_clab.py --q 13 --out /path/to/topo.yaml

Stdlib only (no galois/sympy needed for small primes).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import product
from typing import Dict, List, Tuple


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def projective_points(q: int) -> List[Tuple[int, int, int]]:
    """Canonical representatives of points in PG(2, q): leading nonzero coord = 1."""
    pts: List[Tuple[int, int, int]] = []
    for a, b, c in product(range(q), repeat=3):
        if (a, b, c) == (0, 0, 0):
            continue
        # Normalize: scale so first nonzero coordinate is 1.
        if a != 0:
            inv = pow(a, -1, q)
            rep = (1, (b * inv) % q, (c * inv) % q)
        elif b != 0:
            inv = pow(b, -1, q)
            rep = (0, 1, (c * inv) % q)
        else:
            rep = (0, 0, 1)
        if rep == (a, b, c):
            pts.append(rep)
    expected = q * q + q + 1
    assert len(pts) == expected, f"got {len(pts)} points, expected {expected}"
    return pts


def polarity_edges(points: List[Tuple[int, int, int]], q: int):
    """Return (edges, absolute_indices). Edges are i<j adjacency pairs."""
    edges: List[Tuple[int, int]] = []
    absolute: List[int] = []
    n = len(points)
    for i in range(n):
        a, b, c = points[i]
        if (a * a + b * b + c * c) % q == 0:
            absolute.append(i)
        for j in range(i + 1, n):
            d, e, f = points[j]
            if (a * d + b * e + c * f) % q == 0:
                edges.append((i, j))
    return edges, absolute


def verify(points, edges, absolute, q: int) -> None:
    n = len(points)
    deg = [0] * n
    for i, j in edges:
        deg[i] += 1
        deg[j] += 1
    abs_set = set(absolute)
    for v in range(n):
        expected = q if v in abs_set else q + 1
        assert deg[v] == expected, (
            f"vertex {v} has degree {deg[v]}, expected {expected}"
        )
    expected_edges = (n * (q + 1) - len(absolute)) // 2
    assert len(edges) == expected_edges, (
        f"got {len(edges)} edges, expected {expected_edges}"
    )
    assert len(absolute) == q + 1, (
        f"got {len(absolute)} absolute points, expected {q + 1}"
    )


def mgmt_ip(network_24_third_octet: int, host: int) -> str:
    return f"172.100.{network_24_third_octet}.{host}"


def build_wiring(points, edges, absolute, q: int, variant: str = "sonic-vs") -> Dict:
    """Compute the canonical (switch, port, peer, ip) wiring used by both
    YAML and config emitters. Returns a dict of derived data structures.

    Conventions:
      - Switches numbered 1..n; sw{i+1:0Wd}
      - Per-switch fabric ports allocated in edge-iteration order:
        - variant "sonic-vs": local port index 0,1,2,... -> Ethernet0,
          Ethernet4, Ethernet8, ... (real Force10-S6000 4-lane stride, to
          match docker-sonic-vs's platform.json). Host port is a single
          global constant Ethernet{4*(q+1)}.
        - variant "sonic-vpp": local port index 0,1,2,... -> Ethernet0,
          Ethernet1, Ethernet2, ... (sequential single-lane, to match
          docker-sonic-vpp's own baked-in platform.json AND its
          create_if_mapping()/start_sonic.sh port-trim logic, which numbers
          Ethernet<N> purely by position in the VPP_DPDK_PORTS list with no
          gaps). Host port is therefore PER-SWITCH at Ethernet{radix}, where
          radix is that switch's fabric port count (q for absolute points,
          q+1 otherwise) -- absolute and non-absolute switches disagree on
          which Ethernet index is "host".
        Absolute-point switches use one fewer fabric port (no self-loop).
      - Each fabric link e in [0..|E|-1] uses /127 from 2001:db8:1::/64:
          subnet  = 2001:db8:1:0:E::/127  with E encoded in low bits
          (we use 2 addresses per link, so subnet base = e * 2)
        Endpoints: lower index gets ::0, higher index gets ::1.
    """
    n = len(points)
    abs_set = set(absolute)
    width = max(3, len(str(n)))
    is_vpp = variant == "sonic-vpp"

    def sw_name(i: int) -> str:
        return f"sw{i + 1:0{width}d}"

    def host_name(i: int) -> str:
        return f"h{i + 1:0{width}d}"

    # Global (sonic-vs) host port constant; unused for sonic-vpp, where
    # host_port is computed per-switch below instead.
    host_port = f"Ethernet{4 * (q + 1)}"

    # Per-switch list of fabric ports in allocation order.
    # Each entry: dict(port_name, local_idx, peer_sw_idx, peer_port_name,
    #                  edge_idx, p2p_subnet, my_addr, peer_addr)
    fabric_ports: List[List[Dict]] = [[] for _ in range(n)]
    next_port = [0] * n

    for e_idx, (u, v) in enumerate(edges):
        ulocal = next_port[u]
        vlocal = next_port[v]
        next_port[u] += 1
        next_port[v] += 1
        if is_vpp:
            u_port = f"Ethernet{ulocal}"
            v_port = f"Ethernet{vlocal}"
        else:
            u_port = f"Ethernet{ulocal * 4}"
            v_port = f"Ethernet{vlocal * 4}"

        # /127 P2P from 2001:db8:1::/64 area, indexed by edge number.
        # Use 2001:db8:1:<eg>::/127 where eg = e_idx (so .0 and .1 of that /127).
        # Encode e_idx in 16-bit hex to keep address shape clean.
        subnet_hex = f"{e_idx:x}"
        u_addr = f"2001:db8:1:{subnet_hex}::"
        v_addr = f"2001:db8:1:{subnet_hex}::1"
        prefix = f"2001:db8:1:{subnet_hex}::/127"

        fabric_ports[u].append(
            dict(
                port=u_port,
                local_idx=ulocal,
                peer_sw=v,
                peer_port=v_port,
                edge_idx=e_idx,
                p2p_prefix=prefix,
                my_addr=u_addr,
                peer_addr=v_addr,
            )
        )
        fabric_ports[v].append(
            dict(
                port=v_port,
                local_idx=vlocal,
                peer_sw=u,
                peer_port=u_port,
                edge_idx=e_idx,
                p2p_prefix=prefix,
                my_addr=v_addr,
                peer_addr=u_addr,
            )
        )

    # Per-switch derived addressing
    switches: List[Dict] = []
    for i in range(n):
        sw_idx_1 = i + 1  # 1-based
        radix = len(fabric_ports[i])
        sw_host_port = f"Ethernet{radix}" if is_vpp else host_port
        # Locator: fc00:0:1<NNN>::/48 where NNN is 3 hex digits of switch id.
        # sw001 -> fc00:0:1001::/48, sw057 -> fc00:0:1039::/48 (57 = 0x39).
        loc_id = f"{0x1000 + sw_idx_1:04x}"  # e.g. 1001, 1002, ..., 1039
        locator_prefix = f"fc00:0:{loc_id}::/48"
        loopback_v6 = f"fc00:0:{loc_id}::1"
        loopback_v6_prefix = f"fc00:0:{loc_id}::/48"
        loopback_v4 = f"1.1.{(sw_idx_1 >> 8) & 0xff}.{sw_idx_1 & 0xff}"

        # uDT6 SID for tenant VRF: fc00:<sw>:e000::/48 -- but per the user's
        # constraint ALL function SIDs live under fc00:0::/32. Allocate
        # uDT6 from per-switch locator so they don't collide:
        #   uDT6 = fc00:0:<loc_id>:e000::/64
        # That's a function within the switch's locator block, valid uSID.
        udt6_sid = f"fc00:0:{loc_id}:e000::/64"

        # Tenant VRF + host link addressing
        # Host /64: 2001:db8:a<NNN>::/64 ; switch ::1, host ::2
        host_id = f"a{sw_idx_1:03x}"
        host_subnet = f"2001:db8:{host_id}::/64"
        host_sw_addr = f"2001:db8:{host_id}::1"
        host_host_addr = f"2001:db8:{host_id}::2"

        # ASN: 65000 + sw_idx_1
        asn = 65000 + sw_idx_1

        # MAC: 02:42:ac:14:XX:YY (XX=high,YY=low byte of sw_idx_1*4 to add spread)
        mac_lo = (sw_idx_1 * 4) & 0xff
        mac_hi = (sw_idx_1 * 4 >> 8) & 0xff
        mac = f"02:42:ac:14:{mac_hi:02x}:{mac_lo:02x}"

        switches.append(
            dict(
                idx=i,
                idx1=sw_idx_1,
                name=sw_name(i),
                host_name=host_name(i),
                host_port=sw_host_port,
                radix=radix,
                fabric=fabric_ports[i],
                is_absolute=(i in abs_set),
                loc_id=loc_id,
                locator_prefix=locator_prefix,
                loopback_v6=loopback_v6,
                loopback_v6_prefix=loopback_v6_prefix,
                loopback_v4=loopback_v4,
                udt6_sid=udt6_sid,
                host_subnet=host_subnet,
                host_sw_addr=host_sw_addr,
                host_host_addr=host_host_addr,
                asn=asn,
                mac=mac,
            )
        )

    return dict(
        n=n,
        q=q,
        width=width,
        host_port=host_port,
        variant=variant,
        switches=switches,
        edges=edges,
        absolute=absolute,
    )


def emit_yaml(points, edges, absolute, q: int, out_path: str, wiring: Dict,
              with_binds: bool = False, bind_dir_rel: str = "") -> None:
    n = wiring["n"]
    switches = wiring["switches"]
    variant = wiring.get("variant", "sonic-vs")
    is_vpp = variant == "sonic-vpp"
    # NOTE: "sonic-vpp" is NOT a containerlab-registered kind (unlike
    # "sonic-vs", which containerlab's binary knows natively). containerlab
    # rejects unrecognized kind strings, so the vpp variant uses the generic
    # "linux" kind with an explicit per-node image override instead.
    kind = "linux" if is_vpp else "sonic-vs"
    image = "docker-sonic-vpp:latest" if is_vpp else "docker-sonic-vs:latest"

    lines: List[str] = []
    lines.append(f"# Polarfly q={q} containerlab topology ({kind})")
    lines.append(f"# Generated by topogen2/polarfly_clab.py")
    lines.append(f"# Switches:        {n}")
    lines.append(f"# Fabric links:    {len(edges)}")
    lines.append(f"# Host links:      {n}")
    lines.append(f"# Absolute points: {len(absolute)}  ({sorted(absolute)})")
    if with_binds:
        lines.append(f"# Bind dir (rel): {bind_dir_rel}/<swNNN>/{{config_db.json,frr.conf}}")
    lines.append("")
    lines.append("name: sonic-polarfly")
    lines.append('prefix: ""')
    lines.append("")
    lines.append("mgmt:")
    lines.append("  network: mgmt-net")
    lines.append("  ipv4-subnet: 172.100.0.0/23")
    lines.append("")
    lines.append("topology:")
    lines.append("  kinds:")
    if is_vpp:
        # Switches and hosts both use the generic "linux" kind here (no
        # "sonic-vpp" kind exists in containerlab); each node overrides
        # `image:` individually below instead of relying on a kind default.
        lines.append("    linux: {}")
    else:
        lines.append(f"    {kind}:")
        lines.append(f"      image: {image}")
        lines.append("    linux:")
        lines.append("      image: bmcdougall/alpine-srv6-scapy:1.0")
    lines.append("")
    lines.append("  nodes:")
    for s in switches:
        ip = f"172.100.0.{11 + s['idx']}"
        if is_vpp:
            # radix+1 veth ports total (fabric + host), in Ethernet0..Ethernet{radix}
            # order; VPP_DPDK_PORTS position purely determines the EthernetN
            # numbering (see start_sonic.sh's create_if_mapping()) -- no gaps,
            # no relation to sonic-vs's stride-4 lane convention.
            num_ports = s["radix"] + 1
            dpdk_ports = ",".join(f"eth{i + 1}" for i in range(num_ports))
            lines.append(f"    {s['name']}:")
            lines.append(f"      kind: {kind}")
            lines.append(f"      image: {image}")
            lines.append(f"      mgmt-ipv4: {ip}")
            # docker-sonic-vpp needs the same --privileged its own
            # start_sonic_vpp.sh grants via `docker run --privileged` (network
            # namespace/interface manipulation, syncd, etc.)
            lines.append(f"      privileged: true")
            lines.append(f"      env:")
            lines.append(f'        VPP_DPDK_PORTS: "{dpdk_ports}"')
            lines.append(f'        SONIC_NUM_PORTS: "{num_ports}"')
            lines.append(f'        DPDK_DISABLE: "y"')
            if with_binds:
                lines.append(f"      binds:")
                lines.append(
                    f"        - {bind_dir_rel}/{s['name']}/config_db.json:/etc/sonic/config_db.json"
                )
                lines.append(
                    f"        - {bind_dir_rel}/{s['name']}/frr.conf:/etc/sonic/frr/frr.conf"
                )
        elif with_binds:
            lines.append(f"    {s['name']}:")
            lines.append(f"      kind: {kind}")
            lines.append(f"      mgmt-ipv4: {ip}")
            lines.append(f"      binds:")
            lines.append(
                f"        - {bind_dir_rel}/{s['name']}/config_db.json:/etc/sonic/config_db.json"
            )
            lines.append(
                f"        - {bind_dir_rel}/{s['name']}/frr.conf:/etc/sonic/frr/frr.conf"
            )
        else:
            lines.append(f"    {s['name']}: {{ kind: {kind}, mgmt-ipv4: {ip} }}")
    lines.append("")
    for s in switches:
        ip = f"172.100.1.{11 + s['idx']}"
        lines.append(f"    {s['host_name']}:")
        lines.append(f"      kind: linux")
        lines.append(f"      mgmt-ipv4: {ip}")
        lines.append(f"      exec:")
        lines.append(f'        - "ip -6 addr add {s["host_host_addr"]}/64 dev eth1 nodad"')
        lines.append(f'        - "ip route add fc00::/32 via {s["host_sw_addr"]} dev eth1"')
    lines.append("")
    lines.append("  links:")
    lines.append("    # ---- fabric links (polarity adjacencies) ----")
    if is_vpp:
        lines.append("    # NOTE: link endpoints use eth<N> containerlab naming. Inside the")
        lines.append("    # container, start_sonic.sh's create_if_mapping() numbers EthernetN")
        lines.append("    # purely by VPP_DPDK_PORTS list position (no gaps): eth1->Ethernet0,")
        lines.append("    # eth2->Ethernet1, ..., with the host port last (Ethernet{radix}).")
    else:
        lines.append("    # NOTE: link endpoints use eth<N> containerlab naming, where N = SONiC")
        lines.append("    # 'index' field + 1 (eth1=Ethernet0, eth2=Ethernet4, ..., eth(q+2)=host port).")
        lines.append("    # SONiC's syncd virtual-SAI creates the Ethernet<N> hostif itself and binds")
        lines.append("    # it to the corresponding ethN veth via port_config.ini's index field.")
        lines.append("    # Attaching as Ethernet<N> directly causes SAI_HOSTIF create failures.")
    # Emit edges in original order; pull port from wiring (lower index endpoint
    # is the "u" side of each edge by construction).
    for e_idx, (u, v) in enumerate(edges):
        u_fp = next(p for p in switches[u]["fabric"] if p["edge_idx"] == e_idx)
        v_fp = next(p for p in switches[v]["fabric"] if p["edge_idx"] == e_idx)
        # local_idx 0 -> eth1, 1 -> eth2, ...
        u_eth = f"eth{u_fp['local_idx'] + 1}"
        v_eth = f"eth{v_fp['local_idx'] + 1}"
        lines.append(
            f'    - endpoints: ["{switches[u]["name"]}:{u_eth}", '
            f'"{switches[v]["name"]}:{v_eth}"]'
        )
    lines.append("    # ---- host links (one alpine-srv6 per switch) ----")
    for s in switches:
        # sonic-vs: host port is a fixed global constant Ethernet{4*(q+1)} -> eth{q+2}.
        # sonic-vpp: host port is per-switch Ethernet{radix}, always the last
        # entry in VPP_DPDK_PORTS -> eth{radix+1}.
        host_eth = f"eth{s['radix'] + 1}" if is_vpp else f"eth{q + 2}"
        lines.append(
            f'    - endpoints: ["{s["name"]}:{host_eth}", "{s["host_name"]}:eth1"]'
        )
    lines.append("")

    with open(out_path, "w") as fh:
        fh.write("\n".join(lines))


def emit_adjlist(points, edges, q: int, out_path: str) -> None:
    n = len(points)
    width = max(3, len(str(n)))
    with open(out_path, "w") as fh:
        fh.write(f"# Polarfly q={q} adjacency (sidecar)\n")
        fh.write(f"# {n} vertices, {len(edges)} edges\n")
        fh.write("# index  point(a:b:c)\n")
        for i, p in enumerate(points):
            fh.write(f"V {i + 1:0{width}d}  {p[0]}:{p[1]}:{p[2]}\n")
        fh.write("# i  j  (1-indexed switch IDs)\n")
        for u, v in edges:
            fh.write(f"E {u + 1:0{width}d} {v + 1:0{width}d}\n")


# -----------------------------------------------------------------------------
# Per-switch SONiC config_db.json + FRR frr.conf emission
# -----------------------------------------------------------------------------

# Force10-S6000 lane map (32 ports x 4 lanes), copied from srv6-oci reference.
# Index in this list == port index 0..31; entry = (lanes_csv, alias_suffix).
S6000_LANES: List[Tuple[str, str]] = [
    ("25,26,27,28", "0/0"),
    ("29,30,31,32", "0/4"),
    ("33,34,35,36", "0/8"),
    ("37,38,39,40", "0/12"),
    ("45,46,47,48", "0/16"),
    ("41,42,43,44", "0/20"),
    ("1,2,3,4", "0/24"),
    ("5,6,7,8", "0/28"),
    ("13,14,15,16", "0/32"),
    ("9,10,11,12", "0/36"),
    ("17,18,19,20", "0/40"),
    ("21,22,23,24", "0/44"),
    ("53,54,55,56", "0/48"),
    ("49,50,51,52", "0/52"),
    ("57,58,59,60", "0/56"),
    ("61,62,63,64", "0/60"),
    ("69,70,71,72", "0/64"),
    ("65,66,67,68", "0/68"),
    ("73,74,75,76", "0/72"),
    ("77,78,79,80", "0/76"),
    ("109,110,111,112", "0/80"),
    ("105,106,107,108", "0/84"),
    ("113,114,115,116", "0/88"),
    ("117,118,119,120", "0/92"),
    ("125,126,127,128", "0/96"),
    ("121,122,123,124", "0/100"),
    ("81,82,83,84", "0/104"),
    ("85,86,87,88", "0/108"),
    ("93,94,95,96", "0/112"),
    ("89,90,91,92", "0/116"),
    ("101,102,103,104", "0/120"),
    ("97,98,99,100", "0/124"),
]


def _port_table(used_ports: List[str]) -> Dict[str, Dict[str, str]]:
    """Build a PORT table for the given list of Ethernet<N> port names.
    Maps each Ethernet<N*4> to lane group N from the S6000 layout."""
    out: Dict[str, Dict[str, str]] = {}
    for p in used_ports:
        # p is "EthernetX" with X = 4 * port_index
        idx = int(p[len("Ethernet"):]) // 4
        lanes, alias_suffix = S6000_LANES[idx]
        out[p] = {
            "lanes": lanes,
            "alias": f"fortyGigE{alias_suffix}",
            "index": str(idx),
            "speed": "40000",
            "admin_status": "up",
            "mtu": "9100",
        }
    return out


# docker-sonic-vpp's own baked-in platform.json for HWSKU=Force10-S6000
# (PLATFORM=x86_64-kvm_x86_64-r0) -- confirmed by reading that file directly.
# Unlike the *real* Force10-S6000 hwsku (S6000_LANES above, stride-4), this
# is sequential: Ethernet<N> is simply the Nth front-panel port, one per
# index, lanes taken straight from the image's platform.json.
VPP_LANES: List[str] = [
    "25,26,27,28",
    "29,30,31,32",
    "33,34,35,36",
    "37,38,39,40",
    "45,46,47,48",
    "41,42,43,44",
    "1,2,3,4",
    "5,6,7,8",
    "13,14,15,16",
    "9,10,11,12",
]


def _port_table_vpp(used_ports: List[str]) -> Dict[str, Dict[str, str]]:
    """Build a PORT table for docker-sonic-vpp's sequential Ethernet<N>
    naming, sourced from its own platform.json lane assignments."""
    out: Dict[str, Dict[str, str]] = {}
    for p in used_ports:
        idx = int(p[len("Ethernet"):])
        out[p] = {
            "lanes": VPP_LANES[idx],
            "alias": f"fortyGigE0/{idx}",
            "index": str(idx),
            "speed": "40000",
            "admin_status": "up",
            "mtu": "9100",
        }
    return out


def build_config_db(s: Dict, variant: str = "sonic-vs") -> Dict:
    """Build the config_db.json dict for switch s."""
    fabric = s["fabric"]
    host_port = s["host_port"]

    # All ports we want SONiC to instantiate: every fabric port + the host port.
    used_ports = [p["port"] for p in fabric] + [host_port]
    port_table = _port_table_vpp(used_ports) if variant == "sonic-vpp" else _port_table(used_ports)

    # INTERFACE table: P2P /127 on each fabric port; /64 on host port (in VRF).
    interfaces: Dict[str, Dict] = {}
    for fp in fabric:
        interfaces[fp["port"]] = {}
        interfaces[f"{fp['port']}|{fp['my_addr']}/127"] = {}
    interfaces[host_port] = {"vrf_name": "Vrf-tenant"}
    interfaces[f"{host_port}|{s['host_sw_addr']}/64"] = {}

    cfg = {
        "DEVICE_METADATA": {
            "localhost": {
                "mac": s["mac"],
                "switch_type": "switch",
                "buffer_model": "traditional",
                "hwsku": "Force10-S6000",
                "hostname": s["name"],
                "bgp_asn": str(s["asn"]),
                "docker_routing_config_mode": "split",
            }
        },
        "VRF": {
            "Vrf-tenant": {},
        },
        "LOOPBACK_INTERFACE": {
            "Loopback0": {},
            f"Loopback0|{s['loopback_v4']}/32": {},
            f"Loopback0|{s['loopback_v6']}/128": {},
        },
        "INTERFACE": interfaces,
        "PORT": port_table,
    }
    return cfg


def build_frr_conf(s: Dict, switches: List[Dict]) -> str:
    """Build the frr.conf text for switch s."""
    fabric = s["fabric"]
    lines: List[str] = []
    p = lines.append

    p(f"hostname {s['name']}")
    p("no service integrated-vtysh-config")
    p("!")
    p("route-map BGP-IPV6 permit 20")
    p(" set ipv6 next-hop prefer-global")
    p("exit")
    p("!")
    p("route-map RM_SET_SRC permit 10")
    p(f" set src {s['loopback_v4']}")
    p("exit")
    p("!")
    p("route-map RM_SET_SRC6 permit 10")
    p(f" set src {s['loopback_v6']}")
    p("exit")
    p("!")
    p("password zebra")
    p("enable password zebra")
    p("!")
    p("vrf Vrf-tenant")
    p(" ip nht resolve-via-default")
    p(" ipv6 nht resolve-via-default")
    p("exit-vrf")
    p("!")
    p("vrf vrfdefault")
    p(" ip nht resolve-via-default")
    p(" ipv6 nht resolve-via-default")
    p("exit-vrf")
    p("!")
    p(f"router bgp {s['asn']}")
    p(f" bgp router-id {s['loopback_v4']}")
    p(" bgp log-neighbor-changes")
    p(" no bgp ebgp-requires-policy")
    p(" no bgp default ipv4-unicast")
    p(" bgp bestpath as-path multipath-relax")
    p(" no bgp network import-check")
    # eBGP neighbors over each fabric P2P link
    for fp in fabric:
        peer = switches[fp["peer_sw"]]
        p(f" neighbor {fp['peer_addr']} remote-as {peer['asn']}")
        p(f" neighbor {fp['peer_addr']} capability extended-nexthop")
    p(" !")
    p(" address-family ipv6 unicast")
    p(f"  network {s['locator_prefix']}")
    p(f"  network {s['loopback_v6']}/128")
    for fp in fabric:
        p(f"  neighbor {fp['peer_addr']} activate")
        p(f"  neighbor {fp['peer_addr']} route-map BGP-IPV6 in")
    p("  maximum-paths 64")
    p(" exit-address-family")
    p("exit")
    p("!")
    p("ip protocol bgp route-map RM_SET_SRC")
    p("!")
    p("ipv6 protocol bgp route-map RM_SET_SRC6")
    p("!")
    p("ip nht resolve-via-default")
    p("!")
    p("ipv6 nht resolve-via-default")
    p("!")
    # Segment Routing block
    p("segment-routing")
    p(" srv6")
    p("  static-sids")
    # uN
    p(f"   sid {s['locator_prefix']} locator MAIN behavior uN")
    # uDT6 -> Vrf-tenant
    p(f"   sid {s['udt6_sid']} locator MAIN behavior uDT6 vrf Vrf-tenant")
    # Global uDT6 SID (same on every switch, locally scoped)
    p("   sid fc00:0:e000::/48 locator MAIN behavior uDT6 vrf Vrf-tenant")
    # uA per fabric port (Ethernet0->fc00:0:f000::/48, +4 -> f001, ...)
    for fp in fabric:
        # local_idx 0 -> f000, 1 -> f001, ...
        ua_sid = f"fc00:0:f{fp['local_idx']:03x}::/48"
        p(
            f"   sid {ua_sid} locator MAIN behavior uA "
            f"interface {fp['port']} nexthop {fp['peer_addr']}"
        )
    p("  exit")
    p("  !")
    p(" exit")
    p(" !")
    p(" srv6")
    p("  encapsulation")
    p(f"   source-address {s['loopback_v6']}")
    p("  exit")
    p("  locators")
    p("   locator MAIN")
    p(f"    prefix {s['locator_prefix']} block-len 32 node-len 16")
    p("    behavior usid")
    p("    format usid-f3216")
    p("   exit")
    p("   !")
    p("  exit")
    p("  !")
    p("  formats")
    p("   format usid-f3216")
    p("    local-id-block explicit start 57344 end 65535")
    p("   exit")
    p("   !")
    p("  exit")
    p("  !")
    p(" exit")
    p(" !")
    p("exit")
    p("!")
    p("end")
    p("")  # trailing newline
    return "\n".join(lines)


def emit_configs(wiring: Dict, out_dir: str) -> int:
    """Write per-switch config_db.json and frr.conf into out_dir/<sw_name>/.
    Returns number of switches written."""
    switches = wiring["switches"]
    variant = wiring.get("variant", "sonic-vs")
    os.makedirs(out_dir, exist_ok=True)
    for s in switches:
        sw_dir = os.path.join(out_dir, s["name"])
        os.makedirs(sw_dir, exist_ok=True)
        cfg = build_config_db(s, variant=variant)
        with open(os.path.join(sw_dir, "config_db.json"), "w") as fh:
            json.dump(cfg, fh, indent=4)
            fh.write("\n")
        frr = build_frr_conf(s, switches)
        with open(os.path.join(sw_dir, "frr.conf"), "w") as fh:
            fh.write(frr)
    return len(switches)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--q", type=int, default=13, help="prime order (default: 13)")
    ap.add_argument(
        "--variant",
        choices=["sonic-vs", "sonic-vpp"],
        default="sonic-vs",
        help="switch dataplane: sonic-vs (default, AF_PACKET-vs-Linux-kernel "
             "reference) or sonic-vpp (VPP/AF_PACKET dataplane)",
    )
    here = os.path.dirname(os.path.abspath(__file__))
    # Layout: polarfly/q<q>/<variant-subdir>/{yaml, adj, sonic-config/<sw>/...}
    # Every variant gets its own sibling subdirectory under q<q>/ (sonic/,
    # sonic-vpp/, and the separately-maintained xrd/) so multiple dataplane
    # variants can coexist for the same q. Determined from raw sys.argv
    # (not the parsed --variant below) since these defaults are computed
    # before argparse runs.
    VARIANT_SUBDIR = {"sonic-vs": "sonic", "sonic-vpp": "sonic-vpp"}
    _variant_argv = "sonic-vpp" if (
        "--variant" in sys.argv and "sonic-vpp" in sys.argv
    ) else "sonic-vs"
    default_topo_dir = os.path.normpath(
        os.path.join(here, "..", "q{q}", VARIANT_SUBDIR[_variant_argv])
    )
    default_out = os.path.join(default_topo_dir, "sonic-polarfly-q{q}-nobinds.clab.yaml")
    default_out_binds = os.path.join(
        default_topo_dir, "sonic-polarfly-q{q}.clab.yaml"
    )
    default_adj = os.path.join(default_topo_dir, "polarfly-q{q}.adj.txt")
    default_cfg = os.path.join(default_topo_dir, "sonic-config")
    ap.add_argument(
        "--topo-dir",
        default=default_topo_dir,
        help="top-level dir for this q's topology (default: ../q{q}, '{q}' substituted)",
    )
    ap.add_argument(
        "--out",
        default=default_out,
        help="primary (no-binds) containerlab YAML path; '{q}' substituted",
    )
    ap.add_argument(
        "--out-binds",
        default=default_out_binds,
        help="binds variant YAML path; '{q}' substituted",
    )
    ap.add_argument(
        "--adj",
        default=default_adj,
        help="adjacency sidecar path ('{q}' is substituted)",
    )
    ap.add_argument(
        "--emit-configs",
        action="store_true",
        default=True,
        help="emit per-switch config_db.json and frr.conf (default: on)",
    )
    ap.add_argument(
        "--no-emit-configs",
        dest="emit_configs",
        action="store_false",
        help="skip per-switch config emission",
    )
    ap.add_argument(
        "--config-dir",
        default=default_cfg,
        help="output dir for per-switch configs ('{q}' is substituted)",
    )
    ap.add_argument(
        "--emit-binds-yaml",
        action="store_true",
        default=True,
        help="also emit a binds-variant YAML alongside the no-binds one (default: on)",
    )
    ap.add_argument(
        "--no-emit-binds-yaml",
        dest="emit_binds_yaml",
        action="store_false",
        help="skip the binds-variant YAML",
    )
    ap.add_argument(
        "--bind-dir-rel",
        default="sonic-config",
        help="relative path (from clab YAML location) to per-switch config dir "
             "(default: sonic-config). '{q}' is substituted.",
    )
    args = ap.parse_args()

    if not is_prime(args.q):
        # Prime power would also work mathematically, but requires GF(p^k)
        # arithmetic which is out of scope for this stdlib generator.
        print(
            f"error: q={args.q} is not prime; only prime q is supported here.",
            file=sys.stderr,
        )
        return 2

    points = projective_points(args.q)
    edges, absolute = polarity_edges(points, args.q)
    verify(points, edges, absolute, args.q)

    wiring = build_wiring(points, edges, absolute, args.q, variant=args.variant)

    topo_dir = args.topo_dir.replace("{q}", str(args.q))
    out_path = args.out.replace("{q}", str(args.q))
    out_binds_path = args.out_binds.replace("{q}", str(args.q))
    adj_path = args.adj.replace("{q}", str(args.q))
    bind_dir_rel = args.bind_dir_rel.replace("{q}", str(args.q))
    cfg_dir = args.config_dir.replace("{q}", str(args.q))

    os.makedirs(topo_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    # Always emit the no-binds YAML (the canonical one for script-driven deploys)
    emit_yaml(
        points, edges, absolute, args.q, out_path, wiring,
        with_binds=False, bind_dir_rel=bind_dir_rel,
    )
    # Optionally emit the binds variant
    if args.emit_binds_yaml:
        emit_yaml(
            points, edges, absolute, args.q, out_binds_path, wiring,
            with_binds=True, bind_dir_rel=bind_dir_rel,
        )
    emit_adjlist(points, edges, args.q, adj_path)

    cfg_count = 0
    if args.emit_configs:
        cfg_count = emit_configs(wiring, cfg_dir)

    print(f"variant          = {args.variant}")
    print(f"q                = {args.q}")
    print(f"switches         = {len(points)}")
    print(f"fabric radix     = {args.q + 1}")
    print(f"absolute points  = {len(absolute)}")
    print(f"fabric links     = {len(edges)}")
    print(f"host links       = {len(points)}")
    print(f"total links      = {len(edges) + len(points)}")
    print(f"topo dir         = {topo_dir}")
    print(f"yaml (no-binds)  = {out_path}")
    if args.emit_binds_yaml:
        print(f"yaml (binds)     = {out_binds_path}")
    print(f"adj sidecar      = {adj_path}")
    if args.emit_configs:
        print(f"configs written  = {cfg_count} switches in {cfg_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
