# Structured Optimality vs. Engineered Randomness: Weighted Multipath (WMP) Routing on PolarFly Topologies as an Alternative to Random-Graph Datacenter Fabrics

**Author:** Bruce McDougall, Cisco Systems
**Status:** DRAFT v0.4 — for internal review
**Date:** August 2026

---

## Abstract

Two flat datacenter topologies now offer credible alternatives to the classic CLOS fat tree: Amazon's RNG, a quasi-random expander fabric deployed in production with their homegrown Spraypoint routing protocol and ShuffleBox passive optical cabling; and PolarFly, a deterministic diameter-2 topology built on Erdős–Rényi polarity graphs that asymptotically reaches the Moore bound. The two designs embody opposite philosophies: RNG spends topology (longer paths, statistical guarantees) to keep per-hop routing stateless and running on commodity hardware; PolarFly achieves near-optimal scale and path length but is conventionally held back by sparse minimal-path diversity, odd-prime-power size quantization, and cabling complexity.

This paper argues that SRv6 source routing dissolves the central objection to structured low-diameter fabrics — the forwarding-state explosion of k-path routing on commodity ASICs — and proposes **WMP-PolarFly**: a weighted multipath routing design in which SRv6 segment lists and their traffic weights are derived algebraically from the polarity graph's projective-plane coordinates. For any given source-destination pair in the PolarFly fabric, the topology yields one **shortest path (SP)** and a set of **next-shortest-paths (NSPs)** whose count grows with the fabric parameter q; the operator assigns WMP weights across this set (e.g., for q = 7: 40% over the SP and 10% over each of 6 NSPs). We extend the design with multi-plane slicing of high-radix switches, which restores minimal-path redundancy, enables plane-granular hardware heterogeneity, and converts expansion into a purely additive operation. At current 51.2T (512×100G) and forthcoming 102.4T radixes a PolarFly fabric can achieve enormous scale. For example, a 512×100G radix device may be allocated roughly 256×100G for server attachment and 256×100G for fabric attachment¹. The 256×100G fabric ports map to a 2×q=127 sliced configuration, which creates a dual-plane fabric totaling ~16K ToRs and ~4M server ports at diameter 2 and ~99% Moore-bound efficiency, removing scale as a practical differentiator against RNG.

> ¹ The split is not exactly 256/256 for all switches. Most switches have fabric degree q+1 = 128 per plane (256 total), leaving 256 server ports. Self-conjugate vertices have degree q = 127 per plane (254 total), leaving 258 server ports. The variation is small and predictable from the topology's algebra.

Later, we examine the AI backend case, where the recently published MRC (Multipath Reliable Connection) transport — already deployed with SRv6 path steering on frontier training clusters — supplies exactly the missing ingredient for structured fabrics: reorder-tolerant, per-packet multipath spraying with path-aware congestion control. We show that MRC's path-set abstraction maps naturally onto PolarFly's enumerable, algebraically derivable SP + NSP sets, yielding a backend fabric design that combines deterministic diameter-2 latency, near-Moore per-bit cost efficiency, and transport-layer failure resilience. Finally, we examine the applicability of both topologies across deployment regimes — from elastic multi-tenant cloud infrastructures to fixed-footprint AI training clusters — and argue that the choice between them may be primarily driven by operating model and culture.

---

## 1. Introduction

The fat tree's stark trade between cost and oversubscription is well documented: hierarchical structure pins traffic between endpoint pairs to small link subsets that congest while the rest of the fabric idles. Capacity is stranded structurally, not incidentally. Flat topologies — direct ToR-to-ToR interconnects with no aggregation or spine layers — have promised an escape for over a decade, but until 2026 no hyperscaler had deployed one in production.

That changed with Amazon's RNG (Resilient Network Graphs), now the default fabric for most new AWS datacenter builds. RNG validates the flat-topology thesis at production scale: 69% fewer routers, up to 33% higher throughput, 9–45% lower cost than equivalently oversubscribed fat trees. Its enabling contributions are a routing protocol (Spraypoint) that extracts near-degree edge-disjoint path counts from a quasi-random graph using only commodity ECMP, and a passive optical device (the ShuffleBox) that reduces random-graph cabling complexity to fat-tree levels.

RNG's authors frame randomness as the only practical route to a flat fabric, dismissing structured constructions (Slim Fly, Xpander) on the grounds that k-shortest-path routing cannot be realized on commodity switch memory. **K-shortest-path routing** maintains multiple pre-computed forwarding paths (typically 4–16) between each pair of endpoints. Unlike standard ECMP, which distributes traffic across multiple paths of *equal* cost, k-shortest-path uses paths that may vary in length and metric — trading simplicity for richer load-balancing options at the cost of proportionally more forwarding table entries. This paper contests the RNG framing. The dismissal assumes hop-by-hop path state — MPLS tunnels, VRF multiplication, or conventional source-based forwarding — and does not consider compressed source routing. SRv6 uSID moves path state out of transit ASICs entirely: the encapsulation node holds the policy; transit nodes perform a single longest-prefix match on the uSID carrier. The forwarding-state objection, once removed, reveals that a Moore-bound-optimal structured graph holds per-bit efficiency and latency advantages that no random topology can match — and that these advantages compound with every silicon generation.

We develop this argument through PolarFly, the diameter-2 topology of Lakhotia et al. (SC22), and a routing design we call WMP-PolarFly (Weighted Multi-Path PolarFly). Section 2 reviews both topologies and explores the path diversity challenge all  structured topologies face. Section 3 presents the routing design, including algebraic path derivation and principled weight selection. Section 4 introduces multi-plane slicing for high-radix switches. Section 5 examines scale at 51.2T/102.4T radix. Section 6 compares failure models. Section 7 — the backend case — integrates MRC packet spraying. Section 8 offers a side-by-side analysis and identifies the regimes where each design wins.
*`Bruce`*: I wouldn't naturally use the word 'regimes' in this context. Would 'architectures' or 'deployments' work?

A practical note: while RNG is production-proven at Amazon, it is not a publicly available solution. Spraypoint has not been open-sourced; the RNG paper describes the protocol's design but Amazon has not released code or a NOS implementation. ShuffleBoxes are custom passive optical devices with no known commercial source. A non-Amazon operator wishing to deploy RNG today would need to implement Spraypoint from the paper's description on their own NOS, fabricate or commission ShuffleBoxes, and validate the combined system — a substantial engineering investment. By contrast, WMP-PolarFly builds on open-source components (FRR, SONiC) and standard SRv6 as specified in RFC 8986 and RFC 9256.

> **[FIGURE 1 placeholder: side-by-side — generalized fat tree, RNG quasi-random graph, PolarFly ER_q structure for small q]**

---

## 2. Two Flat Topologies, Two Philosophies

### 2.1 RNG: engineered randomness

RNG interconnects routers as a quasi-random graph — a mix of randomized and deterministic cabling segments that reproduces the statistical properties of a true random graph, which is an asymptotically optimal expander. Physical ports are broken out into individual lanes (e.g., 400G into 4×100G), each forming an adjacency with a different remote router; degree *d* and node count *n* are free parameters, and heterogeneous degrees are supported natively.

Routing is Spraypoint: demand-oblivious, fully distributed, ECMP-only. The source "sprays" flows (not per-packet) across its full neighbor set (flow-level 5-tuple hashing; flows stay ordered and standard TCP/NICs are used), and traffic converges on the destination through *waypoint* levels, randomly selected neighbor sets fanning in toward the target. The construction yields a number of edge-disjoint paths close to the node degree, minimally overlapping across endpoint pairs — the source of RNG's capacity fungibility. The cost is path length: sprayed paths typically traverse 4–5 hops (1 spray hop to a random neighbor, then 2–3 additional hops via waypoint convergence toward the destination, plus the final hop), compared to PolarFly's worst case of 2 hops for SP and 3 hops for NSP. The RNG hop tax is accepted in exchange for diversity and statelessness.

Cabling uses ShuffleBoxes — passive optical devices that internally permute fiber connections, so that chained boxes at planned locations realize a quasi-random global topology with fat-tree-like physical cabling complexity. Critically, this is a *randomness-native* trick: the ShuffleBox works because RNG only needs the wiring's statistics to be right, not any specific edge set.

### 2.2 PolarFly: structured optimality

PolarFly is the first diameter-2 topology to asymptotically reach the Moore bound, exceeding 96% of theoretical peak at practical radixes — i.e., it packs nearly the maximum possible number of nodes for its degree and diameter. Every router pair is at most two hops apart allowing for flat topologies of very wide diameter. PolarFly also offers roughly 50% more feasible degrees than Slim Fly, the prior state of the art, and supports modular incremental growth through its cluster structure.

PolarFly ([Lakhotia et al., SC22, arXiv:2208.01695](https://arxiv.org/abs/2208.01695)) connects N = q² + q + 1 routers (with q being an **odd** prime number or prime power) with fabric degree q + 1, as the Erdős–Rényi polarity graph ER_q derived from the projective plane PG(2, q). The practical consequence: the feasible set is odd primes (3, 5, 7, 11, 13, …) and odd prime powers (9, 25, 27, 49, 81, 121, 125, 243, …). (See also Appendix A.)

### 2.3 The path diversity inversion

PolarFly's topology has a distinctive structural property: **no two routers in the fabric share more than one common neighbor**. This is what gives it exceptional scale — edges are never "wasted" on redundant two-hop paths — but it creates a routing challenge: between most pairs of routers that are not directly connected, there is only **one** shortest (2-hop) path. In networking terms, imagine a fabric where every source-destination pair has exactly one spine to go through; there is no second shortest path to hash onto.

This creates an irony: the very property that makes PolarFly the most efficient topology (maximum routers per port per hop count) simultaneously starves it of the path redundancy that load balancing / entropy depends on. **Optimality and diversity are structurally in tension** — the closer a topology sits to the theoretical efficiency limit (the Moore bound), the fewer shortest paths it can offer per pair.

RNG begins from the same observation regarding structure-optimized topologies: shortest-path routing on any highly efficient topology will congest those singleton shortest paths. RNG's answer is to **abandon shortest-path routing entirely** and let the randomness of the graph supply diversity through longer, sprayed paths. PolarFly's conventional answer — inherited from the Slim Fly and Dragonfly HPC lineage — is non-minimal adaptive routing (UGAL-style), where switches sense congestion in real time and deflect traffic onto longer paths. But UGAL requires HPC-class adaptive-routing hardware; it is not available on commodity Ethernet ASICs running standard routing protocols.

SRv6 source routing is the third answer, and it changes the economics entirely.

---

## 3. WMP-PolarFly

### 3.0 The WMP concept: shortest path + next-shortest-paths

The core of the WMP-PolarFly routing design is **Weighted Multi-Path (WMP)**: SRv6 source routing steers traffic across a source-destination pair's **shortest path (SP)** and a set of **next-shortest-paths (NSPs)** in an operator-configurable ratio.

For a given source-destination pair in a PolarFly fabric with parameter q:

- The **SP** is the unique 2-hop path through the pair's single shared neighbor (the relay node).
- The **NSPs** are the set of 3-hop paths through intermediate nodes that are *not* the relay — approximately q edge-disjoint alternatives whose exact count varies slightly for self-conjugate vertices.

For q = 7 this gives **1 SP + 6 NSPs = 7 total forwarding paths**. Each path is encoded as an SRv6 segment list (a uSID carrier, typically fitting in the IPv6 destination address with no SRH required). The operator assigns WMP weights across the set — for example, 40% of traffic over the SP and 10% over each of the 6 NSPs. As q increases, the NSP count grows roughly with q, providing increasingly rich path entropy: q = 31 yields ~1 shortest-path + 31 next-shortest-paths, q = 127 yields ~1 + 127 paths, and so on.

Two properties make this design distinctive. First, in a PolarFly topology the SP and every NSP are **algebraically derivable** from the source and destination routers' addresses, so there is no need for topology discovery tools such as BGP-LS (Section 3.2). Second, the path state lives entirely in the server/SmartNIC where **encap-node policy memory** is abundant, rather than in table-constrained transit ASICs. This is why WMP-PolarFly works on commodity hardware where tunnel-based k-shortest-path routing cannot (Section 3.1).

### 3.1 State economics: inverting the RNG critique

RNG's quantitative case against k-shortest-path routing: with n = 10K routers, k = 8 paths, and ~4 routers per path, tunnel-based implementations require on the order of 320K forwarding entries per router. Modern commodity switching ASICs offer substantially more forwarding capacity than the 4–16K range RNG's analysis cites — Broadcom Tomahawk 5 supports >300K IPv6 ALPM entries — but the k-shortest-path state problem scales with n² and grows with both fabric size and path diversity. At q = 127 (16,257 routers), WMP-PolarFly uses ~128 paths per destination — a tunnel-based implementation would require approximately 128 paths × 16,257 destinations × ~3 entries per path ≈ **6.2M forwarding entries per router**, catastrophically beyond any current or planned ASIC. The problem is not that ASICs are too small today; it is that tunnel-based path state scales in the wrong dimension.
*`Bruce`*: could we use q=61 for this comparison as it'll reflect a ~4000 switch count that readers will see as realistic for current DC deployments. By my math we're still talking 61 paths x3800 nodes x 3 entries = ~700k which still pushes beyond commodity hardware

SRv6 uSID restructures the problem entirely. Each SP and NSP segment list fits within a single uSID carrier. The SP + NSP set for all destinations concentrates at encapsulation nodes as O(k·n) segment lists in host or edge policy memory (which is cheap and abundant), while the transit FIB holds only the node-SID table and uA adjacency table: O(n), plain LPM, no per-path entries, no tunnels, no VRF multiplication. At q = 61, the transit FIB holds ~4k node-SID entries. Jump up to q = 127 and the transit FIB holds ~16K node-SID entries — well within any modern ASIC's capacity, with room to spare. The fabric ASICs remain **minimal-state** — arguably carrying less state than RNG's, since they bear no ECMP group pressure (Section 5.3). The intelligence relocates to the encap point, where memory is abundant and the computation is — as the next section shows — a direct formula that can be evaluated without any iterative algorithm or external lookup.

### 3.2 Algebraic path derivation

The property that elevates WMP-PolarFly beyond generic source routing on a low-diameter graph: **the SP and NSP set is algebraically derivable**. Vertices of ER_q are points of PG(2, q); adjacency is the polarity (orthogonality) relation. The unique common neighbor of two non-adjacent vertices — the relay node of the SP — is computable directly from their projective coordinates via finite-field arithmetic. The NSP set (on the order of q edge-disjoint 3-hop paths; total pair connectivity ≈ q + 1, with exact counts varying for the self-conjugate, degree-q vertices) is likewise enumerable from coordinates.

In practical terms: for any pair of routers in a q = 7 fabric, the topology guarantees exactly **1 SP** (2 hops through a single relay node) and approximately **6 NSPs** (3 hops each, through different intermediate nodes). The remarkable property is that *which* nodes serve as relays is computable directly from the routers' addresses — no routing protocol is needed to discover these paths. Here is how that computation works:

**Worked example (q = 7).** In a q = 7 WMP-PolarFly fabric — 57 routers, each with 8 fabric ports (or 7, for self-conjugate nodes) — every router has a 3-digit address in mod-7 arithmetic: its projective coordinate, e.g., (1, 3, 5). Two routers are directly cabled if the dot-product of their coordinates equals zero mod 7. Suppose router A = (1, 0, 2) wants to reach router C = (1, 4, 6). They are not directly connected (1·1 + 0·4 + 2·6 = 13 ≡ 6 mod 7 ≠ 0). To find the SP relay — the one common neighbor B — we solve for coordinates (b₀, b₁, b₂) such that A·B = 0 and B·C = 0 simultaneously, i.e., b₀ + 2b₂ ≡ 0 and b₀ + 4b₁ + 6b₂ ≡ 0, both mod 7. This is a system of two linear equations in projective space, yielding exactly one solution (up to scalar multiple): the relay node B. The encap node at A performs this computation — two inner products and a linear solve in mod-7 arithmetic — and emits the SRv6 segment list [uSID-B, uSID-C] for the SP. The same coordinate arithmetic enumerates the 6 NSPs for A→C, each via a different first-hop neighbor that is *not* the direct relay, producing 6 additional segment lists.

The control-plane consequence is significant: **no path-computation protocol is required in this design**. To be precise: running a base routing protocol (IS-IS or BGP) for node-SID distribution and liveness detection is certainly useful — its best the fabric knows *which* routers are alive. However, a committed operator could also algebraically derive the set of static routes every node would need for remote node-SID reachability. The key point is, the functions traditionally performed by RSVP-TE, PCE, or CSPF — *discovering and computing paths* — is eliminated entirely. The encap node synthesizes the full SP + NSP segment-list set from the destination's coordinates alone. Where Spraypoint must compute and disseminate waypoint levels by protocol, WMP-PolarFly's paths are implicit in the topology's algebra. This is a built-in structural simplicity.

### 3.3 Weighted multipath (WMP)

Traffic between a source-destination pair splits across the derived SP and NSP segment lists with explicit weights: a fraction w_SP on the shortest path and (1 − w_SP) spread across the NSP set.

In plain terms: at small fabric sizes (low q), giving the SP a larger share of traffic makes sense — it is the most efficient path (2 hops vs. 3), and there are only a few NSP alternatives to spread across. As the fabric grows (higher q), the NSP count increases roughly with q, and each individual NSP carries proportionally less traffic. The optimal strategy shifts: spread more traffic across the larger NSP set, because concentrating on the single SP wastes the path diversity the topology provides. At q = 7, a 40/60 split (40% SP, 10% each across 6 NSPs) loads the SP at roughly 4× the per-path rate of each NSP — a reasonable allocation, since the 2-hop path consumes fewer link-traversals per bit. At q = 127, the same 40% on one path out of ~128 would be grossly imbalanced; the weight shifts toward a more even distribution.
*`Bruce`*: q=127 might perhaps use ~2/.75 where SP takes ~2% and the 127 NSPs take ~.75% each? Or the encapsulating NIC might call it a wash and simply treat the 128 (SP + NSPs) as ECMP. Also, does this design actually ask the NIC to hold k-shortest-paths in its FIB? Presumably it doesn't need paths to all 3783 or 16k nodes at any given time, but it might be somthing to call out. I expect modern frontend DC DPUs and backend AI DC SmartNICs (ConnectX, Pollara) can handle pretty large FIB sizes.

We deliberately specify the weight as a **derived function, not a constant**. The optimal demand-oblivious split follows from the same capacity accounting underlying the Valiant/UGAL literature, and a single path's share of total pair capacity shrinks as 1/(q + 1). The weight formula is not a tuning knob the operator must guess at — though operators *can* override it for specific traffic patterns.

The weight function takes as inputs: q; the path-length ratio (2 vs. 3 hops); the pair type (Section 3.4); and — critically for incremental deployment — the **live-vertex set**. In a partially built fabric, the SP relay between a live pair may not yet be installed; the encap node detects this from the installed-coordinate set and re-derives weights over the realized subgraph, again with no protocol convergence. Conditional weighting over the realized subgraph is, to our knowledge, novel, and is among the elements identified for internal invention disclosure.

> **[FIGURE 2 placeholder: WMP weight as a function of q; SP vs. per-NSP load curves]**

### 3.4 What RNG retains

**Heterogeneous router degrees.** RNG supports switches with different port counts in a single fabric. If a new-generation switch has 64 ports and the existing fleet has 32, the new switch simply takes more neighbors — the random graph's statistical properties degrade gracefully rather than breaking. In principle, operators can also vary the server-to-fabric port ratio per switch. In practice, the RNG paper does not quantify how path diversity and Spraypoint's load-balancing guarantees degrade as the degree distribution becomes uneven — a heavily lopsided mix (some switches at degree 16, others at degree 64) would weaken expansion properties for the low-degree nodes even though the graph remains connected and routable. WMP-PolarFly is not as flexible as it requires uniform degree within each plane; the multi-plane slicing of Section 4 provides a coarser but operationally cleaner heterogeneity model (e.g., a 400G plane alongside a 100G plane).

**Unquantized sizing and continuous growth.** RNG can be built at any node count *n* — a fabric could be 2,073 nodes, it could be 8,062, whatever the building needs. PolarFly is quantized to q² + q + 1 for the available odd prime powers, and growth beyond the chosen q is a forklift. However, at modern radix this constraint is mild, as the following table shows:

| q | Fabric degree (q+1) | Switches (q²+q+1) |
|---|---|---|
| 7 | 8 | 57 |
| 31 | 32 | 993 |
| 61 | 62 | 3,783 |
| 127 | 128 | 16,257 |
| 251 | 252 | 63,253 |
| 509 | 510 | 259,591 |

Partial deployment within a chosen q is additive (Section 4), but the maximum WMP-PolarFly fabric size is locked to the math, and the operator must pick q at design time and live with the ceiling.

**Stateless operational philosophy.** RNG's transit routers hold destination-based LPM and ECMP groups — the same state any IP router carries. There are no policies, no segment lists, no per-pair configuration anywhere in the fabric. The fabric cannot be misconfigured because it holds no per-path configuration to get wrong. WMP-PolarFly concentrates correctness in the encap-node policy computation. The computation is algebraically deterministic (Section 3.2), but it *is* computation — and the encap node must be right. RNG spends topology to keep routing minimal-state; WMP-PolarFly spends routing intelligence to keep topology optimal.
*`Bruce`*: does RNG use IPv6 addressing or all link-local (can't even misconfigure an IP)?

---

## 4. Multi-Plane Slicing

When a switch has more physical ports than a single PolarFly plane requires, the surplus ports can serve additional planes — trading some per-plane scale for path redundancy, increased bisection bandwidth, heterogeneity support, and operational flexibility.

For reference, the following table shows PolarFly fabric sizes at selected values of q:

| q | Type | N = q²+q+1 (switches) | Fabric degree (q+1) | Notes |
|---|---|---|---|---|
| 7 | prime | 57 | 8 | Lab validation target |
| 31 | prime | 993 | 32 | Dual-plane on 64-port switch |
| 61 | prime | 3,783 | 62 | Quad-plane on 512-port (51.2T) |
| 127 | prime | 16,257 | 128 | Dual-plane on 512-port (51.2T) |
| 251 | prime | 63,253 | 252 | Single-plane on 512-port |
| 509 | prime | 259,591 | 510 | Future 102.4T single-plane |
*`Bruce`*: for 251 and 509 the single-plane switch counts are beyond any known DC plans. Let's make 251 dual-plane on 102.4T and maybe we leave 509 out. 127 could be have two options Dual 512 and Quad 102.4T

### 4.1 Dual-plane and quad-plane configurations

On a 51.2T switch with 512×100G ports, the operator chooses how to partition between fabric and server attachment. Two configurations merit detailed comparison:

**Initial production configuration: Quad-plane 512x100G radix (4×q=61).** Each switch allocates 4×62 = 248 ports to fabric (62 per plane) and 264 ports to server attachment. This yields 3,783 switches with ~1M server attachment points — sufficient for the largest datacenter buildings in production today — and leveraging four independent PolarFly planes. Every source-destination pair enjoys **4 edge-disjoint SPs** (one per plane) plus 4×~61 NSPs ≈ **248 total forwarding paths**. The four-plane redundancy delivers exceptional failure resilience (any single plane failure is a weight rebalance among three surviving same-length SPs, not a hop-count transition), and the per-relay incast under All-to-All is manageable at ~61 flows per relay per plane.
*`Bruce`*: this is great. Is there also a frontend/Cloud DC incast use case we might also mention or add in parenthesis?

**Scale-ceiling configuration: Dual-plane 512x100G (2×q=127).** Each switch allocates 2×128 = 256 ports to fabric (128 per plane) and 256 to server attachment. This yields 16,257 switches with ~4M server attachment points — well beyond any single building in production — across two planes with **2 SPs + ~254 NSPs per pair**. The 99% Moore-bound efficiency at this radix makes it the most port-efficient flat topology achievable at diameter 2.

Both configurations share the same physical switches; the choice is a design-time decision about where to spend the port budget. The 4×q=61 configuration trades scale for more SPs and significantly better failure properties, making it the natural recommendation for production deployments. The 2×q=127 configuration demonstrates that PolarFly can match any building-scale requirement — the scale objection against structured topologies no longer applies at modern radix. For AI backend fabrics (Section 7), where cluster sizes are typically 1–4K switches, even 2×q=31 (993 switches, dual-plane on modest radix, 8-plane on 51.2T with 250k server attachment ports) may suffice, with the full port budget available for server attachment.
*`Bruce`*: i added the 8-plane bit. Is my math correct?

What multi-plane slicing buys, regardless of configuration:

**Minimal-path redundancy.** Every pair holds one SP per plane. With 4 planes, a single-plane failure leaves 3 surviving SPs at identical hop count — no RTT shift, just a weight rebalance. This substantially closes the gap against RNG's continuous failure model (Section 6).

**Plane-granular heterogeneity.** Each plane is internally uniform, but planes may differ: a 400G plane may reside next to a 100G plane, with WMP weights proportional to plane bandwidth. A hardware refresh becomes "stand up a new plane" — coarser than RNG's per-node degree mixing, but ever-increasing radix makes this less of a problem with each generation.

**Additive expansion.** Because the complete edge set of each plane is known in advance, growth never breaks an existing link: a landing router patches into q + 1 pre-planned positions per plane. With pre-provisioned passive patch frames carrying the polarity-graph permutation — the structured analogue of the ShuffleBox, though it must encode the *specific* edge set rather than a blind permutation — PolarFly expansion is arguably cleaner than RNG's break-and-splice appendix. The residual costs: q is a day-1 ceiling (the next odd prime power is a forklift), and the partial graph's path multiplicity is nonuniform, which the live-vertex-aware weight function of Section 3.3 absorbs.

### 4.2 Beyond dual-plane: multi-plane membership and the intersection property

When slicing beyond 2 planes on the same vertex set, the number of planes a switch participates in determines the fabric's diameter guarantee. 

In the configurations of Section 4.1, every switch participates in *all* planes simultaneously (all 4 in 4×q=61, both in 2×q=127), which trivially preserves diameter 2 — every pair shares every plane. But as radix grows further, an operator might want more planes at lower per-plane degree, and it becomes impractical for every switch to join every plane. The question then is: if each switch belongs to only *some* planes, can we still guarantee diameter-2 reachability?
*`Bruce`*: love this!

The answer depends on a simple combinatorial property: **any two switches must share at least one plane in common** — the same way any two people who each speak 2 out of 3 languages will always share a language they can converse in. If each switch belongs to 2 out of p = 3 planes, this property holds: any two 2-subsets of {A, B, C} necessarily overlap. Some pairs share two planes and enjoy dual SPs; others share exactly one plane and have a single SP. The pair type — which planes two switches share — is simply two more coordinates in the address, so the WMP weight derivation remains a direct formula. As a concrete example, 3×q=83 on a 512-port switch (3×84 = 252 fabric ports, 260 server ports, ~7,000 switches) with 2-of-3 membership would preserve diameter 2 globally while providing a middle ground between the 4×q=61 and 2×q=127 configurations.

At **p ≥ 4** with partial membership, the intersection guarantee breaks: two switches belonging to planes {A,B} and {C,D} share no common plane and must transit a bridging switch, raising diameter to 4. At this point the partial-membership constructions become effectively hand-rolled star products, and the honest comparison is no longer against vanilla PolarFly but against **PolarStar** (the diameter-3 star product of ER_q with Paley or inductive-quad graphs — the literature's answer to scaling past q² + q + 1) and BundleFly. Our expectation, to be validated: PolarStar wins on scale-per-port; multi-plane slicing wins on plane-granular heterogeneity and operational modularity.
*`Bruce`*: I've thought about this some in the context of north-south traffic in-out of the DC (public cloud use case). Theoretically the 512x100G switch could be carved as 4xq=61, but with three plans for server attachment and the 4th plane representing an egress or DCI polarfly. Does that logic work?

> **[FIGURE 3 placeholder: multi-plane membership diagram showing p=3 and p=4 configurations; pair-type path multiplicity table]**

To our knowledge, multi-plane membership combinatorics used as a *diameter-preservation mechanism*, with cross-plane WMP weights derived from pair-type labels, is novel. This is among the elements identified for invention disclosure.
*`Bruce`*: I think we can leave out notes on what we plan to patent

---

## 5. Scale at Modern Radix

### 5.1 The Moore ceiling moves above building size

Radix growth is asymmetric between the two designs: it repairs PolarFly's largest weakness while only marginally improving RNG's position.

At 51.2T (512×100G effective lanes), q = 127 yields a 16,257-switch plane at fabric degree 128 — against a Moore bound of d² + 1 = 16,385, i.e., **99% of the theoretical maximum reach for diameter 2**. A pure-transit 4×q=127 configuration is possible but leaves no room for server attachment ports; the realistic ToR-integrated build is **2×q=127** — 256 lanes fabric, 256 lanes server downlink — giving 16,257 ToRs × 256 ports ≈ **4M attachment points at 1:1, dual minimal paths, diameter 2**. That exceeds the footprint of any single building in production today.

Carving the same 512×100G switch budget into 4 planes yields **4×q=61** — 248 fabric ports, 264 server ports, 3,783 switches, and ~1M attachment points. This still far exceeds the compute footprint of any single datacenter building, while providing 4-way SP redundancy and substantially richer path diversity per pair. As discussed in Section 4.1, 4×q=61 is the recommended production configuration; 2×q=127 serves as the scale ceiling for scenarios that require it.

The feasible-degree lattice is the set of odd prime powers: restricting to primes alone gives (61, 67, 71, 73, 79, 83, 89, 97, …), never more than about 6 apart at these magnitudes; odd prime powers (49, 81, 121, 125, 169, 243, …) fill additional points. Powers of 2 — including 64, 128, 256, 512 — are excluded by the even-characteristic degeneracy described in Appendix A, so the lattice is sparser than "all prime powers" but remains dense enough that for any target radix, a feasible q lies within a few ports. Both classical objections — quantization and the q² ceiling — cease to be practical constraints at current-generation silicon.

### 5.2 Per-bit economics compound with bandwidth

Fabric capacity consumed per delivered bit is proportional to hop count. The WMP mix runs at roughly L ≈ 2.6 effective hops (weighted across 2-hop SP and 3-hop NSP sets); Spraypoint's spray-plus-waypoint structure runs meaningfully longer — typically 4–5 hops. At 100G lanes this isn't trivial; at 200G per lane and beyond, each extra hop is another traversal of increasingly expensive and power-hungry optics and serdes. A near-Moore fabric at L ≈ 2.6 sits close to the information-theoretic floor of fabric-capacity-per-delivered-bit. RNG's cost case is "up to 45% cheaper than fat tree" — but the fat tree is a soft target; against a Moore-optimal structured fabric, RNG's hop tax becomes an economic consideration, and it grows in absolute dollars and watts with every silicon generation. The structured topology's advantage here strengthens with scale.

### 5.3 RNG's pressure points at large flat scale

RNG has no topological ceiling, but three practical pressures emerge at large scale. First, the control plane: Spraypoint is a distributed protocol over a flat domain with no hierarchy; dissemination and convergence behavior at thousands of nodes under churn is an open question. Second, ECMP hardware: spraying across the full neighbor set implies ECMP groups approaching the lane count, and ASIC ECMP member tables are a finite, contested resource — 512-wide groups per destination class is real pressure even with group sharing. WMP-PolarFly sidesteps this entirely: explicit paths consume encap-node policy memory, not transit ASIC tables. Third, expansion recabling complexity scales with d: at d = 512, every rack land touches 256 existing links spread across the building. None of these is fatal, but all worsen with radix, while WMP-Polarfly's additive pre-planned algebraic expansion improves relatively.

---

## 6. Failure Models: Statistical Headroom vs. Repair Logic

RNG's resilience claim is best understood as a claim about *blast-radius shape*, and a precision matters: Spraypoint absolutely reacts to failure — it is a routing protocol in the OSPF/BGP mold and reconverges on topology change. What RNG eliminates is *protection machinery*: no FRR, no precomputed backups, no TI-LFA-style repair, because steady-state forwarding already encodes the redundancy. When a link dies, the adjacent router locally prunes the member from its ECMP groups and traffic redistributes in the data plane instantly; the failed link carried roughly 1/d of any affected pair's capacity, so the loss is a thin statistical shave across many pairs rather than a mode change for any one. There are no special routers; every failure is small and uniform. Protocol convergence cleans up in the background with nothing waiting on it.

Single-plane PolarFly, by contrast, undergoes a discrete transition when a pair's unique SP dies: 2-hop traffic steps to the 3-hop NSP set, with an RTT shift congestion control will notice. The response is fast — the encap node re-derives weights algebraically, arguably faster than any IGP floods — but it is a *reaction*, with a detectable before/after. Multi-plane slicing (Section 4.1) converts the transition from a length change into a weight rebalance among length-identical SPs on surviving planes, substantially closing the gap. In the recommended 4×q=61 configuration, losing one plane's SP still leaves 3 same-length SPs — no hop-count transition at all. In the backend deployment of Section 7, MRC moves failure handling into the transport entirely.

The honest framing for operators: PolarFly offers deterministic best-case behavior with discrete failure modes; RNG offers probabilistic behavior with continuous failure modes. Preference depends on whether the workload fears tail latency or fears variance.

---

## 7. The AI Backend: MRC and Packet Spraying on PolarFly

### 7.1 Why the backend is the natural home

RNG's authors explicitly scope to multi-tenant general-purpose fabrics and defer AI training, noting that such workloads may demand rail-optimized structures and local capacity islands that flat random topologies lack. The backend is simultaneously the regime where every PolarFly disadvantage evaporates: the fabric is built once at known size, the operator owns the stack end to end, the hardware population is uniform per build, and per-bit cost and power compound directly into training economics (Section 5.2). Collective-driven traffic additionally rewards deterministic path lengths: flow-completion-time skew across parallel transfers gates the collective, and a hard diameter-2 bound with enumerable path lengths is precisely the property a scheduler can reason about.

What the structured Ethernet fabric has historically lacked in this regime is a transport that can exploit its path set. With MRC that transport now exists.

### 7.2 MRC in brief

MRC (Multipath Reliable Connection), contributed to OCP in May 2026 by OpenAI with AMD, Broadcom, Intel, Microsoft, and NVIDIA, extends RDMA-over-Ethernet semantics so that **a single RDMA connection distributes traffic across multiple network paths**, with reordering tolerated by the transport and congestion managed per path (AMD's NSCC algorithm, now part of the UEC congestion-control specification). It is implemented on shipping 400/800G NICs (ConnectX-8, Pollara, Vulcano, Thor Ultra) with **SRv6 switch support** on Spectrum-4/5 (Cumulus, SONiC) and Tomahawk 5 (EOS), and is deployed in production on OpenAI's largest GB200 clusters (OCI Abilene, Microsoft Fairwater). Cisco Silicon One G200 also supports SRv6 but has not yet appeared in production MRC deployments. The companion paper is explicitly titled "Resilient AI Supercomputer Networking using MRC and SRv6." Reported topology practice mirrors the breakout philosophy: rather than one 800G link, the NIC is split into multiple smaller links to create natural path redundancy, enabling two-tier builds at 100K+ GPU scale with roughly two-thirds the optics and 40% fewer switches than three-tier baselines.

Three properties matter for our purposes. MRC is **reorder-tolerant**, so per-packet (or per-message-slice) spraying is admissible where general purpose cloud requires per-flow distribution. MRC is **path-aware**, maintaining per-path state and congestion signals within one connection. And MRC's deployed path-steering mechanism **is already SRv6** — the same encapsulation substrate as the WMP-PolarFly design.

### 7.3 The synthesis: per-packet WMP over algebraic path sets

Recall why WMP was specified at flow level (Section 3.3 context): general-cloud tenants run vanilla TCP on stock NICs, and per-packet spraying would have required reorder-tolerant transports that cannot be assumed across an adversarial tenant population. The backend inverts the assumption — every endpoint is an MRC-capable RDMA NIC — and the design strengthens along four axes.

**Spraying granularity.** The WMP weights of Section 3.3 apply per packet rather than per flow. Elephant-flow collision risk — the residual weakness of any flow-hashed scheme, RNG's included — vanishes: a single connection's load spreads across the full SP + NSP set in proportion to the derived weights. This is, notably, a capability RNG's general-cloud deployment does not have; Spraypoint sprays flows, not packets.

**Path-set provisioning.** MRC requires each connection to be provisioned with a set of paths (EVs or Entropy Values). On a Clos this set is implicit (ECMP up, ECMP down); on PolarFly it is *explicit and enumerable* — exactly q + 1-ish edge-disjoint segment lists per pair, synthesized from projective coordinates with no path discovery protocol. PolarFly converts MRC's path-set abstraction from a fabric-dependent configuration burden into a direct algebraic computation at connection setup. The diameter-2 bound additionally caps the path-length spread within a connection's set at one hop (2 vs. 3), simplifying the transport's reordering and completion-tracking window relative to a random graph's longer-tailed length distribution.
*`Bruce`*: MRC is packet re-order tolerant, however, in the SP + nxNSP WMP-Polarfly packets on the SP (or set of SPs in multi-planar) will always arrive ahead of packets taking an NSP path. Do we feel MRC is re-order tolerant enough for that scenario? Or does MRC discard the SPs and simply spray across the most-likely large number of available NSPs?

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
| Heterogeneity | RNG | Per-node degree mixing, in place | Plane-granular | RNG finer-grained; slicing operationally cleaner |
| Incremental growth | RNG | Unquantized; break-and-splice | Additive to q ceiling; pre-planned | Different shapes; PolarFly cleaner per step |
| Failure model | — | Continuous, statistical, no protection | Discrete → continuous with 4-plane slicing | Parity at 4 planes; RNG edges single-plane |
| Operational philosophy | RNG | Stateless fabric, minimal-state everywhere | Intelligence concentrated at encap | The irreducible difference |
| Availability | WMP-PolarFly | Amazon-internal; not open-sourced | Open standards (SRv6), open NOS (SONiC/FRR) | Deployable today vs. requires reimplementation |

The two topology families do not converge with scale; they sort by operating model. **Engineered randomness has its advantages in the elastic-fleet (Cloud) deployment**: daily rack lands, rolling hardware generations, adversarial multi-tenant traffic, and an operational culture that prizes a fabric incapable of holding misconfiguration. **Structured optimality has the advantage in deliberate-fabric (AI backend) deployment**: build-once footprints, operator-owned stacks, per-bit economics that compound, and workloads — above all AI training collectives — that reward deterministic latency and enumerable paths. Modern radix removes scale as a discriminator; SRv6 removes the forwarding-state objection; MRC removes the transport objection. What remains is a genuine philosophical choice about where complexity should live, and the thesis of this paper is that for the backend, the answer has quietly become the encap node.
*`Bruce`*: I would argue (and Cloud agrees) that complexity/encap/policy-execution have always belonged on the host

The boundary between regimes (Cloud vs. AI fabric architectures) is less sharp than the literature implies. A fixed-footprint general-cloud datacenter — a sovereign cloud build, a large enterprise private cloud, a neocloud region — shares many characteristics of the "deliberate-fabric" regime: known size at build time, operator-owned stack, uniform hardware generation. WMP-PolarFly is a legitimate candidate for such deployments, and the remaining RNG advantages in that context (unquantized n, per-node heterogeneity) are operational preferences rather than hard technical requirements. The interesting open question is not "which topology for cloud?" but whether "general cloud" is really one regime at all.

A closing observation on the literature: RNG's published case is argued against the fat tree, and its dismissal of structured alternatives does not consider compressed source routing (SRv6 uSID) as an alternative to tunnel-based path state — even though SRv6 was well-established by the time of publication. The comparison that matters next is not flat-versus-tree but structured-flat-versus-random-flat — and on current silicon, with current transports, that comparison is live.

---

## 9. Open Questions and Future Work

The quantitative validation this paper motivates:

1. **WMP-PolarFly vs. RNG** — a direct comparison, contingent on RNG's architectural elements (Spraypoint, ShuffleBox) being made publicly available or independently reimplemented.
2. **MRC-on-PolarFly vs. MRC-on-Clos** — collective completion-time distributions (allreduce, all-to-all) at scale, with specific attention to relay concentration effects under All-to-All. Simulation at q = 7 (57 switches) validates the algebra and WMP mechanics; larger-scale completion-time modeling can be done computationally without requiring physical 100K-GPU testbeds.
3. **Spraypoint convergence and ECMP-table occupancy** — an RNG question, but one whose answer calibrates this comparison.
4. **Passive patch-frame design** — whether the structured analogue of the ShuffleBox (encoding polarity-graph permutations rather than random permutations) can match ShuffleBox manufacturing economics given that it must realize a specific rather than statistical edge set.

*(Patent-relevant elements to be consolidated in a separate internal disclosure document.)*

---

## References (to be completed)

*Placeholder — full citations to be added:* Bernardi et al., "Expanding into Reality: Random Graphs for Datacenter Networks" (RNG), arXiv:2604.15261, 2026 · Lakhotia et al., "PolarFly: A Cost-Effective and Flexible Low-Diameter Topology," SC22, [arXiv:2208.01695](https://arxiv.org/abs/2208.01695) · Lakhotia et al., PolarStar · Singla et al., "Jellyfish: Networking Data Centers Randomly," NSDI 2012 · Valadarsky et al., "Xpander," 2016 · Besta & Hoefler, "Slim Fly," SC14 · OpenAI et al., MRC specification, OCP, May 2026 · OpenAI et al., "Resilient AI Supercomputer Networking using MRC and SRv6" · Zhou et al., "WCMP: Weighted Cost Multipathing," EuroSys 2014 · RFC 9256 (SR Policy Architecture) · RFC 8986 (SRv6 Network Programming) · Erdős–Rényi polarity graph / Brown graph literature · EvalNet toolchain, arXiv:2105.12663.

---

## Appendix A: Even-Characteristic Exclusion (to be written)

*Placeholder — technical explanation of why q must be an odd prime power: the orthogonal polarity ER_q uses degenerates in characteristic 2, as x₀² + x₁² + x₂² = (x₀ + x₁ + x₂)² in fields where 1 + 1 = 0. The polarity becomes symplectic, every point is self-conjugate, and the resulting graph loses C4-freeness and the Moore-bound approach that define PolarFly. All powers of 2 (q = 2, 4, 8, 16, …, 256, 512) are therefore excluded from the feasible set.*

---

## Changelog

**v0.3 → v0.4:**
- Abstract: added footnote on self-conjugate vertex port split (258/254 vs. 256/256)
- Abstract: removed hard regime-sorting conclusion; replaced with nuanced framing
- Section 1: confirmed RNG availability note placement at end of section; clarified "does not consider" vs. "predates" for SRv6
- Section 3.1: sharpened ASIC comparison with q=127 tunnel-state calculation (6.2M entries); added TH5 >300K ALPM reference; clarified transit FIB at ~16K entries
- Section 4: restructured around dual presentation — 4×q=61 as recommended production configuration, 2×q=127 as scale ceiling
- Section 4.1: merged dual-plane and quad-plane into single subsection with concrete 512-port examples and path counts
- Section 4.2: renamed k→p for plane count to avoid collision with k-shortest-path; added plain-language intersection explanation ("shared language" analogy); concrete 3×q=83 example; connected to patent-relevant novelty
- Section 5.1: presents both 4×q=61 (~1M ports) and 2×q=127 (~4M ports) configurations
- Section 5.3: softened scale language from "16K+" to "large flat scale"
- Section 6: updated for 4-plane configuration (3 surviving SPs on single-plane failure)
- Section 7.2: added Cisco G200 SRv6 support note
- Section 7.4: incorporated Bruce's edits; verified accuracy
- Section 7.5: smoothed Clos-to-Spraypoint transition into two distinct comparisons; added 4×q=61 incast analysis (~61 flows per relay per plane)
- Section 8: added Advantage column to scorecard; replaced "retires" with "addresses"; updated closing SRv6 observation to "does not consider" rather than "predates"
- Section 9: reframed bake-offs as simulation targets; noted patent elements moved to separate document
- Appendix A placeholder added

**v0.2 → v0.3:**
- Renamed design to WMP-PolarFly throughout; "SRv6-based WMP-PolarFly" only as long form
- Formalized SP (shortest path) and NSP (next-shortest-path) as defined terms
- New Section 3.0 introducing WMP concept with SP/NSP before state economics
- Section 2.2: moved characteristic-2 math to Appendix A; body states constraint simply
- Section 3.1: k-shortest-path definition acknowledges ECMP distinction
- Section 3.2: plain-English lead-in before worked example; SP/NSP terminology throughout
- Section 3.3: added layman's explanation of weight shift with q
- Section 3.4: concrete explanation of RNG flexibility with honest caveats

**v0.1 → v0.2:**
- Renamed design from WCMP-SRv6-PolarFly to SRv6-WMP-PolarFly throughout
- Applied odd-prime-power correction: Section 2.2 now explains characteristic-2 degeneracy; Section 5.1 lattice corrected to exclude powers of 2
- Section 1: added k-shortest-path definition; added paragraph on Spraypoint/RNG availability
- Section 2.1: quantified Spraypoint hop count (4–5 hops typical)
- Section 2.2: added arXiv link to PolarFly paper
- Section 2.3: rewrote both paragraphs for network-engineer readability
- Section 3.1: updated ASIC baselines (G200, TH5); replaced "stupid" with "minimal-state"; defined "closed-form" inline
- Section 3.2: added worked q=7 example; clarified that IS-IS/BGP still needed for liveness
- Section 7.5: new subsection on All-to-All collectives and bisection bandwidth
- Section 8: added "Availability" row to scorecard; softened front-end cloud concession; added paragraph on regime boundary
