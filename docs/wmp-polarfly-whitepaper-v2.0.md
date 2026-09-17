# WMP-PolarFly: Weighted Multipath Routing on Algebraically Optimal Low-Diameter Datacenter Topologies

**Author:** Bruce McDougall, Cisco Systems
**Co-author:** Christian Martin, Cisco Systems
**Status:** DRAFT v2.0
**Date:** September 2026

---

## Abstract

Low-diameter topologies offer a compelling alternative to Clos fat trees for datacenter fabrics, eliminating spine layers and reducing switch count, optics, and per-bit power consumption. However, their adoption has been blocked by a practical objection: the lack of shortest-path diversity starves standard ECMP load balancing of the path entropy it requires, and the k-shortest-path routing techniques that could compensate cannot be realized on commodity switch ASICs.

This paper presents **WMP-PolarFly**, a routing architecture that resolves this objection for the PolarFly topology, a diameter-2 graph that asymptotically reaches the Moore bound for scale efficiency. WMP-PolarFly uses SRv6 uSID source routing to steer traffic across a source-destination pair's **shortest path (SP)** and **next-shortest-paths (NSPs)** with algebraically derived weights. The SP and NSP set is computed directly from the PolarFly graph's projective-plane coordinates with no path-computation protocol, no topology probing, and no transit forwarding state beyond plain LPM. We present deployment configurations spanning native high-bandwidth fabric links for MRC-based AI training clusters, multi-slice partitioning for flow-level redundancy in general-purpose cloud, multi-tenant VPC overlays with combined transport and service uSID carriers, and physically separate PolarFly planes for first-hop switch redundancy. We compare WMP-PolarFly against Clos fat trees, Amazon's RNG random-graph architecture, and the Spritz sender-based load-balancing framework, and demonstrate that WMP-PolarFly matches or exceeds each on switch count, optics, and per-bit cost while delivering deterministic diameter-2 latency on open standards deployable today.

---

## 1. Introduction

### 1.1 The Clos scaling problem

Clos fat trees have dominated datacenter fabric design for over a decade, and for good reason: they provide non-blocking, high-bisection-bandwidth connectivity with a clean hierarchical structure. But that hierarchy comes at a cost. Spine and super-spine switches serve no endpoints; they exist purely to aggregate and redistribute traffic. In a 3-tier Clos, roughly one-third of all switches and half of all fabric optics are consumed by these portless transit layers. Capacity is stranded structurally, and the cost scales superlinearly with endpoint count.

### 1.2 Low-diameter topologies as alternatives

Flat topologies, where switches interconnect directly with no aggregation layers, have promised an escape from the Clos cost curve for over a decade. The key insight: if every switch serves both endpoints and fabric, no switch is wasted on pure transit. Jellyfish [12] first demonstrated that random regular graphs could match Clos throughput at lower cost; Slim Fly [5] and Xpander [6] showed that structured graphs could approach theoretical efficiency limits; and PolarFly [2] achieved the first asymptotic match to the Moore bound at diameter 2, the theoretical maximum number of nodes for a given degree and diameter.

The common obstacle: these topologies provide far fewer equal-cost shortest paths per endpoint pair than a Clos, starving standard ECMP of the path entropy it needs for effective load balancing. Prior solutions required either HPC-class adaptive routing hardware (UGAL) or abandoning structured topologies entirely in favor of random graphs (RNG/Spraypoint). This paper demonstrates a third path: SRv6 source routing on PolarFly, exploiting the topology's algebraic structure to derive weighted multipath forwarding from endpoint coordinates alone.

### 1.3 Contributions

This paper makes five contributions:

1. **WMP-PolarFly architecture**: a weighted multipath routing design where the SP and NSPs are derived algebraically from PolarFly's projective-plane coordinates, with SRv6 uSID encapsulation concentrating path state at the encap node while transit switches carry only O(n) LPM entries.

2. **Encap/decap architecture**: an analysis of three encapsulation models (NIC-level MRC, host-based encap with egress-leaf decap, and ingress-leaf encap), with a recommendation for host-based encap that places path state in cheap host DRAM rather than constrained NIC SRAM.

3. **Multi-tenant VPC overlay**: a uSID carrier composition that combines transport path (SP/NSP) with tenant service function (uDT6) in a single SRv6 header, using on-demand algebraic path computation that eliminates control-plane consultation for per-flow path setup.

4. **Deployment configuration analysis**: an honest examination of native high-bandwidth links versus multi-slice breakout, showing that slicing adds path diversity but not bandwidth, and that different deployment scenarios benefit from different configurations.

5. **Comparative analysis**: quantitative comparisons against Clos, RNG, and Spritz at matched endpoint populations.

### 1.4 Paper organization

Section 2 presents PolarFly's topology foundations and the path diversity challenge. Section 3 develops the WMP-PolarFly architecture including encap/decap models and multi-tenant overlay. Section 4 analyzes deployment configurations. Section 5 addresses resilience. Section 6 examines deployment scenarios. Section 7 provides comparative analysis. Section 8 concludes.

A practical note: while Amazon's RNG is production-proven, it is not publicly available. Spraypoint has not been open-sourced and ShuffleBoxes have no known commercial source. WMP-PolarFly builds on open-source components (FRR, SONiC) and standard SRv6 (RFC 8986 [8], RFC 9256 [7]), and is deployable today.

---

## 2. PolarFly Topology Foundations

### 2.1 Construction and properties

PolarFly [2] is defined by a single parameter **q**, which must be an odd prime or odd prime power. From q, three properties follow directly:

- **N = q² + q + 1** — the number of switches in the fabric
- **Fabric degree = q + 1** — the number of fabric-facing ports per switch
- **Diameter = 2** — the maximum number of hops between any two switches

The topology is the Erdős–Rényi polarity graph ER_q over the projective plane PG(2, q). Each switch is assigned a projective coordinate, a 3-tuple (a, b, c) over the finite field GF(q), and two switches are directly connected if and only if their coordinates are orthogonal: a₁a₂ + b₁b₂ + c₁c₂ ≡ 0 (mod q).

For example, with q = 7 on a 16-port switch, 8 ports serve the fabric (degree q+1 = 8) and 8 serve endpoints, yielding a fabric of 7² + 7 + 1 = 57 switches from just 8 fabric uplinks each. PolarFly asymptotically reaches the Moore bound, the theoretical maximum node count for a given degree and diameter, exceeding 96% efficiency at practical radixes and 99% at q = 127. It is the most scale-efficient diameter-2 topology known. (See Appendix A for the odd-prime-power constraint and feasible-degree lattice.)

| q | Type | Switches (q²+q+1) | Fabric degree (q+1) |
|---|---|---|---|
| 7 | prime | 57 | 8 |
| 31 | prime | 993 | 32 |
| 61 | prime | 3,783 | 62 |
| 127 | prime | 16,257 | 128 |
| 251 | prime | 63,253 | 252 |

### 2.2 The path diversity inversion

PolarFly's efficiency comes from a structural property: **no two switches share more than one common neighbor**. This maximizes scale (edges are never wasted on redundant two-hop paths) but creates a routing challenge: between most non-adjacent switch pairs, there is only **one** shortest (2-hop) path. In networking terms, every source-destination pair has exactly one spine to traverse, with no second equal-cost path to hash onto.

The irony: the property that makes PolarFly the most efficient topology simultaneously starves it of the path redundancy that ECMP depends on. **Optimality and path diversity are structurally in tension.**

### 2.3 Routing approaches for low-diameter topologies

Four approaches address the path diversity challenge, solving the same problem with different assumptions about what the operator controls and what guarantees they receive in return:

**UGAL / in-network adaptive routing.** Switches sense congestion in real time and deflect traffic onto longer non-minimal paths. This is the standard approach in the HPC Dragonfly and Slim Fly lineage. It delivers real-time adaptivity but requires adaptive-routing hardware that commodity Ethernet ASICs generally do not provide, though certain implementations on standard hardware may be feasible in constrained settings.

**RNG / Spraypoint (topology randomness).** Amazon's RNG [1] uses quasi-random graphs where the randomness of the wiring provides path diversity natively. Spraypoint sprays flows across the full neighbor set using standard ECMP, with traffic converging through waypoint nodes. It achieves diversity through topology design but requires a custom protocol that is not publicly available. The cost is path length: typically 4–5 hops versus PolarFly's diameter of 2.

**Spritz (endpoint probing).** Bonato et al.'s Spritz [13] moves adaptive routing to the endpoint on commodity Ethernet, using ECN, packet trimming, and timeout feedback to probe and cache efficient paths. It works on any low-diameter topology without needing to know the graph structure, but must discover paths empirically before reaching steady state.

**WMP-PolarFly (algebraic derivation).** The approach presented in this paper: the endpoint derives all paths from the source and destination's projective coordinates using finite-field arithmetic, programs them as SRv6 segment lists, and distributes traffic with explicit weights. It requires SRv6 encapsulation and coordinate assignment, but in return delivers deterministic paths with zero discovery latency and no in-network state beyond plain LPM.

---

## 3. The WMP-PolarFly Architecture

### 3.1 SP and NSP definition

For a given source-destination pair in a PolarFly fabric with parameter q:

- The **shortest path (SP)** is the unique 2-hop path through the pair's single shared neighbor, the relay node.
- The **next-shortest-paths (NSPs)** are 3-hop paths through intermediate nodes that are not the relay and whose paths do not share an edge with the SP. Each non-relay neighbor of the source can provide one edge-disjoint NSP, except when that neighbor is adjacent to the relay (forming a triangle whose candidate path would reuse the SP's final edge). This yields **q−1 NSPs for most pairs**, with a minority yielding q NSPs when no such triangle occurs.

For q = 7: **1 SP + 6 NSPs = 7 total forwarding paths** for most pairs. For q = 31: 1 SP + ~30 NSPs. For q = 127: 1 SP + ~126 NSPs.

### 3.2 Algebraic path derivation

The SP and NSP set is algebraically derivable from endpoint coordinates. The SP relay between two non-adjacent nodes with coordinates A and C is the cross product A × C in GF(q), a single finite-field computation yielding the relay's coordinates directly. The NSPs are enumerated by iterating over A's remaining neighbors (excluding the relay and any triangle-adjacent neighbor) and computing their common neighbor with C.

**Worked example (q = 7).** Every switch has a 3-digit mod-7 address. Router A = (1, 0, 2) wants to reach C = (1, 4, 6). They are not adjacent (dot product = 6 ≠ 0). The SP relay B is the cross product: B = A × C mod 7, yielding one canonical projective point. The encap node emits the SRv6 segment list [uSID-B, uSID-C]. The same arithmetic enumerates 6 NSPs, each through a different first-hop neighbor, producing 6 additional three-SID segment lists.

**Control-plane consequence:** no path-computation protocol is required. An IGP (IS-IS or BGP) distributes node-SIDs and provides liveness detection, but path discovery (the function of RSVP-TE, PCE, or CSPF) is eliminated entirely.

### 3.3 SRv6 uSID encapsulation, state economics, and encap/decap models

SRv6 uSID is what makes WMP-PolarFly viable on commodity hardware. Each SP (2-hop) and NSP (3-hop) fits within a single uSID carrier, typically the IPv6 destination address itself with no SRH required. Path state concentrates at encapsulation nodes as O(k·n) segment lists in host or SmartNIC policy memory, while the transit FIB holds only the node-SID table and uA adjacency table: O(n), plain LPM.

The contrast with tunnel-based k-shortest-path routing is significant. In a tunnel-based implementation, each path through each transit router consumes one or more forwarding entries for label mappings, next-hop associations, and adjacency state. Even at a conservative estimate of one entry per path per router, q = 61 (3,783 switches, ~61 paths per destination) requires 61 × 3,783 ≈ **231K forwarding entries per router**, approaching the >300K IPv6 ALPM capacity of a Broadcom Tomahawk 5. Realistic implementations require multiple entries per path, pushing the total well beyond ASIC limits. At q = 127 the problem compounds to over a million entries regardless of the multiplier. SRv6 uSID bypasses the problem entirely: the transit FIB holds ~4K entries at q = 61 or ~16K at q = 127, regardless of how many paths the encap node programs.

**Three encap/decap models** determine where path intelligence and packet processing live:

**Model A: NIC encap, NIC decap (pure MRC).** The RDMA NIC holds per-QP Entropy Values and performs SRv6 encapsulation. The destination NIC decapsulates. This is how MRC operates today on Clos fabrics. It works well for allreduce (few QPs, few destinations), but may hit NIC resource limits for All-to-All at large scale where thousands of QPs each need EV sets. Segment lists are per destination switch (shared across GPUs on the same switch), but EV programming may be per-QP in the MRC API.
// revisit math of all-to-all

**Model B: Host encap, egress leaf decap (recommended).** The host CPU or DPU performs SRv6 encapsulation with segment lists computed algebraically and cached in host DRAM. The egress leaf switch performs SRv6 decap (End.DT6 or uDT6), strips the outer header, and forwards to the local endpoint based on the inner destination address. This cleanly separates path intelligence (host, unlimited memory) from local delivery (switch, standard forwarding). For All-to-All at q = 61, the host caches segment lists for ~3,782 remote switches × ~61 paths ≈ 231K entries, trivial in host DRAM. This model aligns with the paper's thesis: intelligence at the encap node, minimal state in the fabric.
// Did we actually state "intelligence at the encap node, minimal state in the fabric" in the thesis? if not, we probably should. 
// Also, for the math, i'm using linux iproute2 for my mental model. If all hosts attached to a given node reside on the same subnet, then routing can look like this example q=7 SP+NSPs for node0001-host0001 to node0019-host0152 thru node0019-host0159. Traffic from 2001:db8:a001::1/64 to 2001:db8:a013::8/64 matches the below route entry, is encapsulated per the weighting, uSIDs its way thru the polarfly fabric, and arrives at egress node0019 with outer destination address fc00:0:1013:e000::. node0019 sees its locator and uDT function, pops the outer ipv6 header and does a lookup on the inner destination and passes the traffic to host0159 at 2001:db8:a013::8
```bash
2001:db8:a013::/64 metric 1024 pref medium
	nexthop  encap seg6 mode encap.red segs 1 [ fc00:0:1033:1013:e000:: ] via 2001:db8:a001::1 dev eth1 weight 4 
	nexthop  encap seg6 mode encap.red segs 1 [ fc00:0:1002:100b:1013:e000:: ] via 2001:db8:a001::1 dev eth1 weight 1 
	nexthop  encap seg6 mode encap.red segs 1 [ fc00:0:1009:1004:1013:e000:: ] via 2001:db8:a001::1 dev eth1 weight 1 
	nexthop  encap seg6 mode encap.red segs 1 [ fc00:0:1017:101f:1013:e000:: ] via 2001:db8:a001::1 dev eth1 weight 1 
	nexthop  encap seg6 mode encap.red segs 1 [ fc00:0:101e:101d:1013:e000:: ] via 2001:db8:a001::1 dev eth1 weight 1 
	nexthop  encap seg6 mode encap.red segs 1 [ fc00:0:1025:1031:1013:e000:: ] via 2001:db8:a001::1 dev eth1 weight 1 
	nexthop  encap seg6 mode encap.red segs 1 [ fc00:0:102c:1028:1013:e000:: ] via 2001:db8:a001::1 dev eth1 weight 1
```
// Given the above logic and route entry, any given host would have 56 routes to remote host prefixes, each with 7 SIDs, correct? If that's the case, then with MRC and model B egress node decap, presumably the host/NICs can all be on the same subnet. However, MRC also specifies multi-planar fabrics. In an 8-plane deployment each transmitting NIC would have 56 routes with 56 SIDs each. Correct?

**Model C: Ingress leaf encap, egress leaf decap.** The ingress switch encapsulates on behalf of the source endpoint. Path intelligence lives on the switch control plane. This is the traditional SR-TE model and works, but concentrates path computation on the switch rather than the host, which has more constrained memory and is the opposite of where this architecture argues intelligence should live.

**Recommendation:** Model B for both MRC backend and general-purpose cloud. It places path state in the cheapest memory (host DRAM), scales to All-to-All without NIC resource pressure, and lets the egress leaf handle last-mile delivery with no per-flow state. Model A remains viable for MRC deployments that stay within NIC EV capacity (primarily allreduce-dominant workloads). Model C is available as a fallback where host-based encapsulation is not feasible.

### 3.4 WMP weight computation

Traffic splits across the SP and NSP segment lists with explicit weights. The SP is more efficient (2 hops vs. 3), so it receives a premium, but the premium shrinks as q grows and the SP becomes one path among many.

At q = 7 (7 paths): a 30% SP, ~12% per NSP split is a reasonable starting point. At q = 127 (~127 paths): weights converge toward near-uniform, and the operator may treat all paths as ECMP. The weight is a derived function of q and hop-count ratio, not a constant, though operators can override it for specific traffic patterns.

The NIC or host computes segment lists on demand from coordinates and caches them for active connections. For each unique destination switch, the encap node holds one SP + ~(q−1) NSP segment lists. At q = 61, a host with active connections to 1,000 distinct remote switches caches ~61K segment lists, well within the memory capacity of modern DPUs and SmartNICs. Multiple connections to the same destination switch reuse the same cached segment-list set.

### 3.5 Live-vertex-set adaptation

In a partially deployed fabric, the SP relay between a live pair may not yet be installed. The encap node detects this from the installed-coordinate set and re-derives weights over the realized subgraph, with no protocol convergence required. This conditional weighting over the realized subgraph is, to our knowledge, novel, and enables PolarFly's purely additive expansion model.

### 3.6 Multi-tenant VPC overlay

In multi-tenant cloud deployments, VPC overlays terminate at the host (hypervisor, CNI, or DPU). WMP-PolarFly's SRv6 uSID carrier can combine transport path and tenant service function in a single header, using the F3216 format (32-bit block prefix + up to 6 × 16-bit uSIDs):

**NSP path with tenant termination:**
```
[first_hop_uSID | mid_uSID | dst_switch_uSID | uDT6_tenant_func | END]
```

That is 4 uSIDs plus END, fitting in a single carrier with room to spare. The SP case is shorter at 3 uSIDs plus END. No SRH is needed in either case.

**Where state lives in the multi-tenant model:**

- **Transit switches:** see only node-SIDs. FIB = O(n_switches). No per-tenant, per-host, or per-flow state. A transit switch has no awareness of tenants or destination hosts; it shifts and forwards based on the current active uSID.
- **Egress switch:** processes the final uSIDs. It needs local host routes (O(hosts_per_switch), typically 64–256 entries) and uDT6 tenant functions (O(tenants_on_this_switch), typically dozens to low hundreds). Both are small and local.
- **Source host:** holds SR policy entries per (destination_host × tenant) pair. This is where scale lives, and it lives in host DRAM.

**On-demand flow computation (Andromeda-style, but without the controller):**

Rather than pre-populating segment lists for all possible destinations, the host maintains:

- **Static state (pushed at boot):** a prefix-to-coordinate map (~4K entries for q=61, mapping destination IP prefixes to PolarFly switch coordinates) plus a tenant VRF-to-uDT6 function map (pushed per VM lifecycle event).
- **Cached on demand:** per-flow SR policy entries (transport prefix + tenant suffix), installed on first packet to a new destination and aged out when idle.
- **Working set:** proportional to active flows, not total fabric size × tenants.

The flow setup for a new destination:

1. Destination IP → destination switch coordinate (prefix-to-coordinate table lookup)
2. Coordinate → SP + NSP segment lists (algebraic computation, microseconds, no network round trip)
3. Tenant VRF → uDT6 function SID (local lookup)
4. Construct full uSID carrier: [transport_prefix | uDT6_tenant]
5. Install in host flow cache; subsequent packets hit the cached rule at line rate

This is architecturally similar to Google's Andromeda SDN stack, which also uses host-based encapsulation with on-demand flow installation. The critical difference: Andromeda's first-packet slow path requires a control-plane round trip to the Hoverboard system for encapsulation rules. WMP-PolarFly's first-packet path is purely local, because the host can algebraically compute the transport path from coordinates without consulting any controller. The SRv6 SDN controller (or a simpler coordinator) pushes only topology state (coordinates, SIDs, tenant mappings) to hosts; per-flow path computation is self-service.

---

## 4. Deployment Configurations

A 51.2T switch ships as a 64×800G device. It can be deployed at native port speeds, broken out to 128×400G, or further broken out to 512×100G. The choice determines the PolarFly configuration and has significant implications for cabling complexity, path diversity, and which deployment scenarios benefit.

A key observation: **slicing adds path diversity but not bandwidth.** In a 4-slice q=61 configuration at 512×100G, each inter-switch adjacency is 4×100G = 400G. In a native q=61 configuration at 128×400G, each adjacency is 1×400G, the same aggregate bandwidth. Slicing provides multiple independent SPs per pair (valuable for flow-level ECMP) but no additional capacity between any switch pair.

### 4.1 Native high-bandwidth links (MRC backend)

For AI training clusters using MRC, the optimal configuration minimizes cabling while maximizing per-link bandwidth.

| Configuration | Link speed | Fabric ports | Server ports | Switches | Server attachment |
|---|---|---|---|---|---|
| q=61, 128×400G | 400G | 62 | 66 | 3,783 | 66 × 400G per switch |
| q=31, 64×800G | 800G | 32 | 32 | 993 | 32 × 800G per switch |

MRC handles path diversity at the transport layer: per-packet spraying across the 1 SP + ~(q−1) NSPs within a single PolarFly graph. The switch can serve 100G NIC connections from its 400G or 800G server-facing ports via standard breakout on the server side only.

### 4.2 Multi-slice for flow-level redundancy (general cloud)

For general-purpose cloud fabrics running TCP without MRC, flow-level ECMP is the primary load-balancing mechanism. Multiple SPs per pair (one per slice) give the flow hash more equal-cost options:

| Configuration | Link speed | Fabric ports | Server ports | Switches | SPs per pair | Total paths |
|---|---|---|---|---|---|---|
| 4-slice q=61, 512×100G | 100G | 248 (4×62) | 264 | 3,783 | 4 | 4 + ~240 |
| 4-slice q=31, 512×100G | 100G | 128 (4×32) | 384 | 993 | 4 | 4 + ~120 |
| 8-slice q=31, 512×100G | 100G | 256 (8×32) | 256 | 993 | 8 | 8 + ~240 |

At 4-slice q=31 the server-to-fabric ratio is 384:128 = 3:1, matching the standard cloud oversubscription point.

**Slice isolation** is enforced by the SRv6 data plane: each slice's paths use distinct uA (adjacency) SIDs bound to specific physical interfaces. Operators who prefer maximum path diversity over strict failure-domain isolation can relax this binding and spray across all slices.

### 4.3 Physically separate PolarFly planes (MRC multi-plane)

For deployments requiring first-hop switch redundancy, multiple physically separate PolarFly fabrics serve as independent planes:

| Configuration | Planes | Switches/plane | Total switches | GPUs (at 4×100G) | Physical redundancy |
|---|---|---|---|---|---|
| 2 planes × 8-slice q=31 | 2 | 993 | 1,986 | 127K | 2-way |
| 4 planes × 8-slice q=31 | 4 | 993 | 3,972 | 127K | 4-way |

Each GPU's NIC is broken out with each port connecting to a different physical plane's local switch. A switch failure in one plane affects only that plane's NIC connections.

### 4.4 Scale at modern radix

Both configurations exceed any known single datacenter building. The 4-slice q=61 configuration serves ~1M endpoints; the 2-slice q=127 configuration reaches ~4M endpoints at 99% Moore-bound efficiency. The odd-prime-power constraint (Appendix A) excludes powers of 2, but the lattice of odd primes is dense enough at modern radix that a feasible q lies within a few ports of any target.

---

## 5. Resilience

### 5.1 Single-slice failure model

When a pair's unique SP relay fails, traffic undergoes a discrete transition: 2-hop SP traffic shifts to 3-hop NSPs, producing a detectable RTT step. The encap node re-derives weights algebraically, faster than any IGP reconvergence.

### 5.2 Multi-slice failure model

With 4 slices, a single slice's SP failure leaves 3 surviving SPs at identical hop count. No RTT transition, just a weight rebalance.

### 5.3 MRC transport-level resilience

MRC's per-path EV probing detects a dead path within one RTT-scale window and stops scheduling packets onto it. On PolarFly this composes with algebraic re-derivation: the NIC or host masks the failure instantly; the encap layer re-synthesizes the path set from the updated live-vertex set in the background.

### 5.4 Additive expansion

PolarFly's complete edge set is known in advance. Expansion never breaks an existing link. A landing switch patches into q+1 pre-planned positions, and encap nodes algebraically recompute paths to incorporate the new vertex.

---

## 6. Deployment Scenarios

### 6.1 AI backend with MRC

The backend is the deployment type where PolarFly's advantages compound: the fabric is built once at known size, the operator owns the stack end to end, hardware is uniform per build, and per-bit cost compounds directly into training economics.

MRC's properties map naturally onto WMP-PolarFly: per-packet spraying across the full SP + NSP set eliminates elephant-flow collision risk. Algebraic path-set provisioning replaces fabric-dependent EV configuration with a direct computation at connection setup. NSCC's per-path congestion signals modulate the algebraic WMP weight priors adaptively. The 1–2μs SP/NSP latency gap is well within MRC's reorder window.

Using Model B (host encap, egress leaf decap) for All-to-All collectives, the host caches segment lists for all remote switches in DRAM, avoiding NIC EV capacity constraints. For allreduce-dominant workloads, Model A (NIC-level MRC) remains viable since the QP count is low.

### 6.2 Multi-tenant cloud with VPC overlay

For general-purpose cloud and private cloud deployments with VPC isolation, the multi-tenant architecture of Section 3.6 applies. The host hypervisor or CNI encapsulates each tenant's traffic with a combined transport + service uSID carrier, computed algebraically from the destination switch coordinate and the tenant's uDT6 function SID.

The on-demand flow model keeps the host's working set proportional to active flows rather than total fabric size × tenant count. With Model B encap/decap, the egress leaf performs uDT6 decap and VRF-based forwarding to the destination host, requiring no per-flow state on any transit or egress switch beyond local host routes and tenant function SIDs.

Multi-slice configurations (Section 4.2) provide the flow-level SP redundancy that TCP workloads need. The combined carrier [transport uSIDs | uDT6 tenant function] fits within a single F3216 uSID carrier for both SP and NSP paths.

### 6.3 The deployment boundary

The boundary between "cloud" and "backend" deployment types is less sharp than the literature implies. A fixed-footprint cloud datacenter, whether a sovereign build, a large enterprise private cloud, or a neocloud region, shares many characteristics of the deliberate-fabric deployment: known size at build time, operator-owned stack, uniform hardware generation. WMP-PolarFly is a legitimate candidate wherever the operator owns the host stack and can deploy SRv6 encapsulation at the endpoint.

---

## 7. Comparative Analysis

### 7.1 WMP-PolarFly vs. Clos

**At 3:1 oversubscription (~381K servers, 512×100G switches):**

| Configuration | Switches | Servers | Fabric optics | Hops |
|---|---|---|---|---|
| **3-tier Clos** | 1,792 | ~393K | 524K | 2–4 |
| **WMP-PolarFly 4-slice q=31** | 993 (−45%) | ~381K | 127K (−76%) | 2–3 |

**At 1:1 oversubscription (~254K servers):**

| Configuration | Switches | Servers | Fabric optics | Hops |
|---|---|---|---|---|
| **3-tier Clos** | 2,560 | ~262K | 1,049K | 2–4 |
| **WMP-PolarFly 8-slice q=31** | 993 (−61%) | ~254K | 254K (−76%) | 2–3 |

### 7.2 WMP-PolarFly vs. RNG

At matched oversubscription, WMP-PolarFly and RNG converge to identical switch count and fabric optics. The differentiator is path quality and availability.

**At 3:1:**

| Configuration | Switches | Fabric optics | Paths per pair | Hops |
|---|---|---|---|---|
| **RNG** | 993 | 127K | ~128 edge-disjoint (spray) | 4–5 |
| **WMP-PolarFly 4-slice q=31** | 993 | 127K | 4 SPs + ~120 NSPs | 2–3 |

**MRC backend comparison:**

| Configuration | Switches | GPUs | Fabric optics | Physical redundancy |
|---|---|---|---|---|
| **4-plane Clos** | 3,072 | 131K | 1,048K | 4 planes |
| **WMP-PolarFly: 2 planes × 8-slice q=31** | 1,986 (−35%) | 127K | 508K (−52%) | 2 planes |
| **8-plane Clos** | 6,144 | 131K | 2,097K | 8 planes |
| **WMP-PolarFly: 4 planes × 8-slice q=31** | 3,972 (−35%) | 127K | 1,016K (−52%) | 4 planes |

### 7.3 WMP-PolarFly vs. Spritz

Spritz [13] is the closest intellectual sibling: both move routing intelligence to the endpoint on commodity Ethernet. They represent opposite ends of the topology-knowledge spectrum:

| Dimension | Spritz | WMP-PolarFly |
|---|---|---|
| Path discovery | Probe-based (ECN, trimming, timeout) | Algebraic (projective coordinates) |
| Topology knowledge required | None | Full coordinate assignment |
| Encapsulation | Standard Ethernet | SRv6 uSID |
| Path certainty | Probabilistic (cached, may be stale) | Deterministic (computed, always valid) |
| Topology scope | Agnostic (any low-diameter graph) | PolarFly-specific |
| Convergence on failure | Re-probing latency | Algebraic recomputation (instantaneous) |
| Setup latency | Probing time before steady state | Zero (computed at connection setup) |

### 7.4 Feature comparison

| Dimension | Advantage | RNG | WMP-PolarFly | Notes |
|---|---|---|---|---|
| Scale per port | — | Unbounded n | ~16K ToRs at 2×q=127 | Gap closed at ≥51.2T radix |
| Diameter / latency | WMP-PolarFly | Probabilistic (≈4–5 hops) | Deterministic 2 (L ≈ 2.6) | Gap grows with optics cost |
| Per-bit cost & power | WMP-PolarFly | 9–45% under Clos | Near Moore-bound floor | Advantage increases with bandwidth |
| Path diversity | — | High (spray), non-minimal | 1 SP + ~(q−1) NSPs per slice | Both adequate; different mechanisms |
| Transit ASIC state | WMP-PolarFly | LPM + wide ECMP groups | LPM only; paths in encap memory | Avoids ECMP table pressure |
| Control plane | WMP-PolarFly | Distributed protocol (Spraypoint) | IS-IS/BGP for liveness; paths algebraic | Spraypoint not public |
| Heterogeneity | RNG | Per-node degree mixing | Uniform per slice | Limited practical advantage |
| Incremental growth | — | Unquantized; break-and-splice | Additive to q ceiling; pre-planned | Different tradeoffs |
| Failure model | — | Continuous, statistical | Discrete → continuous with slicing/MRC | Parity at 4 slices |
| Multi-tenant | WMP-PolarFly | Not addressed | Combined transport + service uSID | Controller-free path computation |
| Operational model | RNG | Stateless fabric everywhere | Intelligence at encap node | The irreducible difference |
| Availability | WMP-PolarFly | Amazon-internal | Open standards (SRv6), open NOS | Deployable today |

---

## 8. Conclusions and Future Work

### 8.1 Conclusions

WMP-PolarFly demonstrates that the path-state objection to structured low-diameter fabrics is an artifact of tunnel-based forwarding, not a fundamental limitation. SRv6 uSID moves path state to the encap node; PolarFly's algebraic structure eliminates path-computation protocols; and MRC provides the transport-layer diversity mechanism that completes the architecture for AI training backends. The multi-tenant VPC overlay extends the architecture to general-purpose cloud, with on-demand algebraic path computation that eliminates the control-plane round trip traditional SDN overlays require.

At matched oversubscription on identical switch hardware, WMP-PolarFly matches RNG on switch count and optics while delivering half the hop count and deterministic diameter-2 latency. Against Clos, it eliminates the spine layer entirely, achieving 35–61% switch-count savings and up to 76% optics savings. Against Spritz, it trades topology generality for algebraic path certainty.

Unlike RNG and Spritz, WMP-PolarFly is built entirely on open standards and open-source NOS implementations, and is deployable today.

### 8.2 Future work

1. **Lab validation** at q=7 on docker-sonic-vs with Containerlab.
2. **MRC-on-PolarFly vs. MRC-on-Clos** collective completion-time distributions.
3. **Rigorous cost modeling** at matched endpoint populations.
4. **NCCL/RCCL plugin** for automated MRC EV provisioning via the PolarFly topology API.
5. **Multi-tenant validation** of combined transport + service uSID carriers at scale.
6. **Mixed-purpose multi-plane configurations** for internal fabric + DCI egress.

---

## References

[1] Bernardi et al., "Expanding into Reality: Random Graphs for Datacenter Networks," arXiv:2604.15261, 2026.
[2] Lakhotia et al., "PolarFly: A Cost-Effective and Flexible Low-Diameter Topology," SC22, arXiv:2208.01695.
[3] OpenAI et al., "MRC: Multipath Reliable Connection," OCP specification, May 2026.
[4] OpenAI et al., "Resilient AI Supercomputer Networking using MRC and SRv6," 2026.
[5] Besta & Hoefler, "Slim Fly: A Cost Effective Low-Diameter Network Topology," SC14.
[6] Valadarsky et al., "Xpander: Towards Optimal-Performance Datacenters," CoNEXT 2016.
[7] RFC 9256, "Segment Routing Policy Architecture," 2022.
[8] RFC 8986, "SRv6 Network Programming," 2021.
[9] Lakhotia et al., "PolarStar: Expanding the Scalability Horizon of All-to-All Networks," SC23.
[10] OpenAI, https://openai.com/index/mrc-supercomputer-networking/
[11] Zhou et al., "WCMP: Weighted Cost Multipathing for Improved Fairness in Data Centers," EuroSys 2014.
[12] Singla et al., "Jellyfish: Networking Data Centers Randomly," NSDI 2012.
[13] Bonato et al., "Spritz: Path-Aware Load Balancing in Low-Diameter Networks," arXiv:2602.19567, 2026.
[14] Dalton et al., "Andromeda: Performance, Isolation, and Velocity at Scale in Cloud Network Virtualization," NSDI 2018.

---

## Appendix A: Even-Characteristic Exclusion and Feasible-Degree Lattice

### A.1 Why q must be an odd prime power

The orthogonal polarity that defines ER_q degenerates in fields of characteristic 2. The bilinear form u₀v₀ + u₁v₁ + u₂v₂ = 0 yields a proper orthogonal polarity only in odd characteristic. In characteristic 2, the quadratic form x₀² + x₁² + x₂² = (x₀ + x₁ + x₂)²; the polarity becomes symplectic, every point is self-conjugate, and the graph loses C4-freeness. All powers of 2 are excluded.

### A.2 The feasible-degree lattice at high radix

The feasible set comprises odd primes and odd prime powers. Primes alone: 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, … never more than about 6 apart. Odd prime powers (49, 81, 121, 125, 169, 243, …) fill additional points. The lattice is dense enough that for any target radix above ~60, a feasible q lies within a few ports.
