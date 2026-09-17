# WMP-PolarFly: Weighted Multipath Routing on Algebraically Optimal Low-Diameter Datacenter Topologies

**Author:** Bruce McDougall, Cisco Systems

**Co-author:** Christian Martin, Cisco Systems

**Status:** DRAFT v3.0

**Date:** September 2026

---

## Abstract

Low-diameter topologies offer a compelling alternative to Clos fat trees for datacenter fabrics by eliminating spine layers and reducing switch count, optics, and per-bit power consumption. However, their adoption has been blocked by practical considerations around cabling complexity, lack of shortest-path ECMP, and the fact that k-shortest-path routing techniques that could compensate are generally not realized on commodity switch ASICs.

This paper presents **WMP-PolarFly** (Weighted Multi-Path Polarfly), a routing architecture that resolves these objections for the PolarFly topology. WMP-PolarFly uses SRv6 uSID source routing to steer traffic across a source-destination pair's **shortest path (SP)** and set of **next-shortest-paths (NSPs)** with algebraically derived weights. The SP and NSP set is computed directly from the PolarFly graph's projective-plane coordinates, requiring no path-computation protocol, no topology probing, and no transit forwarding state beyond plain LPM. We present deployment configurations spanning native high-bandwidth fabric links for both AI training clusters and general-purpose cloud, multi-tenant VPC overlays with combined transport and service uSID carriers, and physically separate PolarFly planes for first-hop switch redundancy. We compare WMP-PolarFly against Clos fat trees, Amazon's RNG random-graph architecture, and the Spritz sender-based load-balancing framework, and demonstrate that WMP-PolarFly matches or exceeds each on switch count, optics, and per-bit cost while delivering deterministic diameter-2 latency on open standards deployable today.

---

## 1. Introduction

### 1.1 The Clos scaling problem

Clos fat trees have dominated datacenter fabric design for over a decade, and for good reason: they provide non-blocking, high-bisection-bandwidth connectivity with a clean hierarchical structure. But that hierarchy comes at a cost. Spine and super-spine switches do not directly serve endpoints; they exist purely to aggregate and redistribute traffic. In a 3-tier Clos, roughly one-third of all switches and half of all fabric optics are consumed by these transit layers. Capacity is stranded structurally, and the cost scales superlinearly with endpoint count.

### 1.2 Low-diameter topologies as alternatives

Flat topologies, where switches interconnect directly with no aggregation layers, have promised an escape from the Clos cost curve for over a decade. The key insight: if every switch serves both endpoints and fabric, no switch is dedicated purely to transit. Examples include Jellyfish [12], which first demonstrated that random regular graphs could match Clos throughput at lower cost; Slim Fly [5] and Xpander [6], which showed that structured graphs could approach theoretical efficiency limits; and PolarFly [2], which achieved the first asymptotic match to the Moore bound at diameter 2, the theoretical maximum number of nodes for a given degree and diameter.

**Figure 1**: *The 10-node Petersen Graph is an intuitive low-diameter topology showing how any node can reach any other non-directly connected node via a single two-hop shortest path*

<img src=./images/figure-1.png width="400" height="400" alt="Figure 1">

The common obstacle blocking deployment of low-diameter topologies: they provide far fewer equal-cost shortest paths per endpoint pair than a Clos, starving standard ECMP of the path entropy it needs for effective load balancing. Prior solutions required either HPC-class adaptive routing hardware (UGAL) or abandoning structured topologies entirely in favor of random graphs (Amazon RNG/Spraypoint) [1]. This paper's thesis is that WMP-PolarFly is a lower-cost, more efficient alternative to Clos and other datacenter topologies, deployable today on open standards. The key enabler is relocating path intelligence from the fabric to the encap node: SRv6 source routing concentrates all path state in host memory while the transit fabric carries only minimal-state LPM entries, dissolving the forwarding-state objection that has historically blocked structured low-diameter topologies on commodity hardware.

### 1.3 Contributions

This paper makes five contributions:

1. **WMP-PolarFly architecture**: a weighted multipath routing design where the SP and NSPs are derived algebraically from PolarFly's projective-plane coordinates, with SRv6 uSID encapsulation concentrating path state at the encap node while transit switches carry only O(n) LPM entries.

2. **Encap/decap architecture**: an analysis of three encapsulation models — host-based encap with host decap (Model 1), host-based encap with egress-leaf decap (Model 2), and leaf-based encap with leaf decap (Model 3) — with a recommendation for Models 1 or 2, which place path state in abundant host DRAM rather than constrained switch or NIC memory. The choice of decap location (host or egress leaf) depends on use case and scale requirements.

3. **Multi-tenant VPC overlay**: a uSID carrier composition that combines transport path (SP/NSP) with tenant service function (uDT6) in a single SRv6 header, using on-demand algebraic path computation that eliminates control-plane consultation for per-flow path setup.

4. **Deployment configuration analysis**: an examination of PolarFly at various switch radixes and breakout configurations, showing how native high-bandwidth links serve AI backends while the same topology serves general-purpose cloud workloads via host-based weighted multipath.

5. **Comparative analysis**: quantitative comparisons against Clos, RNG, and Spritz at matched endpoint populations.

### 1.4 Paper organization

Section 2 presents PolarFly's topology foundations and the path diversity challenge. Section 3 develops the WMP-PolarFly architecture including encap/decap models, resilience, and multi-tenant considerations. Section 4 analyzes deployment configurations. Section 5 examines deployment scenarios for AI backend and general-purpose cloud. Section 6 provides comparative analysis against Clos, RNG, and Spritz. Section 7 concludes.

It should be noted, WMP-PolarFly architecture is built on standard Ethernet and SRv6 (RFC 8986 [8], RFC 9256 [7]), and is deployable today. Availability constraints of alternative architectures are discussed in Section 6.2.

---

## 2. PolarFly Topology Foundations

### 2.1 Construction and properties

A PolarFly [2] topology is defined by a single parameter **q**, which must be an odd prime or odd prime power. From q, three properties follow directly:

- **N = q² + q + 1** — the number of switches in the fabric
- **Fabric degree = q + 1** — the number of fabric-facing ports per switch
- **Diameter = 2** — the maximum number of hops between any two switches

The PolarFly network is built on a structured graph design (the Erdős–Rényi polarity graph) that dictates how these properties translate into physical wiring. Rather than using random layouts, every switch is assigned a unique 3-part coordinate identifier, and a direct link is established between any two switches whose coordinates satisfy a deterministic matching rule—essentially, a zero-mod-q dot product.

**Figure 2**: *A 57-node q = 7 PolarFly topology. Image credit Lakhotia et al.*

<img src=./images/figure-2.png width="400" height="400" alt="Figure 2">

For example, with q = 7 on a 16-port switch, 8 ports serve the fabric (degree q+1 = 8) and 8 serve endpoints, yielding a fabric of 7² + 7 + 1 = 57 switches from just 8 fabric uplinks each. PolarFly asymptotically reaches the Moore bound, the theoretical maximum node count for a given degree and diameter, exceeding 96% efficiency at practical radixes and 99% at q = 127. It is the most scale-efficient diameter-2 topology known. (See Appendix A for the odd-prime-power constraint and feasible-degree lattice.)

**Table 1: PolarFly fabric sizes at selected values of q**

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

For a given non-directly connected source-destination pair in a PolarFly fabric with parameter q:

- The **shortest path (SP)** is the unique 2-hop path through the pair's single shared neighbor, the relay node.
- The **next-shortest-paths (NSPs)** are 3-hop paths through intermediate nodes that are not the relay and whose paths do not share an edge with the SP. Each non-relay neighbor of the source can provide one edge-disjoint NSP, except when that neighbor is adjacent to the relay (forming a triangle whose candidate path would reuse the SP's final edge). This yields **q−1 NSPs for most pairs**, with a minority yielding q NSPs when no such triangle occurs.

For q = 7: **1 SP + 6 NSPs = 7 total forwarding paths** for most pairs. For q = 31: 1 SP + ~30 NSPs. For q = 127: 1 SP + ~126 NSPs.

**Figure 3**: *Node-1 to Node-34 in a 57-node q = 7 fabric: one SP and six NSPs*

### 3.2 Algebraic path derivation

The property that distinguishes WMP-PolarFly from generic source routing: **the SP and NSP set is algebraically derivable from endpoint coordinates**.

The SP relay between two non-adjacent nodes with coordinates A and C is the cross product A × C in GF(q), a single finite-field computation yielding the relay's coordinates directly. The NSPs are enumerated by iterating over A's remaining neighbors (excluding the relay and any triangle-adjacent neighbor) and computing their common neighbor with C.

**Worked example (q = 7).** Every switch has a 3-digit mod-7 address. Router A = (1, 0, 2) wants to reach C = (1, 4, 6). They are not adjacent (dot product = 6 ≠ 0). The SP relay B is the cross product: B = A × C mod 7, yielding one canonical projective point. The encap node emits the SRv6 segment list [uSID-B, uSID-C]. The same arithmetic enumerates 6 NSPs, each through a different first-hop neighbor, producing 6 additional three-SID segment lists.

**Control-plane consequence:** no path-computation protocol is required. A routing protocol such as IS-IS or BGP may be used to distribute node-SIDs and BFD may be used for liveness detection, but path discovery and calculation — the functions of RSVP-TE, PCE, or CSPF — are eliminated entirely. A local software agent on the encap node synthesizes the full SP + NSP segment-list set from the destination's coordinates alone.

### 3.3 SRv6 uSID encapsulation, state economics, and encap/decap models

SRv6 uSID is what makes WMP-PolarFly viable on commodity hardware. Each SP (2-hop) and NSP (3-hop) fits within a single uSID carrier, with no SRH required. Path state concentrates at encapsulation nodes as segment lists in host memory, while the transit FIB holds only the node-SID table and uA adjacency table: O(n), plain LPM.

The contrast with tunnel-based k-shortest-path routing is significant. In a tunnel-based implementation, each path through each transit router consumes one or more forwarding entries for label mappings, next-hop associations, and adjacency state. Even at a conservative estimate of one entry per path per router, q = 61 (3,783 switches, ~61 paths per destination) requires 61 × 3,783 ≈ **231K forwarding entries per router**, approaching the >300K IPv6 ALPM capacity of a Broadcom Tomahawk 5. Realistic implementations require multiple entries per path, pushing the total well beyond ASIC limits. At q = 127 the problem compounds to over a million entries regardless of the multiplier. SRv6 uSID bypasses the problem entirely: the transit FIB holds ~4K entries at q = 61 or ~16K at q = 127, regardless of how many paths the encap node programs.

**Three encap/decap models** determine where path intelligence and packet processing live:

**Model 1: Host encap, host decap.** The source host (CPU, DPU, or hypervisor) performs SRv6 encapsulation with segment lists computed algebraically and cached in host DRAM. The destination host decapsulates. This is the most general model, applicable to both AI training (MRC/RDMA) and multi-tenant cloud (VPC overlays). Because each destination host requires its own locator/uSID in the carrier, segment lists are per destination host. However, the transport portion of the segment list (the SP or NSP through the fabric) is per destination *switch* and shared across all hosts on that switch, so the source host caches transport prefixes per switch and appends the destination host's locator at encap time.

At q = 61 with 64 hosts per switch, a host communicating with all remote hosts would need segment lists for 3,782 remote switches × ~61 paths ≈ 231K transport prefixes, cached in host DRAM. The per-host suffix is a simple append. For AI training collectives, the NCCL/RCCL orchestrator can further limit the active working set to the subset of GPUs currently participating in the collective, keeping the active entry count proportional to the collective size rather than the full fabric.

**Model 1 in practice (iproute2 example at q=7).** On a Linux host attached to switch sw001, the route to hosts on remote switch sw019 (subnet 2001:db8:a013::/64) is a single weighted multipath entry with 7 nexthops: 1 SP at weight 4 and 6 NSPs at weight 1:

```
2001:db8:a013::/64 metric 1024 pref medium
  nexthop encap seg6 mode encap.red segs 1 [ fc00:0:1033:1013:e000:: ] weight 4
  nexthop encap seg6 mode encap.red segs 1 [ fc00:0:1002:100b:1013:e000:: ] weight 1
  nexthop encap seg6 mode encap.red segs 1 [ fc00:0:1009:1004:1013:e000:: ] weight 1
  nexthop encap seg6 mode encap.red segs 1 [ fc00:0:1017:101f:1013:e000:: ] weight 1
  nexthop encap seg6 mode encap.red segs 1 [ fc00:0:101e:101d:1013:e000:: ] weight 1
  nexthop encap seg6 mode encap.red segs 1 [ fc00:0:1025:1031:1013:e000:: ] weight 1
  nexthop encap seg6 mode encap.red segs 1 [ fc00:0:102c:1028:1013:e000:: ] weight 1
```

The SP carrier `fc00:0:1033:1013:e000::` encodes two uSIDs: relay sw051 (0x1033) and destination sw019's locator plus uDT function (0x1013:e000). The NSP carriers encode three uSIDs: first-hop, mid-node, and the same destination locator plus uDT. Transit switches process only node-SID LPM lookups. The destination host matches its locator, executes the uDT decap, and processes the inner packet.

Each host in this q=7 fabric holds 56 such routes (one per remote switch subnet), each with 7 weighted nexthops, for a total of 392 nexthop entries. At q=61 this grows to ~3,782 routes × ~61 nexthops ≈ 231K entries, entirely in host memory.

**Model 2: Host encap, egress leaf decap.** The source host encapsulates as in Model 1, but the segment list targets the destination *switch* rather than individual hosts. The egress leaf switch performs SRv6 decap (End.DT6 or uDT6), strips the outer header, and forwards to the local endpoint based on the inner destination address. Because routing targets switch subnets rather than individual hosts, the entry count drops by a factor of hosts-per-switch compared to Model 1. This model is useful when all hosts on a switch share a common subnet and the operator prefers simpler host addressing at the cost of a decap function on the egress switch.

**Model 3: Switch encap, switch decap.** The ingress switch encapsulates on behalf of the source endpoint. This is the traditional SR-TE model widely deployed in service provider transport networks, but it concentrates SR-policy entries in TCAM-constrained switches and thus does not scale as well as the host-based encapsulation models.

**Recommendation:** Models 1 or 2 for all deployment scenarios. Both place path state in host memory, scale naturally with host DRAM capacity, and align with the architecture's principle of host-based encap intelligence. The choice between them depends on the addressing model: Model 1 when destination hosts need individual locators (MRC, multi-tenant VPC), Model 2 when shared subnets per switch simplify addressing. Model 3 is available as a fallback where host-based encapsulation is not feasible. Subsequent sections of this paper assume host-based encapsulation, and all calculations are based on that assumption.

### 3.4 WMP weight computation

Traffic splits across the SP and NSP segment lists with explicit weights. The SP is more efficient (2 hops vs. 3), so it receives a premium, but the premium shrinks as q grows and the SP becomes one path among many.

At q = 7 (7 paths): a 30% SP, ~12% per NSP split is a reasonable starting point. At q = 127 (~127 paths): weights converge toward near-uniform, and the operator may treat all paths as ECMP. The weight is a derived function of q and hop-count ratio, not a constant, though operators can override it for specific traffic patterns.

The host computes segment lists on demand from coordinates and caches them for active connections. For each unique destination switch, the encap node holds one SP + ~(q−1) NSP segment lists. At q = 61, a host with active connections to 1,000 distinct remote switches caches ~61K segment lists, well within the memory capacity of modern host systems, DPUs, and SmartNICs. Multiple connections to the same destination switch reuse the same cached transport prefixes.

### 3.5 Live-vertex-set adaptation

In a partially deployed fabric, the SP relay between a live pair may not yet be installed. The encap node detects this from the installed-coordinate set and re-derives weights over the realized subgraph, with no protocol convergence required. This conditional weighting over the realized subgraph is, to our knowledge, novel, and enables PolarFly's purely additive expansion model (Section 4.3).

### 3.6 Resilience and failure handling

When a pair's SP relay fails, traffic undergoes a transition: 2-hop SP traffic shifts to 3-hop NSPs. The encap node re-derives weights algebraically from the updated live-vertex set, faster than any IGP reconvergence. If a link fails rather than a node, the encap node removes the affected path from the segment-list set and rebalances weights across the surviving paths.

Node liveness is detected via BFD (as discussed in Section 3.2). The key resilience property: because the full SP + NSP set provides ~q edge-disjoint paths between any pair, losing a single node or link affects only one path out of ~q. Traffic redistributes across the remaining paths with a weight adjustment, not a topology reconvergence. In MRC deployments, path-level failure handling moves to the transport entirely: MRC's per-path EV probing detects a dead path within one RTT-scale window and stops scheduling packets onto it, composing with the algebraic re-derivation at the host level.

---

## 4. Deployment Configurations

A 51.2T switch ships as a 64×800G device. It can be deployed at native port speeds or broken out to 128×400G, 256×200G, or other configurations. The choice of breakout determines the PolarFly parameter q, the number of server-facing ports, and the resulting fabric scale.

**Table 2: PolarFly configurations on a 51.2T switch**

| Configuration | Link speed | q | Fabric ports (q+1) | Server ports | Switches | Server attachment |
|---|---|---|---|---|---|---|
| 64×800G | 800G | 31 | 32 | 32 | 993 | 32 × 800G per switch |
| 128×400G | 400G | 61 | 62 | 66 | 3,783 | 66 × 400G per switch |
| 256×200G | 200G | 127 | 128 | 128 | 16,257 | 128 × 200G per switch |

Each configuration represents a single PolarFly topology with one fabric link per adjacency. Server-facing ports can be broken out independently to match endpoint NIC speeds (e.g., 400G server ports broken out to 4×100G for GPU connections) without affecting the fabric topology.

### 4.1 Native high-bandwidth links

For both AI training and general-purpose cloud, the optimal configuration uses native fabric links at the switch's highest practical port speed. At 128×400G with q=61, each switch has 62 fabric ports and 66 server ports, yielding 3,783 switches with 66 × 400G server attachment points each. MRC handles path diversity at the transport layer through per-packet spraying across the 1 SP + ~60 NSPs. For TCP/cloud workloads, host-based weighted multipath distributes flows across the same SP + NSP set.

### 4.2 Physically separate PolarFly planes

For deployments requiring first-hop switch redundancy, multiple physically separate PolarFly fabrics serve as independent planes. Each GPU or server NIC connects to multiple planes via separate ports, so a switch failure in one plane affects only that plane's connections.

**Table 3: Multi-plane configurations on 51.2T switches**

| Configuration | Planes | q | Switches/plane | Total switches | GPU attachment |
|---|---|---|---|---|---|
| 2 planes, 128×400G | 2 | 61 | 3,783 | 7,566 | 66 × 400G split across 2 planes |
| 4 planes, 64×800G | 4 | 31 | 993 | 3,972 | 32 × 800G split across 4 planes |

In a 4-plane configuration with q=31, each GPU's NIC is broken out to 4×100G with one port connecting to each plane's local switch. A switch failure in one plane leaves three surviving planes. Within each plane, the full SP + NSP path set (1 + ~30 paths per pair) provides transport-level diversity.

### 4.3 Additive expansion

PolarFly's complete edge set is known in advance from the algebraic construction. Expansion never breaks an existing link: a landing switch patches into q+1 pre-planned positions, and encap nodes algebraically recompute paths to incorporate the new vertex. The live-vertex-aware weight function (Section 3.5) handles partial deployment natively, maintaining WMP correctness throughout the build-out. The residual constraint: q is a day-1 ceiling, and growth beyond q²+q+1 switches requires a forklift to the next feasible q value.

### 4.4 Scale at modern radix

At 128×400G (q=61), a single PolarFly plane reaches 3,783 switches. At 256×200G (q=127), it reaches 16,257 switches at 99% Moore-bound efficiency. Both exceed the footprint of any known single datacenter building. The odd-prime-power constraint (Appendix A) excludes powers of 2 from the feasible set of q values, but the lattice of odd primes is dense enough at modern radix that a feasible q lies within a few ports of any target.

---

## 5. Deployment Scenarios

### 5.1 AI backend with MRC

The AI training backend is the deployment type where PolarFly's advantages compound: the fabric is built once at known size, the operator owns the stack end to end, hardware is uniform per build, and per-bit cost compounds directly into training economics.

MRC's properties map naturally onto WMP-PolarFly. Per-packet spraying across the full SP + NSP set eliminates elephant-flow collision risk. Algebraic path-set provisioning replaces fabric-dependent EV configuration with a direct computation at connection setup. NSCC's per-path congestion signals modulate the algebraic WMP weight priors adaptively. The 1–2μs SP/NSP latency gap (one additional switch traversal) is well within MRC's reorder window.

MRC's path-health probing and per-path congestion state are functions native to the MRC transport, fully decoupled from WMP-PolarFly's host state. MRC's probing runs identically regardless of the underlying topology. WMP-PolarFly adds only the algebraic segment-list computation, imposing no additional probing, no cache maintenance, and no background traffic.

Using Model 1 (host encap, host decap), the host computes and caches segment lists for remote switches in DRAM. For All-to-All collectives, MRC's dynamic EV management limits the active EV working set to the 128–256 EVs per source-destination pair specified by the MRC protocol, with the NCCL/RCCL orchestrator coordinating which destinations are active at any point. The working set remains proportional to the collective's active communication partners, not the full fabric size.

### 5.2 Multi-tenant cloud with VPC overlay

For general-purpose cloud and private cloud deployments with VPC isolation, WMP-PolarFly supports multi-tenant overlays using a combined transport + service uSID carrier. The SRv6 F3216 format (32-bit block prefix + up to 6 × 16-bit uSIDs) accommodates the full NSP path with tenant termination at the destination host:

**NSP carrier for host-terminated VPC:**
```
[first_hop_uSID | mid_uSID | dst_switch_uSID | dst_host_uSID | uDT6_tenant_func]
```

That is 5 active uSIDs consuming 5 of the 6 available F3216 slots, with the 6th slot serving as the zero-terminator. The SP case uses 4 active uSIDs with two slots free.

As a concrete example, an NSP carrier from a host on sw001 to the 64th host on sw019 in a tenant VPC might look like: `fc00:0:1002:100b:1013:a03f:e000::`, encoding first-hop (0x1002), mid-node (0x100b), destination switch (0x1013), destination host (0xa03f), and uDT6 tenant function (0xe000). Host locators can be reused at every switch since hosts connect directly to their local leaf; for example, if every switch has 64 attached hosts, locators a000 through a03f can be assigned identically at each switch.

**Where state lives in the multi-tenant model:**

- **Transit switches:** see only node-SIDs. FIB = O(n_switches). No per-tenant, per-host, or per-flow state. Transit switches perform uSID shift-and-forward based on the current active uSID, with no awareness of tenants or destination hosts.
- **Egress switch:** performs uSID shift-and-forward toward the destination host. No decap, no VRF lookup, no per-tenant state on the switch.
- **Destination host:** processes the final uSIDs (host locator + uDT6 tenant function), performs VRF-based decap, and delivers the inner packet to the appropriate VM or container.
- **Source host:** holds SR policy entries per (destination host × tenant) pair in host memory, computed algebraically on demand.

**On-demand flow computation.** Rather than pre-populating segment lists for all possible destinations, the source host maintains static state pushed at boot: a prefix-to-coordinate map (~4K entries for q=61) plus a tenant VRF-to-uDT6 function map (pushed per VM lifecycle event). Per-flow SR policy entries are computed on first packet to a new destination (algebraic path computation plus tenant suffix lookup, completed in microseconds with no network round trip) and cached for the flow's lifetime, aging out when idle. The working set is proportional to active flows, not total fabric size × tenant count.

This is architecturally similar to Google's Andromeda SDN stack [14], which also uses host-based encapsulation with on-demand flow installation. The critical difference: Andromeda's first-packet slow path requires a control-plane round trip to the Hoverboard system for encapsulation rules. WMP-PolarFly's first-packet path is purely local, because the host can algebraically compute the transport path from coordinates without consulting any controller. An SDN coordinator pushes only topology state (coordinates, SIDs, tenant mappings) to hosts; per-flow path computation is self-service.

The boundary between cloud and backend deployments is less sharp than it may appear. A fixed-footprint datacenter with a known build size and an operator-owned stack shares many characteristics with an AI training cluster, and WMP-PolarFly applies equally to both. The architecture's requirements are SRv6 encapsulation at the host and PolarFly coordinate assignment in the fabric; any environment that meets these is a candidate.

---

## 6. Comparative Analysis

### 6.1 WMP-PolarFly vs. Clos

The spine-elimination argument: a Clos dedicates a substantial fraction of its switches and optics to spine and super-spine layers that serve no endpoints. PolarFly is flat; every switch serves both fabric and server attachment. The savings are structural and grow with scale.

At q=31 on a 128×400G switch (32 fabric ports, 96 server ports, 3:1 oversubscription), PolarFly serves ~95K server ports from 993 switches. A 3-tier Clos serving comparable endpoints at the same oversubscription requires roughly 1,800 switches (leafs + spines + super-spines), with approximately twice the fabric optics. At q=61 (62 fabric, 66 server, ~1:1 oversubscription), PolarFly serves ~250K server ports from 3,783 switches, while a comparable Clos requires over 5,000 switches. In both cases, PolarFly achieves 40–60% switch-count savings and significant optics reduction by eliminating the transit-only tiers.

### 6.2 WMP-PolarFly vs. RNG

At matched oversubscription on the same switch hardware, WMP-PolarFly and RNG converge to identical switch count and fabric optics, because both are flat topologies where every switch serves endpoints. The differentiator is path quality and availability.

**At 3:1 oversubscription (128×400G switches, 32 fabric / 96 server):**

| Configuration | Switches | Server ports | Paths per pair | Hops |
|---|---|---|---|---|
| **RNG** | 993 | ~95K | ~32 edge-disjoint (spray) | 4–5 |
| **WMP-PolarFly q=31** | 993 | ~95K | 1 SP + ~30 NSPs | 2–3 |

The hardware is indistinguishable. The differences are hop count (2–3 vs. 4–5), path structure (deterministic algebraic vs. statistical spray), and availability. RNG is production-proven at Amazon but not publicly available: the Spraypoint protocol has not been open-sourced and ShuffleBoxes are not commercially available. A non-Amazon operator would need to reimplement Spraypoint and fabricate ShuffleBoxes independently. WMP-PolarFly builds on open standards (SRv6) and open-source NOS implementations (FRR, SONiC), and is deployable today.

**MRC backend comparison (128×400G switches, q=61):**

| Configuration | Switches | GPUs (at 8×100G) | Fabric optics | Paths per pair |
|---|---|---|---|---|
| **8-plane Clos** | 6,144 | 131K | 2,097K | ECMP per plane |
| **Single PolarFly q=61** | 3,783 (−38%) | ~125K | 234K (−89%) | 1 SP + ~60 NSPs |

The single-plane PolarFly comparison is dramatic: 38% fewer switches and 89% fewer fabric optics at comparable GPU count, because PolarFly uses native 400G fabric links (one optic per adjacency) while the Clos uses 8 planes of 100G links across leaf, spine, and super-spine tiers.

### 6.3 WMP-PolarFly vs. Spritz

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
| Host state | Empirical path cache (requires re-probing) | Deterministic function of coordinates (always current) |

Spritz's strength is generality: it works on any low-diameter topology without needing to know the graph structure. WMP-PolarFly's strength is certainty: the path set is a mathematical fact, not a discovery, so there is no probing phase, no stale-cache risk, and failure re-derivation is instantaneous. WMP-PolarFly's host state is a deterministic function of topology coordinates, always valid by construction, whereas Spritz maintains an empirical path cache that requires periodic re-probing to stay current. An operator choosing between them is choosing between topology-agnostic flexibility and topology-specific optimality.

### 6.4 Feature comparison

| Dimension | Advantage | RNG | WMP-PolarFly | Notes |
|---|---|---|---|---|
| Scale per port | — | Unbounded n | ~16K ToRs at q=127 | Gap closed at ≥51.2T radix |
| Diameter / latency | WMP-PolarFly | Probabilistic (≈4–5 hops) | Deterministic 2 (L ≈ 2.6) | Gap grows with optics cost |
| Per-bit cost & power | WMP-PolarFly | 9–45% under Clos | Near Moore-bound floor | Advantage increases with bandwidth |
| Path diversity | — | High (spray), non-minimal | 1 SP + ~(q−1) NSPs | Both adequate; different mechanisms |
| Transit ASIC state | WMP-PolarFly | LPM + wide ECMP groups | LPM only; paths in host memory | Avoids ECMP table pressure |
| Control plane | WMP-PolarFly | Distributed protocol (Spraypoint) | IS-IS/BGP for liveness; paths algebraic | Spraypoint not public |
| Heterogeneity | RNG | Per-node degree mixing | Uniform degree per fabric | Limited practical advantage |
| Incremental growth | — | Unquantized; break-and-splice | Additive to q ceiling; pre-planned | Different tradeoffs |
| Failure model | — | Continuous, statistical | Algebraic re-derivation to NSPs | Different mechanisms; both effective |
| Multi-tenant | WMP-PolarFly | Not addressed | Combined transport + service uSID | Controller-free path computation |
| Operational model | RNG | Stateless fabric everywhere | Intelligence at encap node | The irreducible difference |
| Availability | WMP-PolarFly | Amazon-internal | Open standards (SRv6), open NOS | Deployable today |

---

## 7. Conclusions and Future Work

### 7.1 Conclusions

WMP-PolarFly demonstrates that the path-state objection to structured low-diameter fabrics is an artifact of tunnel-based forwarding, not a fundamental limitation. SRv6 uSID moves path state to the encap node; PolarFly's algebraic structure eliminates path-computation protocols. The SP + NSP construct provides path diversity for any deployment type: for AI training backends, MRC enables per-packet spraying across the SP + NSP set with congestion-aware adaptive weighting; for general-purpose cloud, flow-level weighted multipath distributes traffic across the same path set using standard Linux routing. In MRC deployments, path-health probing and per-path congestion state are functions native to the MRC transport, fully decoupled from WMP-PolarFly's host state. The multi-tenant VPC overlay extends the architecture to general-purpose cloud, with on-demand algebraic path computation that eliminates the control-plane round trip traditional SDN overlays require.

At matched oversubscription on identical switch hardware, WMP-PolarFly matches RNG on switch count and optics while delivering half the hop count and deterministic diameter-2 latency. Against Clos, it eliminates the spine layer entirely, achieving 40–60% switch-count savings and significant optics reduction. Against Spritz, it trades topology generality for algebraic path certainty: zero probing latency, zero stale-cache risk, instantaneous failure re-derivation, and host state that is a deterministic function of coordinates rather than an empirical cache requiring periodic refresh.

Unlike RNG and Spritz, WMP-PolarFly is built entirely on open standards and open-source NOS implementations, and is deployable today.

### 7.2 Future work

1. **Lab validation** at q=7 on docker-sonic-vs with Containerlab, validating algebraic path computation, WMP weight distribution, and failure re-derivation end to end.
2. **MRC-on-PolarFly vs. MRC-on-Clos** collective completion-time distributions (allreduce, all-to-all) via simulation.
3. **Rigorous cost modeling** of WMP-PolarFly vs. Clos vs. RNG on switch count, optics, power, and total cost of ownership at matched endpoint populations.
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

The feasible set comprises odd primes and odd prime powers. Primes alone: 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127 … never more than about 6 apart. Odd prime powers (49, 81, 121, 125, 169, 243 …) fill additional points. The lattice is dense enough that for any target radix above ~60, a feasible q lies within a few ports.
