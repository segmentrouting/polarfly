# Structured Optimality vs. Engineered Randomness: 
## Weighted Multipath (WMP) Routing on PolarFly Topologies as an Alternative to Random-Graph Datacenter Fabrics

**Author:** Bruce McDougall, Cisco Systems

**Status:** DRAFT v0.6 — for internal review

**Date:** August 2026

---

## Abstract

Two flat datacenter topologies now offer credible alternatives to the classic CLOS fat tree: Amazon's RNG [1], a quasi-random expander fabric deployed in production with the Spraypoint routing protocol and ShuffleBox passive optical cabling; and PolarFly [2], a deterministic diameter-2 topology built on Erdős–Rényi polarity graphs that asymptotically reaches the Moore bound. The two designs embody opposite philosophies: RNG spends topology (longer paths, statistical guarantees) to keep per-hop routing stateless; PolarFly achieves near-optimal scale and path length but is conventionally held back by lack of shortest-path diversity and cabling complexity.

This paper argues that SRv6 source routing resolves the objections to structured low-diameter fabrics and proposes **WMP-PolarFly**: a weighted multipath routing design in which SRv6 segment lists and their traffic weights are derived algebraically from the polarity graph's projective-plane coordinates. We extend the design with multi-plane slicing of high-radix switches for path redundancy and operational flexibility. At current 51.2T radix, a quad-plane configuration (4×q=61) serves ~1M endpoints at diameter 2 with four edge-disjoint shortest paths per pair; a dual-plane configuration (2×q=127) reaches ~4M endpoints at 99% Moore-bound efficiency. We further show that the MRC transport [7] — already deployed with SRv6 on frontier AI training clusters — maps naturally onto PolarFly's algebraically enumerable path sets, enabling per-packet spraying with path-aware congestion control. We examine both topologies across deployment types and argue that the choice between them is primarily driven by operating model and culture.

---

## 1. Introduction

The fat tree's stark trade between cost and oversubscription is well documented: hierarchical structure pins traffic between endpoint pairs to small link subsets that congest while the rest of the fabric idles. Capacity is stranded structurally, not incidentally. Flat topologies — direct ToR-to-ToR interconnects with no aggregation or spine layers — have promised an escape for over a decade, but until 2026 no hyperscaler had deployed one in production.

That changed with Amazon's RNG (Resilient Network Graphs), now the default fabric for most new AWS datacenter builds. RNG validates the flat-topology thesis at production scale: 69% fewer routers, up to 33% higher throughput, 9–45% lower cost than equivalently oversubscribed fat trees. Its enabling contributions are a routing protocol (Spraypoint) that extracts near-degree edge-disjoint path counts from a quasi-random graph using only commodity ECMP, and a passive optical device (the ShuffleBox) that reduces random-graph cabling complexity to fat-tree levels.

RNG's authors frame randomness as the only practical route to a flat fabric, dismissing structured constructions (Slim Fly [5], Xpander [6]) on the grounds that k-shortest-path routing is required to achieve multi-path, but cannot be realized on commodity switch memory. **K-shortest-path routing** maintains multiple pre-computed forwarding paths (typically 4–16) between each pair of endpoints. Unlike standard ECMP, which distributes traffic across multiple paths of *equal* cost, k-shortest-path uses paths that may vary in length and metric — trading simplicity for richer load-balancing options at the cost of proportionally more forwarding table entries. This paper contests the RNG framing. The dismissal assumes hop-by-hop path state — MPLS tunnels, VRF multiplication, or conventional source-based forwarding — and does not consider compressed source routing. SRv6 uSID moves path state out of transit ASICs entirely: the encapsulation node holds the policy; transit nodes perform a single longest-prefix match on the uSID carrier. The forwarding-state objection, once removed, reveals that a Moore-bound-optimal structured graph holds per-bit efficiency and latency advantages that no random topology can match — and that these advantages compound with every silicon generation.

We develop this argument through PolarFly, the diameter-2 topology of Lakhotia et al., and a routing design we call **WMP-PolarFly (Weighted Multi-Path PolarFly)**. Section 2 reviews both topologies and explores the path diversity challenge all structured topologies face. Section 3 presents the routing design, including algebraic path derivation and principled weight selection. Section 4 introduces multi-plane slicing for high-radix switches. Section 5 examines scale at 51.2T/102.4T radix. Section 6 compares failure models. Section 7 — the backend case — integrates MRC packet spraying. Section 8 offers a side-by-side analysis and identifies the deployment types where each design wins.

A practical note: while RNG is production-proven at Amazon, it is not a publicly available solution. Spraypoint has not been open-sourced; the RNG paper describes the protocol's design but Amazon has not released code or a NOS implementation. ShuffleBoxes are custom passive optical devices with no known commercial source. A non-Amazon operator wishing to deploy RNG today would need to implement Spraypoint from the paper's description on their own NOS, fabricate or commission ShuffleBoxes, and validate the combined system — a substantial engineering investment. By contrast, WMP-PolarFly builds on open-source components (FRR, SONiC) and standard SRv6 as specified in RFC 8986 [7] and RFC 9256 [8].

> **[FIGURE 1 placeholder: side-by-side — generalized fat tree, RNG quasi-random graph, PolarFly ER_q structure for small q]**

---

## 2. Two Flat Topologies, Two Philosophies

### 2.1 RNG: engineered randomness

RNG interconnects routers as a quasi-random graph — a mix of randomized and deterministic cabling segments that reproduces the statistical properties of a true random graph, which is an asymptotically optimal expander. Physical ports are broken out into individual lanes (e.g., 400G into 4×100G), each forming an adjacency with a different remote router; degree *d* and node count *n* are free parameters, and heterogeneous degrees are supported natively.

Routing is Spraypoint: demand-oblivious, fully distributed, ECMP-only. The source "sprays" flows (not per-packet) across its full neighbor set (flow-level 5-tuple hashing; flows stay ordered and standard TCP/NICs are used), and traffic converges on the destination through *waypoint* levels, randomly selected neighbor sets fanning in toward the target. The construction yields a number of edge-disjoint paths close to the node degree, minimally overlapping across endpoint pairs, which is the source of RNG's capacity fungibility. The cost is path length: sprayed paths typically traverse 4–5 hops (1 spray hop to a random neighbor, then 2–3 additional hops via waypoint convergence toward the destination, plus the final hop), compared to PolarFly's worst case of 2 hops for SP and 3 hops for NSP. The RNG hop tax is accepted in exchange for diversity and statelessness.

Cabling uses ShuffleBoxes — passive optical devices that internally permute fiber connections, so that chained boxes at planned locations realize a quasi-random global topology with fat-tree-like physical cabling complexity. Critically, this is a *randomness-native* trick: the ShuffleBox works because RNG only needs the wiring's statistics to be right, not any specific edge set.

### 2.2 PolarFly: structured optimality

PolarFly is the first diameter-2 topology to asymptotically reach the Moore bound, exceeding 96% of theoretical peak at practical radixes — i.e., it packs nearly the maximum possible number of nodes for its degree and diameter. Every router pair is at most two hops apart allowing for flat topologies of very wide diameter. PolarFly also offers roughly 50% more feasible degrees than Slim Fly, the prior state of the art, and supports modular incremental growth through its cluster structure.

PolarFly connects N = q² + q + 1 routers (with q being an **odd** prime number or prime power) with fabric degree q + 1, as the Erdős–Rényi polarity graph ER_q derived from the projective plane PG(2, q). For example, with q = 7 on a 16-port switch, 8 ports go to fabric (degree q+1 = 8) and 8 to servers, yielding a fabric of N = 7² + 7 + 1 = 57 switches — 57 nodes from just 8 fabric uplinks each. (See Appendix A for further detail.)

### 2.3 The path diversity inversion

PolarFly's topology has a distinctive structural property: **no two routers in the fabric share more than one common neighbor**. This is what gives it exceptional scale — edges are never "wasted" on redundant two-hop paths — but it creates a routing challenge: between most pairs of routers that are not directly connected, there is only **one** shortest (2-hop) path. In networking terms, imagine a fabric where every source-destination pair has exactly one spine to go through; there is no second shortest path to hash onto.

This creates an irony: the very property that makes PolarFly the most efficient topology (maximum routers per port per hop count) simultaneously starves it of the path redundancy that load balancing / entropy depends on. Optimality and path diversity are structurally at odds, the closer a topology sits to the theoretical efficiency limit (the Moore bound), the fewer shortest paths it can offer per pair.

RNG begins from the same observation regarding structure-optimized topologies: shortest-path routing on any highly efficient topology will congest those singleton shortest paths. RNG's answer is to **abandon shortest-path routing entirely** and let the randomness of the graph supply diversity through longer, sprayed paths. PolarFly's conventional answer, inherited from the Slim Fly and Dragonfly HPC lineage, is non-minimal adaptive routing (UGAL-style), where switches sense congestion in real time and deflect traffic onto longer paths. But UGAL requires HPC-class adaptive-routing hardware; it is not available on commodity Ethernet ASICs running standard routing protocols.

SRv6 source routing is the third answer, and it changes the economics entirely.

---

## 3. WMP-PolarFly

### 3.0 The WMP concept: Shortest Path + Next-Shortest-Paths

The core of the WMP-PolarFly routing design is **Weighted Multi-Path (WMP)**: SRv6 source routing steers traffic across a source-destination pair's **shortest path (SP)** and a set of **next-shortest-paths (NSPs)** in an operator-configurable ratio.

For a given source-destination pair in a PolarFly fabric with parameter q:

- The **SP** is the unique 2-hop path through the pair's single shared neighbor (the relay node).
- The **NSPs** are the set of 3-hop paths through intermediate nodes that are *not* the relay — approximately q edge-disjoint alternatives whose exact count varies slightly for self-conjugate vertices.

For q = 7 this gives **1 SP + 6 NSPs = 7 total forwarding paths**. Each path is encoded as an SRv6 segment list (a uSID carrier, easily fitting in the IPv6 destination address with no SRH required). The operator assigns WMP weights across the set — for example, 40% of traffic over the SP and 10% over each of the 6 NSPs. As q increases, the NSP count grows roughly with q, providing increasingly rich path entropy: q = 31 yields ~1 shortest-path + 31 next-shortest-paths, q = 127 yields ~1 + 127 paths, and so on.

### 3.1 State economics: addressing the RNG critique

RNG's quantitative case against k-shortest-path routing: with n = 10K routers, k = 8 paths, and ~4 routers per path, tunnel-based implementations require on the order of 320K forwarding entries per router. Modern commodity switching ASICs offer substantially more forwarding capacity than the 4–16K range RNG's analysis cites — Broadcom Tomahawk 5 supports >300K IPv6 ALPM entries — but the k-shortest-path state problem scales with n² and grows with both fabric size and path diversity. Even at the practical production scale of q = 61 (3,783 routers), WMP-PolarFly uses ~62 paths per destination — a tunnel-based implementation would require approximately 62 paths × 3,783 destinations × ~3 entries per path ≈ **703K forwarding entries per router**, already exceeding TH5's 300K ALPM capacity. At the scale-ceiling configuration of q = 127 (16,257 routers, ~128 paths per destination), the number explodes to **6.2M entries per router**, well beyond any current or planned ASIC. The problem is not that ASICs are too small today; it is that tunnel-based path state scales in the wrong dimension.

SRv6 uSID restructures the problem entirely. Each SP and NSP segment list fits within a single uSID carrier. The SP + NSP set for all destinations concentrates at encapsulation nodes as O(k·n) segment lists in host or edge policy memory (which is cheap and abundant), while the transit FIB holds only the node-SID table and uA adjacency table: O(n), plain LPM, no per-path entries, no tunnels, no VRF multiplication. At q = 61, the transit FIB holds ~4K node-SID entries. Jump up to q = 127 and the transit FIB holds ~16K node-SID entries — well within any modern ASIC's capacity, with room to spare. The fabric ASICs remain **minimal-state**, arguably carrying less state than RNG's, since they bear no ECMP group pressure (Section 5.3). The intelligence relocates to the encap point, where memory is abundant and the computation is a direct formula that can be evaluated without any iterative algorithm or external lookup.

### 3.2 Algebraic path derivation

The property that elevates WMP-PolarFly beyond generic source routing on a low-diameter graph: **the SP and NSP set is algebraically derivable**. Vertices of ER_q are points of PG(2, q); adjacency is the polarity (orthogonality) relation. The unique common neighbor of two non-adjacent vertices — the relay node of the SP — is computable directly from their projective coordinates via finite-field arithmetic. The NSP set (on the order of q edge-disjoint 3-hop paths; total pair connectivity ≈ q + 1, with exact counts varying for the self-conjugate, degree-q vertices) is likewise enumerable from coordinates.

In practical terms: for any pair of routers in a q = 7 fabric, the topology guarantees exactly **1 SP** (2 hops through a single relay node) and approximately **6 NSPs** (3 hops each, through different intermediate nodes). The remarkable property is that *which* nodes serve as relays is computable directly from the routers' addresses — no routing protocol is needed to discover these paths. Here is how that computation works:

**Worked example (q = 7).** In a q = 7 WMP-PolarFly fabric — 57 routers, each with 8 fabric ports (or 7, for self-conjugate nodes) — every router has a 3-digit address in mod-7 arithmetic: its projective coordinate, e.g., (1, 3, 5). Two routers are directly cabled if the dot-product of their coordinates equals zero mod 7. Suppose router A = (1, 0, 2) wants to reach router C = (1, 4, 6). They are not directly connected (1·1 + 0·4 + 2·6 = 13 ≡ 6 mod 7 ≠ 0). To find the SP relay — the one common neighbor B — we solve for coordinates (b₀, b₁, b₂) such that A·B = 0 and B·C = 0 simultaneously, i.e., b₀ + 2b₂ ≡ 0 and b₀ + 4b₁ + 6b₂ ≡ 0, both mod 7. This is a system of two linear equations in projective space, yielding exactly one solution (up to scalar multiple): the relay node B. The encap node at A performs this computation — two inner products and a linear solve in mod-7 arithmetic — and emits the SRv6 segment list [uSID-B, uSID-C] for the SP. The same coordinate arithmetic enumerates the 6 NSPs for A→C, each via a different first-hop neighbor that is *not* the direct relay, producing 6 additional segment lists.

The control-plane consequence is significant: **no path-computation protocol is required in this design**. To be precise: running a base routing protocol (IS-IS or BGP) for node-SID distribution and liveness detection is certainly useful — it is best the fabric knows *which* routers are alive. The key point is, the functions traditionally performed by RSVP-TE, PCE, or CSPF — *discovering and computing paths* — are eliminated entirely. The encap node synthesizes the full SP + NSP segment-list set from the destination's coordinates alone. Where Spraypoint must compute and disseminate waypoint levels by protocol, WMP-PolarFly's paths are implicit in the topology's algebra. This is a built-in structural simplicity.

### 3.3 Weighted multipath (WMP)

Traffic between a source-destination pair splits across the derived SP and NSP segment lists with explicit weights: a fraction w_SP on the shortest path and (1 − w_SP) spread across the NSP set.

In plain terms: at small fabric sizes (low q), giving the SP a larger share of traffic makes sense — it is the most efficient path (2 hops vs. 3), and there are only a few NSP alternatives to spread across. As the fabric grows (higher q), the NSP count increases roughly with q, and each individual NSP carries proportionally less traffic. The optimal strategy shifts: spread more traffic across the larger NSP set, because concentrating on the single SP wastes the path diversity the topology provides. At q = 7, a 40/60 split (40% SP, 10% each across 6 NSPs) loads the SP at roughly 4× the per-path rate of each NSP — a reasonable allocation, since the 2-hop path consumes fewer link-traversals per bit. At q = 127, the SP is one path among ~128; the weight distribution converges toward near-uniform — perhaps ~2% SP and ~0.77% per NSP, or the operator may simply treat all 128 paths as ECMP and let the transport's per-path congestion feedback (Section 7.3) handle the minor hop-count difference adaptively.

We deliberately specify the weight as a **derived function, not a constant**. The optimal demand-oblivious split follows from the same capacity accounting underlying the Valiant/UGAL literature, and a single path's share of total pair capacity shrinks as 1/(q + 1). The weight formula is not a tuning knob the operator must guess at — though operators *can* override it for specific traffic patterns.

A note on encap-node memory: the NIC does not need to hold pre-computed segment lists to all destinations simultaneously. Because the SP and NSP paths are algebraically derivable from coordinates (Section 3.2), the NIC computes segment lists on demand — a few arithmetic operations per destination — and caches them for active connections. A NIC maintaining 1,000 active connections at q = 61 holds ~62K segment lists, well within the memory capacity of modern frontend DPUs and backend SmartNICs (ConnectX, Pollara, and similar). The computation is lightweight enough to run at connection-setup time without measurable latency impact.

The weight function takes as inputs: q; the path-length ratio (2 vs. 3 hops); the pair type (Section 3.4); and — critically for incremental deployment — the **live-vertex set**. In a partially built fabric, the SP relay between a live pair may not yet be installed; the encap node detects this from the installed-coordinate set and re-derives weights over the realized subgraph, again with no protocol convergence. Conditional weighting over the realized subgraph is, to our knowledge, novel.

> **[FIGURE 2 placeholder: WMP weight as a function of q; SP vs. per-NSP load curves]**

### 3.4 What RNG retains

**Heterogeneous router degrees.** RNG supports switches with different port counts in a single fabric. If a new-generation switch has 64 ports and the existing fleet has 32, the new switch simply takes more neighbors — the random graph's statistical properties degrade gracefully rather than breaking. In principle, operators can also vary the server-to-fabric port ratio per switch. In practice, the RNG paper does not quantify how path diversity and Spraypoint's load-balancing guarantees degrade as the degree distribution becomes uneven — a heavily lopsided mix (some switches at degree 16, others at degree 64) would weaken expansion properties for the low-degree nodes even though the graph remains connected and routable. WMP-PolarFly is not as flexible: it requires uniform fabric degree (all nodes in a given plane share the same q value, which determines their fabric port count) within each plane. The multi-plane slicing described in Section 4 provides a coarser but operationally cleaner heterogeneity model via generational plane separation.

**Unquantized sizing and continuous growth.** RNG can be built at any node count *n* — a fabric could be 2,673 nodes, it could be 8,001, whatever the building needs. PolarFly is quantized to q² + q + 1 for the available odd prime powers, and growth beyond the chosen q is a forklift. However, at modern radix this constraint is mild, as the following table shows:

| q | Fabric degree (q+1) | Switches (q²+q+1) |
|---|---|---|
| 7 | 8 | 57 |
| 31 | 32 | 993 |
| 61 | 62 | 3,783 |
| 127 | 128 | 16,257 |
| 251 | 252 | 63,253 |

Partial deployment within a chosen q is additive (Section 4), but the maximum WMP-PolarFly fabric size is locked to the math, and the operator must pick q at design time and live with the ceiling.

**Stateless operational philosophy.** RNG's transit routers hold destination-based LPM and ECMP groups — the same state any IP router carries. There are no policies, no segment lists, no per-pair configuration anywhere in the fabric. The fabric cannot be misconfigured because it holds no per-path configuration to get wrong (RNG still requires routable address assignment across multi-hop paths; the misconfiguration immunity refers to the absence of per-path forwarding state). WMP-PolarFly concentrates correctness in the encap-node policy computation. The computation is algebraically deterministic (Section 3.2), but it *is* computation — and the encap node must be right. RNG spends topology to keep routing minimal-state; WMP-PolarFly spends routing intelligence to keep topology optimal.

---

## 4. Multi-Plane Slicing

When a switch has more physical ports than a single PolarFly plane requires, the surplus ports can serve additional planes — trading some per-plane scale for path redundancy, increased bisection bandwidth, and operational flexibility.

For reference, the following table shows PolarFly fabric sizes at selected values of q:

| q | Type | N = q²+q+1 (switches) | Fabric degree (q+1) | Notes |
|---|---|---|---|---|
| 7 | prime | 57 | 8 | Lab validation target |
| 31 | prime | 993 | 32 | Multi-plane on 64-port or 512-port |
| 61 | prime | 3,783 | 62 | Quad-plane on 512-port (51.2T) |
| 127 | prime | 16,257 | 128 | Dual-plane on 512-port (51.2T); Quad-plane on 1024-port (102.4T) |
| 251 | prime | 63,253 | 252 | Dual-plane on 1024-port (102.4T) |

### 4.1 Dual-plane and quad-plane configurations

On a 51.2T switch with 512×100G ports, the operator chooses how to partition between fabric and server attachment. Two configurations merit detailed comparison:

**Initial production configuration: Quad-plane 512×100G radix (4×q=61).** Each switch allocates 4×62 = 248 ports to fabric (62 per plane) and 264 ports to server attachment. This yields 3,783 switches with ~1M server attachment points — sufficient for the largest datacenter buildings in production today — and leveraging four independent PolarFly planes. Every source-destination pair enjoys **4 edge-disjoint SPs** (one per plane) plus 4×~61 NSPs ≈ **248 total forwarding paths**. The four-plane redundancy delivers exceptional failure resilience (any single plane failure is a weight rebalance among three surviving same-length SPs, not a hop-count transition), and the per-relay incast under All-to-All is manageable at ~61 flows per relay per plane (and similarly beneficial for cloud fan-in/incast patterns where many clients converge on a single service endpoint).

**Scale-ceiling configuration: Dual-plane 512×100G (2×q=127).** Each switch allocates 2×128 = 256 ports to fabric (128 per plane) and 256 to server attachment. This yields 16,257 switches with ~4M server attachment points — well beyond any single building in production — across two planes with **2 SPs + ~254 NSPs per pair**. The 99% Moore-bound efficiency at this radix makes it the most port-efficient flat topology achievable at diameter 2.

Both configurations share the same physical switches; the choice is a design-time decision about where to spend the port budget. The 4×q=61 configuration trades scale for more SPs and significantly better failure properties, making it the natural recommendation for production deployments. The 2×q=127 configuration demonstrates that PolarFly can match any building-scale requirement — the scale objection against structured topologies no longer applies at modern radix. For AI backend fabrics (Section 7), where cluster sizes are typically 1–4K switches, even 2×q=31 (993 switches, dual-plane on modest radix) may suffice — or on a 51.2T switch, 8×q=31 (8×32 = 256 fabric ports, 256 server ports, yielding 993 switches with ~254K server attachment points and 8 SPs + ~31 NSPs per pair), with exceptional path diversity.

**A note on plane isolation.** In multi-plane configurations on shared physical switches, the "planes" are logical partitions of the same hardware — two adjacent switches in a 4×q=61 fabric have four parallel 100G links between them, one per plane. Plane isolation is enforced by the SRv6 data plane: each plane's paths use distinct uA (adjacency) SIDs bound to specific physical interfaces, so a segment list for plane-2 resolves at each transit hop to the plane-2 egress link specifically. Without per-plane uA SIDs, nothing prevents cross-plane leakage. Operators who prefer strict failure-domain isolation should enforce per-plane uA binding; operators who prefer maximum path diversity may choose to relax isolation and let the encap node spray across all four links as a wider path set. Both modes are valid and the choice is operational, not topological.

What multi-plane slicing buys, regardless of configuration:

**Minimal-path redundancy.** Every pair holds one SP per plane. With 4 planes, a single-plane failure leaves 3 surviving SPs at identical hop count — no RTT shift, just a weight rebalance. This substantially closes the gap against RNG's continuous failure model (Section 6).

**Additive expansion.** Because the complete edge set of each plane is known in advance, growth never breaks an existing link: a landing router patches into q + 1 pre-planned positions per plane. With pre-provisioned passive patch frames carrying the polarity-graph permutation — the structured analogue of the ShuffleBox, though it must encode the *specific* edge set rather than a blind permutation — PolarFly expansion is arguably cleaner than RNG's break-and-splice appendix. The residual costs: q is a day-1 ceiling (the next odd prime power is a forklift), and the partial graph's path multiplicity is nonuniform, which the live-vertex-aware weight function of Section 3.3 absorbs.

### 4.2 Beyond dual-plane: multi-plane membership and the intersection property

Section 4.1 describes multi-plane configurations where every switch participates in all planes on the same physical hardware. This subsection considers a different model: **physically separate PolarFly fabrics** where each switch joins only a subset of available planes, and different planes may use different switch populations or hardware generations.

When slicing beyond 2 planes on the same vertex set, the number of planes a switch participates in determines the fabric's diameter guarantee. In the configurations of Section 4.1, every switch participates in *all* planes simultaneously (all 4 in 4×q=61, both in 2×q=127), which trivially preserves diameter 2 — every pair shares every plane. But as radix grows further, an operator might want more planes at lower per-plane degree, and it becomes impractical for every switch to join every plane. The question then is: if each switch belongs to only *some* planes, can we still guarantee diameter-2 reachability?

The answer depends on a simple combinatorial property: **any two switches must share at least one plane in common** — the same way any two people who each speak 2 out of 3 languages will always share a language they can converse in. If each switch belongs to 2 out of p = 3 planes, this property holds: any two 2-subsets of {A, B, C} necessarily overlap. Some pairs share two planes and enjoy dual SPs; others share exactly one plane and have a single SP. The pair type — which planes two switches share — is simply two more coordinates in the address, so the WMP weight derivation remains a direct formula. As a concrete example, 3×q=83 on a 512-port switch (3×84 = 252 fabric ports, 260 server ports, ~7,000 switches) with 2-of-3 membership would preserve diameter 2 globally while providing a middle ground between the 4×q=61 and 2×q=127 configurations.

At **p ≥ 4** with partial membership, the intersection guarantee breaks: two switches belonging to planes {A,B} and {C,D} share no common plane and must transit a bridging switch, raising diameter to 4. At this point the partial-membership constructions become effectively hand-rolled star products, and the honest comparison is no longer against vanilla PolarFly but against **PolarStar** [9] (the diameter-3 star product of ER_q with Paley or inductive-quad graphs — the literature's answer to scaling past q² + q + 1) and BundleFly. Our expectation, to be validated: PolarStar wins on scale-per-port; multi-plane slicing wins on plane-granular heterogeneity and operational modularity.

Multi-plane slicing also admits mixed-purpose configurations — for example, 3 internal fabric planes plus 1 DCI/egress plane at a different q — though the cross-plane routing implications of such designs are deferred to future work.

> **[FIGURE 3 placeholder: multi-plane membership diagram showing p=3 and p=4 configurations; pair-type path multiplicity table]**

---

## 5. Scale at Modern Radix

### 5.1 The Moore ceiling moves above building size

Radix growth is asymmetric between the two designs: it repairs PolarFly's largest weakness while only marginally improving RNG's position.

The two configurations described in Section 4.1 — 4×q=61 at ~4000 switches and ~1M endpoints, and 2×q=127 at ~16k switches and ~4M endpoints — both exceed the footprint of any single datacenter building in production today.

The odd-prime-power constraint (Appendix A) means that powers of 2 — including 64, 128, 256, 512 — are excluded from the feasible set of q values. However, the lattice of odd primes and odd prime powers is dense enough at modern radix that a feasible q lies within a few ports of any target (61 is close to 64), and both classical objections to PolarFly — quantization and the q² ceiling — cease to be practical constraints at current-generation silicon.

### 5.2 Per-bit economics compound with bandwidth

Fabric capacity consumed per delivered bit is proportional to hop count. The WMP mix runs at roughly L ≈ 2.6 effective hops (weighted across 2-hop SP and 3-hop NSP sets); Spraypoint's spray-plus-waypoint structure runs meaningfully longer — typically 4–5 hops. At 100G lanes this isn't trivial; at 200G per lane and beyond, each extra hop is another traversal of increasingly expensive and power-hungry optics and serdes. A near-Moore fabric at L ≈ 2.6 sits close to the information-theoretic floor of fabric-capacity-per-delivered-bit. RNG's cost case is "up to 45% cheaper than fat tree" — but the fat tree is a soft target; against a Moore-optimal structured fabric, RNG's hop tax becomes an economic consideration, and it grows in absolute dollars and watts with every silicon generation. The structured topology's advantage here strengthens with scale.

WMP-PolarFly's cost advantage over fat tree has not yet been rigorously modeled, but the directional argument is strong: a 4×q=61 configuration serves ~1M endpoints with 3,783 total switches at L ≈ 2.6 hops, versus a 3-tier Clos serving the same population with substantially more switches at 4–6 hops per path. The switch-count and per-bit-hop savings should match or exceed RNG's reported 9–45% cost advantage over fat tree — and PolarFly's lower hop count (2.6 vs. 4–5) suggests the per-bit advantage may be larger. Rigorous cost modeling is a future-work item (Section 9).

### 5.3 RNG's pressure points at large flat scale

RNG has no topological ceiling, but three practical pressures emerge at large scale. First, the control plane: Spraypoint is a distributed protocol over a flat domain with no hierarchy; dissemination and convergence behavior at thousands of nodes under churn is an open question. Second, ECMP hardware: spraying across the full neighbor set implies ECMP groups approaching the lane count, and ASIC ECMP member tables are a finite, contested resource — 512-wide groups per destination class is real pressure even with group sharing. WMP-PolarFly sidesteps this entirely: explicit paths consume encap-node policy memory, not transit ASIC tables. Third, expansion recabling complexity scales with d: at d = 512, every rack land touches 256 existing links spread across the building. None of these is fatal, but all worsen with radix, while WMP-PolarFly's additive pre-planned algebraic expansion improves relatively.

---

## 6. Failure Models: Statistical Headroom vs. Repair Logic

RNG's resilience claim is best understood as a claim about *blast-radius shape*, and a precision matters: Spraypoint absolutely reacts to failure — it is a routing protocol in the OSPF/BGP mold and reconverges on topology change. What RNG eliminates is *protection machinery*: no FRR, no precomputed backups, no TI-LFA-style repair, because steady-state forwarding already encodes the redundancy. When a link dies, the adjacent router locally prunes the member from its ECMP groups and traffic redistributes in the data plane instantly; the failed link carried roughly 1/d of any affected pair's capacity, so the loss is a thin statistical shave across many pairs rather than a mode change for any one. There are no special routers; every failure is small and uniform. Protocol convergence cleans up in the background with nothing waiting on it.

Single-plane PolarFly, by contrast, undergoes a discrete transition when a pair's unique SP dies: 2-hop traffic steps to the 3-hop NSP set, with an RTT shift congestion control will notice. The response is fast — the encap node re-derives weights algebraically, arguably faster than any IGP floods — but it is a *reaction*, with a detectable before/after. Multi-plane slicing (Section 4.1) converts the transition from a length change into a weight rebalance among length-identical SPs on surviving planes, substantially closing the gap. In the recommended 4×q=61 configuration, losing one plane's SP still leaves 3 same-length SPs — no hop-count transition at all. In the backend deployment of Section 7, MRC moves failure handling into the transport entirely.

The honest framing for operators: PolarFly offers deterministic best-case behavior with discrete failure modes; RNG offers probabilistic behavior with continuous failure modes. Preference depends on whether the workload fears tail latency or fears variance.

---

## 7. The AI Backend: MRC and Packet Spraying on PolarFly

### 7.1 Why the backend is the natural home

RNG's authors explicitly scope to multi-tenant general-purpose fabrics and defer AI training, noting that such workloads may demand rail-optimized structures and local capacity islands that flat random topologies lack. The backend is simultaneously the deployment type where every PolarFly disadvantage evaporates: the fabric is built once at known size, the operator owns the stack end to end, the hardware population is uniform per build, and per-bit cost and power compound directly into training economics (Section 5.2). Collective-driven traffic additionally rewards deterministic path lengths: flow-completion-time skew across parallel transfers gates the collective, and a hard diameter-2 bound with enumerable path lengths is precisely the property a scheduler can reason about.

What the structured Ethernet fabric has historically lacked in this deployment type is a transport that can exploit its path set. With MRC that transport now exists.

### 7.2 MRC in brief

MRC (Multipath Reliable Connection), contributed to OCP in May 2026 by OpenAI with AMD, Broadcom, Intel, Microsoft, and NVIDIA, extends RDMA-over-Ethernet semantics so that **a single RDMA connection distributes traffic across multiple network paths**, with reordering tolerated by the transport and congestion managed per path (AMD's NSCC algorithm, now part of the UEC congestion-control specification). It is implemented on shipping 400/800G NICs (ConnectX-8, Pollara, Vulcano, Thor Ultra) with **SRv6 switch support** on Spectrum-4/5 (Cumulus, SONiC) and Tomahawk 5 (EOS), and is deployed in production on OpenAI's largest GB200 clusters (OCI Abilene, Microsoft Fairwater) [10]. Cisco Silicon One G200 also supports SRv6 but has not yet appeared in production MRC deployments. The companion paper is explicitly titled "Resilient AI Supercomputer Networking using MRC and SRv6." Reported topology practice mirrors the breakout philosophy: rather than one 800G link, the NIC is split into multiple smaller links to create natural path redundancy, enabling two-tier builds at 100K+ GPU scale with roughly two-thirds the optics and 40% fewer switches than three-tier baselines.

Three properties matter for our purposes. MRC is **reorder-tolerant**, so per-packet (or per-message-slice) spraying is admissible where general purpose cloud requires per-flow distribution. MRC is **path-aware**, maintaining per-path state and congestion signals within one connection. And MRC's deployed path-steering mechanism **is already SRv6** — the same encapsulation substrate as the WMP-PolarFly design.

### 7.3 The synthesis: per-packet WMP over algebraic path sets

Recall why WMP was specified at flow level (Section 3.3 context): general-cloud tenants run vanilla TCP on stock NICs, and per-packet spraying would have required reorder-tolerant transports that cannot be assumed across an adversarial tenant population. The backend inverts the assumption — every endpoint is an MRC-capable RDMA NIC — and the design strengthens along four axes.

**Spraying granularity.** The WMP weights of Section 3.3 apply per packet rather than per flow. Elephant-flow collision risk — the residual weakness of any flow-hashed scheme, RNG's included — vanishes: a single connection's load spreads across the full SP + NSP set in proportion to the derived weights. This is, notably, a capability RNG's general-cloud deployment does not have; Spraypoint sprays flows, not packets.

**Path-set provisioning.** MRC requires each connection to be provisioned with a set of paths (EVs or Entropy Values). On a Clos this set is implicit (ECMP up, ECMP down); on PolarFly it is *explicit and enumerable* — exactly q + 1-ish edge-disjoint segment lists per pair, synthesized from projective coordinates with no path discovery protocol. PolarFly converts MRC's path-set abstraction from a fabric-dependent configuration burden into a direct algebraic computation at connection setup. The diameter-2 bound additionally caps the path-length spread within a connection's set at one hop (2 vs. 3), simplifying the transport's reordering and completion-tracking window relative to a random graph's longer-tailed length distribution.

**SP/NSP latency differential and MRC reorder tolerance.** A natural question arises: can MRC handle the latency difference between 2-hop SPs and 3-hop NSPs within the same connection? The answer is yes — MRC's reorder tolerance is designed for arbitrary path-length variation, and NSCC maintains separate congestion state per path, naturally adapting to per-path RTT differences. At datacenter scale, the SP-vs-NSP latency gap is on the order of 1–2μs (one additional switch traversal), well within MRC's reorder window. At high q, where the SP is one path among ~128, the practical approach is to treat all paths as near-equal and let NSCC's per-path feedback handle the minor latency difference adaptively. At low q (e.g., q = 7, where the SP carries a meaningful weight premium), MRC's per-path RTT tracking inherently schedules more aggressively onto the faster SP — the WMP weight priors and NSCC's adaptive feedback reinforce each other.

**Adaptive weighting.** NSCC's per-path congestion signals provide the feedback channel that pure demand-oblivious WMP lacks. The static algebraic weights become *priors*, modulated at the NIC by per-path congestion state — UGAL-like adaptivity realized at the transport rather than in switch hardware, on commodity Ethernet ASICs. The lineage is satisfying: PolarFly's original authors assumed HPC-class adaptive routing in switches; MRC relocates exactly that function to the place the backend operator controls.

**Failure handling.** MRC's headline operational result — switch reboots during frontier training runs without job disruption — derives from per-path health tracking: the transport stops scheduling onto a dead path within one RTT-scale detection window. On PolarFly this composes with algebraic re-derivation: the NIC's transport masks the failure instantly; the encap layer re-synthesizes the path set from the updated live-vertex set in the background; no IGP convergence sits anywhere on the critical path. The discrete-transition concern of Section 6 is fully addressed in this deployment model — the surviving paths in the MRC set absorb the weight shift per packet, and multi-plane slicing (where used) makes even the length distribution invariant.

> **[FIGURE 4 placeholder: MRC connection over PolarFly — one SP + q NSP segment lists, per-packet weighted spray, NSCC feedback loop]**

### 7.4 Positioning against MRC's deployed topologies and against RNG

MRC is topology-agnostic and its production deployments to date run on two-tier rail-style Clos fabrics. The proposal here is therefore not MRC-versus-PolarFly but MRC-*on*-PolarFly as the structured direct-topology alternative to MRC-on-Clos: diameter 2 instead of 4-hop worst-case through a spine, ~99% Moore efficiency instead of Clos port overheads, and a path set the transport can enumerate algebraically. The breakout philosophy is shared — MRC deployments already split NICs into multiple lower-rate links for path redundancy, which is precisely the lane-level adjacency model PolarFly's degree budget wants. On the other hand RNG's authors generally concede it is not a great match to collective-driven traffic. A quantitative bake-off — MRC-on-PolarFly vs. MRC-on-Clos at matched port count, on allreduce/all-to-all completion-time distributions — is the natural next experiment and an open invitation in this paper.

### 7.5 All-to-All collectives and bisection bandwidth

All-to-All is the adversarial traffic pattern for any topology: O(n²) simultaneous flows, uniform demand across every pair. Under full All-to-All, every link in any non-blocking fabric saturates simultaneously, and no topology — Clos, RNG, or PolarFly — escapes bisection-bandwidth limits. The question is not whether PolarFly saturates but how it compares at matched cost.

PolarFly's near-Moore structure gives it close to optimal bisection bandwidth for its degree and node count — structurally higher than a Clos at matched port investment, because Clos strands capacity in its tree hierarchy.

Separately, PolarFly's hop-count advantage compounds under All-to-All: a diameter-2 fabric with L ≈ 2.6 effective hops consumes roughly half the link-traversals per delivered bit compared to Spraypoint's 4–5 hop paths, meaning PolarFly delivers more aggregate throughput from the same total link budget. This is the per-bit economics argument of Section 5.2 applied to the worst-case traffic matrix.

The practical concern is not aggregate throughput but **incast at individual switches**: in All-to-All, each router receives traffic from all N−1 peers simultaneously. On PolarFly, roughly q+1 of these arrive via direct (1-hop) links, while the remaining ~q² arrive via 2-hop paths through q+1 relay neighbors. Each relay therefore concentrates traffic from ~q senders, creating per-relay load of ~q flows. In the recommended 4×q=61 configuration, this means ~61 concurrent inbound flows per relay per plane — manageable, and spread across 4 independent planes. MRC's per-path congestion control (NSCC) provides the backpressure mechanism, and the WMP weights can be adjusted to spread load across the NSP set when relay congestion is detected. This adaptive rebalancing under All-to-All load is a natural target for simulation validation in the q = 7 lab environment.

---

## 8. Scorecard and Conclusions

| Dimension | Advantage | RNG (quasi-random + Spraypoint) | WMP-PolarFly (incl. slicing) | Notes |
|---|---|---|---|---|
| Scale per port | — | Unbounded n | ~16K ToRs / ~4M ports at 2×q=127 | Gap closed at ≥51.2T radix; neither side wins decisively |
| Diameter / latency | WMP-PolarFly | Probabilistic, longer (≈4–5 hops) | Deterministic 2 (L ≈ 2.6 effective) | Gap grows with optics cost |
| Per-bit cost & power | WMP-PolarFly | 9–45% under fat tree | Near Moore-bound floor | Compounds with bandwidth |
| SP diversity | WMP-PolarFly | High (spray), non-minimal | 1 SP per plane; 4 planes ⇒ 4 SPs | Slicing closes gap; MRC addresses residual |
| Transit ASIC state | WMP-PolarFly | LPM + wide ECMP groups | LPM only; paths in encap memory | Avoids ECMP table pressure |
| Control plane | WMP-PolarFly | Distributed protocol (Spraypoint) | IS-IS/BGP for liveness; paths algebraic | No path-computation protocol |
| Heterogeneity | RNG | Per-node degree mixing, in place | Uniform per plane | Modern DC builds use uniform hardware, limiting practical advantage |
| Incremental growth | RNG | Unquantized; break-and-splice | Additive to q ceiling; pre-planned | Different shapes; PolarFly cleaner per step |
| Failure model | — | Continuous, statistical, no protection | Discrete → continuous with 4-plane slicing | Parity at 4 planes; RNG edges single-plane |
| Operational philosophy | RNG | Stateless fabric, minimal-state everywhere | Intelligence concentrated at encap | The irreducible difference |
| Availability | WMP-PolarFly | Amazon-internal; not open-sourced | Open standards (SRv6), open NOS (SONiC/FRR) | Deployable today vs. requires reimplementation |

The two topology families do not converge with scale; they sort by operating model. **Engineered randomness has its advantages in the elastic-fleet (Cloud) deployment**: daily rack lands, rolling hardware generations, adversarial multi-tenant traffic, and an operational culture that prizes a fabric incapable of holding misconfiguration. **Structured optimality has the advantage in deliberate-fabric (AI backend) deployments**: build-once footprints, operator-owned stacks, per-bit economics that compound, and workloads — above all AI training collectives — that reward deterministic latency and enumerable paths. Modern radix removes scale as a discriminator; SRv6 removes the forwarding-state objection; MRC removes the transport objection. What remains is a genuine philosophical choice about where complexity should live, and the thesis of this paper is that for the backend, the answer has quietly become the encap node — a conclusion that aligns with a broader industry trend toward host-based policy execution, visible across cloud-native networking, SmartNIC offload architectures, and now MRC. The boundary between these deployment types is less sharp than the literature implies: a fixed-footprint cloud datacenter — a sovereign build, a large enterprise private cloud, a neocloud region — shares many characteristics of the deliberate-fabric deployment, and WMP-PolarFly is a legitimate candidate there as well.

RNG's published case is argued against the fat tree, and its dismissal of structured alternatives does not consider compressed source routing (SRv6 uSID) as an alternative to tunnel-based path state — even though SRv6 was well-established by the time of publication. The comparison that matters next is not flat-versus-tree but structured-flat-versus-random-flat — and on current silicon, with current transports, that comparison is live. Unlike RNG, WMP-PolarFly is built on open standards and open-source NOS implementations, and is deployable today.

---

## 9. Open Questions and Future Work

The quantitative validation this paper motivates:

1. **WMP-PolarFly vs. RNG** — a direct comparison, contingent on RNG's architectural elements (Spraypoint, ShuffleBox) being made publicly available or independently reimplemented.
2. **MRC-on-PolarFly vs. MRC-on-Clos** — collective completion-time distributions (allreduce, all-to-all) at scale, with specific attention to relay concentration effects under All-to-All. Simulation at q = 7 (57 switches) validates the algebra and WMP mechanics; larger-scale completion-time modeling can be done computationally without requiring physical 100K-GPU testbeds.
3. **Rigorous cost modeling** — WMP-PolarFly vs. fat tree vs. RNG on switch count, optics, power, and total cost of ownership at matched endpoint populations.
4. **Spraypoint convergence and ECMP-table occupancy** — an RNG question, but one whose answer calibrates this comparison.
5. **Passive patch-frame design** — whether the structured analogue of the ShuffleBox (encoding polarity-graph permutations rather than random permutations) can match ShuffleBox manufacturing economics given that it must realize a specific rather than statistical edge set.
6. **Mixed-purpose multi-plane configurations** — cross-plane routing for designs that allocate planes to different functions (e.g., internal fabric + DCI egress), including diameter and weight implications.

---

## References

[1] Bernardi et al., "Expanding into Reality: Random Graphs for Datacenter Networks" (RNG), arXiv:2604.15261, 2026.
[2] Lakhotia et al., "PolarFly: A Cost-Effective and Flexible Low-Diameter Topology," SC22, [arXiv:2208.01695](https://arxiv.org/abs/2208.01695).
[3] OpenAI et al., "MRC: Multipath Reliable Connection," OCP specification, May 2026.
[4] OpenAI et al., "Resilient AI Supercomputer Networking using MRC and SRv6," 2026.
[5] Besta & Hoefler, "Slim Fly: A Cost Effective Low-Diameter Network Topology," SC14.
[6] Valadarsky et al., "Xpander: Towards Optimal-Performance Datacenters," CoNEXT 2016.
[7] RFC 9256, "Segment Routing Policy Architecture," 2022.
[8] RFC 8986, "SRv6 Network Programming," 2021.
[9] Lakhotia et al., "PolarStar: Expanding the Scalability Horizon of All-to-All Networks," SC23.
[10] OpenAI https://openai.com/index/mrc-supercomputer-networking/
[11] Zhou et al., "WCMP: Weighted Cost Multipathing for Improved Fairness in Data Centers," EuroSys 2014.

---

## Appendix A: Even-Characteristic Exclusion and Feasible-Degree Lattice

### A.1 Why q must be an odd prime power

The orthogonal polarity that defines ER_q degenerates in fields of characteristic 2. The bilinear form u₀v₀ + u₁v₁ + u₂v₂ = 0 yields a proper orthogonal polarity only in odd characteristic. In characteristic 2 (where 1 + 1 = 0), the associated quadratic form x₀² + x₁² + x₂² = (x₀ + x₁ + x₂)² — the polarity becomes symplectic, every point is self-conjugate, and the resulting graph loses the C4-freeness and Moore-bound approach that define PolarFly. All powers of 2 (q = 2, 4, 8, 16, …, 256, 512) are therefore excluded from the feasible set.

### A.2 The feasible-degree lattice at high radix

The feasible set of q values comprises odd primes and odd prime powers. Restricting to primes alone: 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, … — never more than about 6 apart at these magnitudes. Odd prime powers (49, 81, 121, 125, 169, 243, …) fill additional points. Despite excluding all powers of 2, the lattice remains dense enough that for any target radix above ~60, a feasible q lies within a few ports.


