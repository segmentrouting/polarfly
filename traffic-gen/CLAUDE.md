# CLAUDE.md — SRv6 PolarFly Lab Topology Project

## Project Summary

This project validates a novel datacenter fabric design called **WCMP-SRv6-PolarFly**: weighted multipath SRv6 source routing over PolarFly topologies, proposed as a structured alternative to Amazon's RNG (Resilient Network Graphs) quasi-random fabric architecture. The goal is to build a lab-scale PolarFly topology, implement SRv6-based forwarding with weighted multipath, and validate the theoretical claims from the companion whitepaper (`srv6-polarfly-whitepaper.md`).

## Core Concepts

### PolarFly Topology

PolarFly is a **diameter-2** network topology based on the **Erdős–Rényi polarity graph** ER_q, derived from the projective plane PG(2, q) over a finite field GF(q). Key properties:

- **Vertices:** N = q² + q + 1 routers, where q must be a **prime power** (the construction is mathematically valid for all prime powers, but lab validation focuses on **prime q only** for implementation simplicity; verify whether even-characteristic cases matter for the whitepaper's high-radix arguments)
- **Fabric degree:** q + 1 (each router has q + 1 fabric-facing links)
- **Diameter:** exactly 2 — any two routers are at most 2 hops apart
- **Moore bound efficiency:** >96% at moderate radixes, ~99% at q=127
- **C4-free:** any two non-adjacent vertices share **exactly one** common neighbor — this is why it approaches the Moore bound, and it is also the source of the path diversity challenge

### The Path Diversity Inversion

Moore-bound optimality and minimal-path diversity are structurally in tension. Because ER_q is C4-free, most non-adjacent pairs have **exactly one** minimal (2-hop) path. This is the central routing challenge: shortest-path routing would congest singleton paths. Amazon's RNG solves this by abandoning minimality (Spraypoint spray routing over random graphs); our design solves it with SRv6 source routing over explicit minimal + non-minimal paths.

### Adjacency in ER_q

Vertices are points of PG(2, q), represented as equivalence classes of nonzero vectors (a, b, c) in GF(q)³. Two vertices u = (u₀, u₁, u₂) and v = (v₀, v₁, v₂) are **adjacent** iff they satisfy the polarity (orthogonality) relation:

```
u₀·v₀ + u₁·v₁ + u₂·v₂ = 0  (in GF(q))
```

**Self-conjugate vertices** (those orthogonal to themselves: u₀² + u₁² + u₂² = 0) have degree q instead of q + 1. The number of self-conjugate vertices depends on q mod 4.

### Path Derivation is Algebraic

This is the key differentiator vs. RNG and vs. generic source routing on arbitrary topologies:

- **Minimal path (2-hop):** The unique common neighbor (relay) of two non-adjacent vertices u, v is computable directly from their projective coordinates via finite-field arithmetic — no SPF, no link-state flooding
- **Non-minimal paths (3-hop):** On the order of q edge-disjoint 3-hop paths exist per pair (total pair connectivity ≈ q + 1); these are also enumerable from coordinates
- **No path computation protocol exists in this design** — the encap node synthesizes segment lists from destination coordinates alone

### W-CMP (Weighted ECMP)

Traffic between a pair splits across derived SRv6 segment lists:

- **w_min** fraction on the unique minimal (2-hop) path
- **(1 − w_min)** spread evenly across the non-minimal (3-hop) set
- The weight is a **derived function of q**, not a fixed constant — optimal split shifts toward non-minimal as q grows (single path's share shrinks as 1/(q+1))
- Weight function inputs: q, path-length ratio (2 vs. 3 hops), pair type (in multi-plane configs), and the **live-vertex set** (for partial deployments)
- A fixed 40/60 split is a reasonable starting point for small q (e.g., q=7) but is not the final design

### SRv6 State Economics

The reason SRv6 dissolves the historical objection to structured topologies on commodity ASICs:

- **RNG's critique of k-path routing:** with n=10K, k=8, ~4 hops/path, tunnel-based implementations need ~320K forwarding entries/router; commodity ASICs support 4–16K — a 20–80× gap
- **SRv6 uSID restructures this:** a 3-hop path fits in a single uSID carrier (often no SRH needed); path state is O(k·n) segment lists in cheap encap-node policy memory; transit FIB is O(n) plain LPM — no per-path entries, no tunnels, no VRFs
- Transit ASICs are as "stupid" as RNG's — stupider, since they carry no ECMP group pressure

### Multi-Plane Slicing

High-radix switches can be logically split across multiple PolarFly planes:

- **Dual-plane (2×q):** e.g., a 64-port switch runs two q=31 planes → dual minimal-path ECMP, plane-granular heterogeneity
- **k=3 plane membership:** each switch joins 2 of 3 planes; any two 2-subsets of {A,B,C} intersect → diameter 2 preserved globally; path multiplicity is pair-type-dependent (same-type pairs get 2 minimal paths, cross-type pairs get 1)
- **k≥4:** disjoint memberships appear → diameter 4; effectively a hand-rolled star product (compare against PolarStar)

### MRC (Multipath Reliable Connection)

MRC is the transport layer that completes the backend/training-fabric design:

- Published May 2026 by OpenAI + AMD/Broadcom/Intel/Microsoft/NVIDIA via OCP
- Extends RDMA-over-Ethernet: **one connection sprays across multiple paths** with reorder tolerance
- Per-path congestion control (AMD's NSCC algorithm, part of UEC CC spec)
- Deployed on ConnectX-8, Pollara, Vulcano, Thor Ultra NICs
- **SRv6 switch support** on Spectrum-4/5 and Tomahawk 5 — same encap substrate as our design
- Deployed in production: OpenAI GB200 clusters (OCI Abilene, Microsoft Fairwater)
- Companion paper: "Resilient AI Supercomputer Networking using MRC and SRv6"

MRC on PolarFly enables **per-packet W-CMP** (vs. per-flow in general cloud), eliminates elephant-flow collision risk, and turns static algebraic weights into congestion-modulated priors via NSCC feedback.

## Comparison Framework: RNG vs. WCMP-SRv6-PolarFly

| Dimension | RNG wins | PolarFly wins |
|---|---|---|
| Heterogeneous degree | Per-node, in-fabric | Plane-granular (coarser) |
| Unquantized growth | Yes (any n, d) | No (q must be prime power) |
| Operational simplicity | Stateless fabric, unconfigurable | Intelligence at encap |
| Diameter / latency | — | Deterministic 2 vs. ~4-5 sprayed |
| Per-bit cost & power | — | Near Moore-bound floor; compounds with BW |
| Transit ASIC state | — | LPM only; no ECMP table pressure |
| Control plane complexity | — | No path computation protocol |
| Failure model | Continuous, statistical | Discrete → continuous with planes + MRC |
| AI backend fit | Deferred by Amazon | Natural home |

**Key thesis:** The two designs sort by operating model, not by scale. RNG wins elastic multi-tenant fleets; PolarFly wins deliberate build-once fabrics (especially AI backend/training).

## Lab Topology Planning

### Recommended Lab Scale

Small **prime** values of q suitable for lab validation (note: the ER_q construction mathematically admits any prime power, but prime-power extension-field arithmetic adds implementation complexity; restrict to primes for lab work and verify whether the whitepaper's high-radix arguments depend on prime-power availability):

| q | N = q²+q+1 | Fabric degree (q+1) | Notes |
|---|---|---|---|
| 3 | 13 | 4 | Minimum interesting; very small |
| 5 | 31 | 6 | Small but complete validation |
| **7** | **57** | **8** | **Primary lab target** |
| 11 | 133 | 12 | Mid-scale |
| 13 | 183 | 14 | Mid-scale |
| **17** | **307** | **18** | **Stretch target if resources allow** |

**q=7 is the likely sweet spot** for physical lab: 57 nodes at degree 8 is achievable with commodity 8-port switches or virtual routers, large enough to demonstrate all routing properties, small enough to cable and manage.

### What to Validate

1. **Topology construction:** Generate ER_q adjacency from PG(2,q) coordinates; verify diameter=2, C4-free, degree distribution (q+1 vs. q for self-conjugate vertices)
2. **Algebraic path derivation:** For every non-adjacent pair, compute the unique minimal relay and the non-minimal path set from coordinates; verify against graph traversal
3. **SRv6 encapsulation:** Program segment lists at encap nodes; verify transit forwarding via uSID LPM; measure FIB occupancy vs. equivalent k-shortest-path state
4. **W-CMP forwarding:** Implement weighted traffic split across minimal + non-minimal segment lists; measure per-path utilization under uniform and adversarial traffic
5. **Failure scenarios:** Kill the minimal-path relay for a pair; verify weight redistribution to non-minimal set; measure RTT transition with and without dual-plane slicing
6. **Multi-plane slicing (if radix allows):** Dual-plane at q=3 on 8-port switches (2×4 fabric ports); verify dual minimal-path ECMP and plane-independent failure
7. **MRC integration (stretch goal):** If MRC NICs are available, validate per-packet spray over algebraic path sets with NSCC feedback

### Platform

- **Switching:** docker-sonic-vs (containerized SONiC virtual switch)
- **Hosts/traffic:** Custom Alpine image from https://github.com/segmentrouting/srv6-mrc-emulator/tree/main/host-image — serves as traffic generator and simulator
- **Orchestration:** Containerlab (assumed; confirm)
- **Initial scale:** q=7 (57 nodes, degree 8)
- **Stretch scale:** q=17 (307 nodes, degree 18) — contingent on docker-sonic-vs being lightweight enough to run 307+ containers

### Software Components to Build

1. **Topology generator:** Given q, produce the ER_q graph (adjacency list, coordinate assignments, self-conjugate vertex identification)
2. **Path calculator:** For each pair, derive minimal relay and non-minimal path set algebraically from coordinates
3. **SRv6 segment-list synthesizer:** Convert algebraic paths to SRv6 uSID segment lists; compute W-CMP weights as f(q, pair-type, live-vertex-set)
4. **Configuration generator:** Produce FRR/SONiC/XR configs for each node (interfaces, SRv6 locators, uSID SIDs, SR policies with weighted candidate paths)
5. **Containerlab/topology deployer:** Wiring definition matching ER_q adjacency
6. **Validation test suite:** Connectivity, path verification, traffic distribution measurement, failure injection
7. **Visualization:** Topology graph rendering with coordinate labels, path highlighting

## Technical Context

### Bruce's Environment and Expertise

- **OS:** macOS Tahoe (beta)
- **Networking expertise:** Senior-level in SRv6, AI fabric architecture, datacenter networking
- **SRv6 specifics:** Deep familiarity with uSID, F3216/F1616 carrier formats, RFC 8986, uED (SRv6 uSID Point of Encapsulation-Decapsulation) — Bruce coined the uED acronym
- **Open source:** Contributor to the Jalapeno project (github.com/jalapeno/) — SRv6 SDN controller ecosystem; new project `syd` for topology/use-case-agnostic SRv6 SDN
- **Lab tooling:** Experience with QEMU/qcow2 image baking, TRex traffic generator, Containerlab, FRR, SONiC, Cisco 8000 emulator
- **SONiC:** Aware of SONiC PR #4404 for SRv6 uSID multi-tenant deployability
- **Current work context:** Also preparing an OCP conference abstract on SRv6 uSID multi-tenant design for AI backend networks

### Related Project Context

- A full whitepaper draft exists: `srv6-polarfly-whitepaper.md` — covers nine sections including the RNG comparison, multi-plane slicing, MRC integration, and a comparative scorecard
- Bruce has previously built a detailed 3-tier AI factory network architecture (Scalable Units of 256 hosts / 2,048 GPUs → spine → 64 SUs at 131,072 GPUs total)
- Rail-axis spine group alignment and 512×100G leaf-spine link granularity decisions are established
- The Jalapeno `syd` project may eventually serve as the SDN controller for PolarFly SRv6 policy programming

### Key Terminology

- **ER_q:** Erdős–Rényi polarity graph of order q
- **PG(2,q):** Projective plane over GF(q)
- **Self-conjugate vertex:** A vertex orthogonal to itself (u₀² + u₁² + u₂² = 0 in GF(q)); has degree q instead of q+1
- **uSID:** Micro-SID — compressed SRv6 segment identifier fitting multiple SIDs in one 128-bit IPv6 address
- **uED:** SRv6 uSID Point of Encapsulation-Decapsulation (Bruce's term)
- **W-CMP:** Weighted ECMP — traffic split with explicit per-path weights
- **MRC:** Multipath Reliable Connection — OCP transport protocol for reorder-tolerant multi-path RDMA
- **NSCC:** AMD's congestion control algorithm used within MRC (part of UEC CC spec)
- **Spraypoint:** RNG's routing protocol — flow-level spray via ECMP hashing + waypoint fan-in; NOT per-packet
- **ShuffleBox:** RNG's passive optical cabling device — works because random graphs only need statistical wiring correctness; NOT applicable to structured topologies

### Finite Field Arithmetic Notes for Implementation

For lab work with prime q: GF(q) arithmetic is simply **modular arithmetic mod q**. All operations (addition, multiplication, finding multiplicative inverses) are standard mod-q. This keeps the topology generator straightforward.

The general ER_q construction admits prime powers (q = p^k, k > 1), which would require polynomial arithmetic over GF(p) modulo an irreducible polynomial of degree k. This is not needed for the lab targets (q=7, q=17) but may matter for the whitepaper's high-radix arguments if prime-power q values are claimed — **verify against PolarFly paper whether even-characteristic (q = 2^k) cases are validated**.

Projective coordinates are equivalence classes: (a, b, c) ~ (λa, λb, λc) for any nonzero λ ∈ GF(q). Canonical form: normalize to the leftmost nonzero coordinate = 1. Total points in PG(2,q): (q³ - 1)/(q - 1) = q² + q + 1.

Useful Python library: `galois` — handles GF(q) for both prime and prime-power fields.

## References

- Bernardi et al., "RNG: Flat Datacenter Networks at Scale," arXiv:2604.15261, 2026
- Lakhotia et al., "PolarFly: A Cost-Effective and Flexible Low-Diameter Topology," SC22, arXiv:2208.01695
- OpenAI et al., MRC specification, OCP, May 2026
- OpenAI et al., "Resilient AI Supercomputer Networking using MRC and SRv6"
- RFC 8986 — SRv6 Network Programming
- RFC 9256 — SR Policy Architecture
- Intel Labs PolarFly repo: github.com/IntelLabs/PolarFly
- SRv6 MRC emulator (host image): github.com/segmentrouting/srv6-mrc-emulator
