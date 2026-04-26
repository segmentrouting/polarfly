# AGENTS.md — polarfly

## What this is

A containerlab-based SONiC fabric lab using the **Polarfly topology** (Erdős–Rényi
polarity graph of the projective plane `PG(2, q)` for prime `q`). Each switch is
a `docker-sonic-vs:latest` container; the fabric is fully configured for SRv6
uSID with eBGP. Generation, wiring, and per-switch configs are all produced by
a single Python tool from `topogen2/`.

Two scales are tracked in-tree:

- **q=7** → 57 switches, 224 fabric edges, 8 absolute points (verified working: BGP converges, SRv6 traffic flows end-to-end).
- **q=13** → 183 switches, 1274 fabric edges, 14 absolute points (generated, ready to deploy on a 96 GB host).

## Layout

```
polarfly/
├── topogen2/polarfly_clab.py        # the generator (stdlib only)
├── q7/
│   ├── sonic-polarfly-q7.clab.yaml          # binds variant (uses sonic-config/)
│   ├── sonic-polarfly-q7-nobinds.clab.yaml  # plain variant (configs pushed at runtime)
│   ├── polarfly-q7.adj.txt                  # adjacency sidecar
│   ├── q7-config.sh                         # parallel deploy/config script
│   └── sonic-config/sw001..sw057/{config_db.json, frr.conf}
├── q13/                                     # same shape, 183 switches
└── topogen/, radix-8/, sonic-radix8/, xarchive/, diagrams/, README.md, *.png, config.sh
                                             # legacy — DO NOT modify
```

The `topogen/`, `radix-8/`, `sonic-radix8/`, `xarchive/`, `diagrams/`,
`polarfly.png`, `radix-8-polarfly.png`, root `README.md`, and root `config.sh`
are legacy assets. Treat them as read-only history.

## The generator

`topogen2/polarfly_clab.py` is stdlib-only Python. From a single `--q N`
invocation it emits the entire `q<N>/` directory:

- `sonic-polarfly-q<N>.clab.yaml` — containerlab YAML with bind mounts to `sonic-config/sw###/`
- `sonic-polarfly-q<N>-nobinds.clab.yaml` — same topology, no binds
- `polarfly-q<N>.adj.txt` — adjacency sidecar (humans + scripts)
- `sonic-config/sw###/config_db.json` + `sonic-config/sw###/frr.conf` for every switch

Useful flags: `--q`, `--out`, `--out-binds`, `--adj`, `--config-dir`,
`--bind-dir-rel`, `--emit-configs`, `--emit-binds-yaml`, `--topo-dir`. Defaults
write everything under `../q<q>/` relative to the script.

When changing the generator, regenerate **both** `q7/` and `q13/` and spot-check
counts (see "Verifying" below).

## Per-switch design (locked in — don't drift)

Each switch `sw###` (1-indexed, zero-padded to 3 digits, `sw_idx_1` below):

| Item | Formula |
|---|---|
| ASN | `65000 + sw_idx_1` |
| Loopback v6 | `fc00:0:1<NNN>::1/128` where `NNN = format(sw_idx_1, '04x')` (sw001 → `fc00:0:1001::1`, sw183 → `fc00:0:10b7::1`) |
| Locator | `fc00:0:1<NNN>::/48`, `usid-f3216`, block-len 32 / node-len 16 |
| uN SID | locator prefix `fc00:0:1<NNN>::/48` |
| uDT6 SID | `fc00:0:1<NNN>:e000::/64` → `Vrf-tenant` (single per-switch VRF) |
| uA SIDs | **global block `fc00:0::/32`**: `Ethernet0 → fc00:0:f000::/48`, `Ethernet4 → fc00:0:f001::/48`, …, indexed by **local fabric port index**. Same SID values reused on every switch — they're locally advertised, no global collision. |
| Fabric P2P | `2001:db8:1:<edge_hex>::/127`; **lower-index endpoint gets `::0`, higher gets `::1`**. |
| Host subnet | `2001:db8:a<NNN>::/64`; switch `::1`, host `::2`. |
| Mgmt | `172.100.0.0/23`; switches `.0.11+i`, hosts `.1.11+i`. |

Containers: switches `docker-sonic-vs:latest`, hosts `iejalapeno/alpine-srv6:1.0`.
Style references (read-only): `../srv6-oci/01-sonic-vs/config/{leaf00,spine00}/{config_db.json,frr.conf}`
and the green-host model in `../srv6-oci/01-sonic-vs/topology.yaml`.

**Hosts are deferred.** The generator currently emits host nodes in YAML but no
host configs. Future work (not yet requested): green-host-style SRv6 encap routes.

## Critical gotchas

These are not optional — getting them wrong silently breaks the fabric.

### 1. containerlab link endpoints MUST use `eth1..ethN`, not `Ethernet0..EthernetN`

When a veth attaches as `Ethernet0` directly into `sonic-vs`, syncd's
`SAI_HOSTIF` create fails with `SAI_STATUS_FAILURE` (name collision — SONiC
itself creates the `Ethernet<N>` hostif and binds it to `ethN` per
`port_config.ini`'s `index` field). orchagent then never publishes
`INTF_TABLE` entries → no IPv6 ever appears on the port → BGP never comes up.

The generator wires:

- fabric port at local index `i` (0-based) → `eth(i + 1)`
- host port → `eth(q + 2)`

Inside the container, SONiC remaps `eth1..ethN` → `Ethernet0, Ethernet4, …`.
All `config_db.json`, `frr.conf`, sysctls, and the deploy script use
`Ethernet<N>` names; only the containerlab YAML uses `ethN`.

### 2. Kernel-level admin-up + MTU before sonic-cfggen

The deploy script must explicitly:

```
ip link set Ethernet<N> mtu 9100 up
```

**before** `sonic-cfggen --write-to-db`, and **again** after
`supervisorctl restart all`. Otherwise intfmgrd misses the netdev appearance
and the interface stays Down even after config push.

### 3. Per-interface IPv6 sysctls

For static IPv6 to stick on each `Ethernet<N>`:

```
net.ipv6.conf.<iface>.forwarding = 1
net.ipv6.conf.<iface>.accept_ra  = 0
```

The deploy script applies these per-iface; don't rely on the all/default scopes.

### 4. Purge SONiC's default `router bgp 65100`

`docker-sonic-vs:latest` ships with a stub `router bgp 65100` in FRR. Before
applying our config:

```
vtysh ... -c "no router bgp 65100"
```

The deploy script handles this.

### 5. Container naming requires `prefix: ""`

The deploy script discovers switches with regex `^sw[0-9]{3}$`. This only
matches because the YAML sets `prefix: ""` at topology level (otherwise
containerlab prefixes with the lab name).

### 6. Absolute points use one fewer fabric port

In `PG(2, q)`, an "absolute" point `P` satisfies `a² + b² + c² ≡ 0 (mod q)`,
producing a self-loop in the abstract graph that we drop physically. So
absolute switches have radix `q` instead of `q + 1`.

- q=7: 8 absolute switches (1-indexed: sw026, sw027, sw032, sw035, sw039, sw042, sw047, sw048)
- q=13: 14 absolute switches (zero-indexed: `[6, 9, 19, 22, 57, 62, 69, 76, 79, 118, 134, 141, 148, 153]`)

The generator computes these; don't hand-edit.

## Deploying

```sh
# from polarfly/q7/ or polarfly/q13/
sudo containerlab deploy -t sonic-polarfly-q<N>-nobinds.clab.yaml
./q<N>-config.sh                  # parallel, --jobs 32 default
./q<N>-config.sh --jobs 16        # throttle if host is small
./q<N>-config.sh --serial         # one switch at a time (debug)
./q<N>-config.sh sw001 sw057      # specific switches only
```

The script auto-detects `q` from the parent directory name. The `q7-config.sh`
and `q13-config.sh` files are content-identical by design.

The binds variant (`sonic-polarfly-q<N>.clab.yaml`) also works, but the script
`docker cp`s configs at runtime regardless, so binds aren't required.

Each `docker-sonic-vs` consumes <100 MB; q=13 (366 containers) is comfortable
on a 96 GB host. For q=13, eventually consider pre-checking
`fs.inotify.*` and `net.ipv[46].neigh.default.gc_thresh*` (not yet wired in).

## Verifying after a regen

Counts must match exactly:

| q | switches | fabric edges | host links | total links | adj lines |
|---|---|---|---|---|---|
| 7 | 57 | 224 | 57 | 281 | 285 (4 header) |
| 13 | 183 | 1274 | 183 | 1457 | 1461 (4 header) |

Quick smoke test:

```sh
grep -cE '^\s{4}sw[0-9]{3}:' q<N>/sonic-polarfly-q<N>.clab.yaml   # node count
grep -cE '^\s+- endpoints:' q<N>/sonic-polarfly-q<N>.clab.yaml    # link count
ls q<N>/sonic-config | wc -l                                      # = node count
```

Spot-check formulas on the first and last switch:

```sh
grep -E 'router bgp|fc00:0:1|locator|usid' q13/sonic-config/sw001/frr.conf
grep -E 'router bgp|fc00:0:1|locator|usid' q13/sonic-config/sw183/frr.conf
```

For q=13 sw001 expect `router bgp 65001`, loopback `fc00:0:1001::1`,
locator `fc00:0:1001::/48`. For sw183 expect `65183`, `fc00:0:10b7::1`,
`fc00:0:10b7::/48`.

## When extending

- Maintain the per-switch design table verbatim. Any drift in SID/ASN/loopback
  formulas requires regenerating **both** q7 and q13.
- Keep `q<N>-config.sh` files identical across q-dirs (they auto-detect q).
- For new scales (e.g., q=11, q=17), just `python3 topogen2/polarfly_clab.py --q <N>`;
  the generator handles everything. Copy a `q<N>-config.sh` from an existing q-dir.
- BGP convergence on q=7 yields 98–100 received prefixes per peer (Polarfly
  diameter-2 propagation). Expect proportionally more on q=13.
