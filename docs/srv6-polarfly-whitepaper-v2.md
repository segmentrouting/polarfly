# Structured Optimality vs. Engineered Randomness: Weighted Multipath (WMP) Routing on PolarFly Topologies as an Alternative to Random-Graph Datacenter Fabrics

**Author:** Bruce McDougall, Cisco Systems
**Status:** DRAFT v0.3 — for internal review
**Date:** August 2026

---

## Abstract

Two flat datacenter topologies now offer credible alternatives to the classic CLOS fat tree: Amazon's RNG, a quasi-random expander fabric deployed in production with their homegrown Spraypoint routing protocol and ShuffleBox passive optical cabling; and PolarFly, a deterministic diameter-2 topology built on Erdős–Rényi polarity graphs that asymptotically reaches the Moore bound. The two designs embody opposite philosophies: RNG spends topology (longer paths, statistical guarantees) to keep per-hop routing stateless and running on commodity hardware; PolarFly achieves near-optimal scale and path length but is conventionally held back by sparse minimal-path diversity, odd-prime-power size quantization, and cabling complexity.

This paper argues that SRv6 source routing dissolves the central objection to structured low-diameter fabrics — the forwarding-state explosion of k-path routing on commodity ASICs — and proposes **WMP-PolarFly**: a weighted multipath routing design in which SRv6 segment lists and their traffic weights are derived algebraically from the polarity graph's projective-plane coordinates. For any given source-destination pair in the Polarfly fabric, the topology yields one **shortest path (SP)** and a set of **next-shortest-paths (NSPs)** whose count grows with the fabric parameter q; the operator assigns WMP weights across this set (e.g., for q = 7: 40% over the SP and 10% over each of 6 NSPs). We extend the design with multi-plane slicing of high-radix switches, which restores minimal-path redundancy, enables plane-granular hardware heterogeneity, and converts expansion into a purely additive operation. At current 51.2T (512×100G) and forthcoming 102.4T radixes a Polarfly fabric can achieve enormous scale. For example, a 512x100G radix device may be allocated 256x100G for server attachment and 256x100G for fabric attachment *!*. The 256x100G fabric ports map to a  2xq=127 sliced configuration, which creates a dual-plane fabric totaling ~16K ToRs and ~4M server ports at diameter 2 and ~99% Moore-bound efficiency, removing scale as a practical differentiator against RNG.
*`Bruce`*: should we innclude a footnote at the *!* which explains the math would technically add up to 258x100G server ports and 254x100G fabric ports?

Finally, we examine the AI backend case, where the recently published MRC (Multipath Reliable Connection) transport — already deployed with SRv6 path steering on frontier training clusters — supplies exactly the missing ingredient for structured fabrics: reorder-tolerant, per-packet multipath spraying with path-aware congestion control. We show that MRC's path-set abstraction maps naturally onto PolarFly's enumerable, algebraically derivable SP + NSP sets, yielding a backend fabric design that combines deterministic diameter-2 latency, near-Moore per-bit cost efficiency, and transport-layer failure resilience. We examine the applicability of both topologies across deployment regimes — from elastic multi-tenant fleets to fixed-footprint AI training clusters — and argue that the choice between them is driven by operating model rather than by scale or raw performance.

---

## 1. Introduction

The fat tree's stark trade between cost and oversubscription is well documented: hierarchical structure pins traffic between endpoint pairs to small link subsets that congest while the rest of the fabric idles. Capacity is stranded structurally, not incidentally. Flat topologies — direct ToR-to-ToR interconnects with no aggregation or spine layers — have promised an escape for over a decade, but until 2026 no hyperscaler had deployed one in production.

That changed with Amazon's RNG (Resilient Network Graphs), now the default fabric for most new AWS datacenter builds. RNG validates the flat-topology thesis at production scale: 69% fewer routers, up to 33% higher throughput, 9–45% lower cost than equivalently oversubscribed fat trees. Its enabling contributions are a routing protocol (Spraypoint) that extracts near-degree edge-disjoint path counts from a quasi-random graph using only commodity ECMP, and a passive optical device (the ShuffleBox) that reduces random-graph cabling complexity to fat-tree levels.

RNG's authors frame randomness as the only practical route to a flat fabric, dismissing structured constructions (Slim Fly, Xpander) on the grounds that k-shortest-path routing cannot be realized on commodity switch memory. **K-shortest-path routing** maintains multiple pre-computed forwarding paths (typically 4–16) between each pair of endpoints. Unlike standard ECMP, which distributes traffic across multiple paths of *equal* cost, k-shortest-path uses paths that may vary in length and metric — trading simplicity for richer load-balancing options at the cost of proportionally more forwarding table entries. This paper contests the RNG framing. The dismissal assumes hop-by-hop path state — MPLS tunnels, VRF multiplication, or conventional source-based forwarding — and does not engage with SRv6 uSID source routing. SRv6 uSID moves path state out of transit ASICs entirely: the encapsulation node holds the policy; transit nodes perform a single longest-prefix match on the uSID carrier. The forwarding-state objection, once removed, reveals that a Moore-bound-optimal structured graph holds per-bit efficiency and latency advantages that no random topology can match — and that these advantages compound with every silicon generation.

We develop this argument through PolarFly, the diameter-2 topology of Lakhotia et al. (SC22), and a routing design we call WMP-PolarFly (Weighted Multi-Path PolarFly). Section 2 reviews both topologies and identifies a structural irony we call the *path diversity inversion*. Section 3 presents the routing design, including algebraic path derivation and principled weight selection. Section 4 introduces multi-plane slicing for high-radix switches. Section 5 examines scale at 51.2T/102.4T radix. Section 6 compares failure models. Section 7 — the backend case — integrates MRC packet spraying. Section 8 offers a side-by-side analysis and identifies the regimes where each design wins.

A practical note: while RNG is production-proven at Amazon, it is not a publicly available solution. Spraypoint has not been open-sourced; the RNG paper describes the protocol's design but Amazon has not released code or a NOS implementation. ShuffleBoxes are custom passive optical devices with no known commercial source. A non-Amazon operator wishing to deploy RNG today would need to implement Spraypoint from the paper's description on their own NOS, fabricate or commission ShuffleBoxes, and validate the combined system — a substantial engineering investment. By contrast, WMP-PolarFly builds on open-source components (FRR, SONiC) and standard SRv6 as specified in RFC 8986 and RFC 9256.
*`Bruce`*: I moved this paragraph down as it feels more like an addendum to section 1

> **[FIGURE 1 placeholder: side-by-side — generalized fat tree, RNG quasi-random graph, PolarFly ER_q structure for small q]**

---

## 2. Two Flat Topologies, Two Philosophies

### 2.1 RNG: engineered randomness

RNG interconnects routers as a quasi-random graph — a mix of randomized and deterministic cabling segments that reproduces the statistical properties of a true random graph, which is an asymptotically optimal expander. Physical ports are broken out into individual lanes (e.g., 400G into 4×100G), each forming an adjacency with a different remote router; degree *d* and node count *n* are free parameters, and heterogeneous degrees are supported natively.

Routing is Spraypoint: demand-oblivious, fully distributed, ECMP-only. The source "sprays" flows (not per-packet) across its full neighbor set (flow-level 5-tuple hashing; flows stay ordered and stock TCP/NICs are not modified), and traffic converges on the destination through *waypoint* levels, randomly selected neighbor sets fanning in toward the target. The construction yields a number of edge-disjoint paths close to the node degree, minimally overlapping across endpoint pairs — the source of RNG's capacity fungibility. The cost is path length: sprayed paths typically traverse 4–5 hops (1 spray hop to a random neighbor, then 2–3 additional hops via waypoint convergence toward the destination, plus the final hop), compared to PolarFly's worst case of 2 hops for SP and 3 hops for NSP. The RNG hop tax is accepted in exchange for diversity and statelessness.

Cabling uses ShuffleBoxes — passive optical devices that internally permute fiber connections, so that chained boxes at planned locations realize a quasi-random global topology with fat-tree-like physical cabling complexity. Critically, this is a *randomness-native* trick: the ShuffleBox works because RNG only needs the wiring's statistics to be right, not any specific edge set.
*`Bruce`*: should the practical note about RNG public availability actually go here?

### 2.2 PolarFly: structured optimality

PolarFly is the first diameter-2 topology to asymptotically reach the Moore bound, exceeding 96% of theoretical peak at practical radixes — i.e., it packs nearly the maximum possible number of nodes for its degree and diameter. Every router pair is at most two hops apart allowing for flat topologies of very wide diameter. PolarFly also offers roughly 50% more feasible degrees than Slim Fly, the prior state of the art, and supports modular incremental growth through its cluster structure.

PolarFly ([Lakhotia et al., SC22, arXiv:2208.01695](https://arxiv.org/abs/2208.01695)) connects N = q² + q + 1 routers (with q being an **odd** prime number or prime power) with fabric degree q + 1, as the Erdős–Rényi polarity graph ER_q derived from the projective plane PG(2, q). The practical consequence: the feasible set is odd primes (3, 5, 7, 11, 13, …) and odd prime powers (9, 25, 27, 49, 81, 121, 125, 243, …). (see also Appendix A). 

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

Two properties make this design distinctive. First, in a Polarfly topology the SP and every NSP are **algebraically derivable** from the source and destination routers' addresses — no need for topology discovery tools such as BGP-LS (Section 3.2). Second, the path state lives entirely in the server/SmartNIC where **encap-node policy memory** is abundant, rather than in table-constrained transit ASICs. This is why WMP-PolarFly works on commodity hardware where tunnel-based k-shortest-path routing cannot (Section 3.1).

### 3.1 State economics: inverting the RNG critique

RNG's quantitative case against k-shortest-path routing: with n = 10K routers, k = 8 paths, and ~4 routers per path, tunnel-based implementations require on the order of 320K forwarding entries per router. Modern commodity switching ASICs offer substantially more forwarding capacity than the 4–16K range RNG's analysis cites (but still under 1M). Even with the larger LPM tables the k-shortest-path state problem scales with n², so even modern ASICs face pressure at 16K+ node fabrics.
*`Bruce`*: BRCM Tomahawk5 indicates >300K IPv6 ALPM entries, so is this a case where Amazon RNG is using old 3.2T or 6.4T XGS boxes? In a q=127 polarfly is k=8 paths and 4 routers per path be reasonable, or would those numbers actually be much higher, and thus push k-shortest-paths well above 320K?

SRv6 uSID restructures the problem entirely. Each SP and NSP segment list fits within a single uSID carrier — in most cases no SRH is required at all. The SP + NSP set for all destinations concentrates at encapsulation nodes as O(k·n) segment lists in host or edge policy memory (which is cheap and abundant), while the transit FIB holds only the node-SID table and uA adjacency table: O(n), plain LPM, no per-path entries, no tunnels, no VRF multiplication. The fabric ASICs remain **minimal-state** — arguably carrying less state than RNG's, since they bear no ECMP group pressure (Section 5.3). The intelligence relocates to the encap point, where memory is abundant and the computation is — as the next section shows — a direct formula that can be evaluated without any iterative algorithm or external lookup.

### 3.2 Algebraic path derivation

The property that elevates WMP-PolarFly beyond generic source routing on a low-diameter graph: **the SP and NSP set is algebraically derivable**. Vertices of ER_q are points of PG(2, q); adjacency is the polarity (orthogonality) relation. The unique common neighbor of two non-adjacent vertices — the relay node of the SP — is computable directly from their projective coordinates via finite-field arithmetic. The NSP set (on the order of q edge-disjoint 3-hop paths; total pair connectivity ≈ q + 1, with exact counts varying for the self-conjugate, degree-q vertices) is likewise enumerable from coordinates.

In practical terms: for any pair of routers in a q = 7 fabric, the topology guarantees exactly **1 SP** (2 hops through a single relay node) and approximately **6 NSPs** (3 hops each, through different intermediate nodes). The remarkable property is that *which* nodes serve as relays is computable directly from the routers' addresses — no routing protocol is needed to discover these paths. Here is how that computation works:

**Worked example (q = 7).** In a q = 7 WMP-PolarFly fabric — 57 routers, each with 8 fabric ports (or 7, for self-conjugate nodes) — every router has a 3-digit address in mod-7 arithmetic: its projective coordinate, e.g., (1, 3, 5). Two routers are directly cabled if the dot-product of their coordinates equals zero mod 7. Suppose router A = (1, 0, 2) wants to reach router C = (1, 4, 6). They are not directly connected (1·1 + 0·4 + 2·6 = 13 ≡ 6 mod 7 ≠ 0). To find the SP relay — the one common neighbor B — we solve for coordinates (b₀, b₁, b₂) such that A·B = 0 and B·C = 0 simultaneously, i.e., b₀ + 2b₂ ≡ 0 and b₀ + 4b₁ + 6b₂ ≡ 0, both mod 7. This is a system of two linear equations in projective space, yielding exactly one solution (up to scalar multiple): the relay node B. The encap node at A performs this computation — two inner products and a linear solve in mod-7 arithmetic — and emits the SRv6 segment list [uSID-B, uSID-C] for the SP. The same coordinate arithmetic enumerates the 6 NSPs for A→C, each via a different first-hop neighbor that is *not* the direct relay, producing 6 additional segment lists.

The control-plane consequence is significant: **no path-computation protocol exists in this design**. To be precise: there is still a lightweight routing protocol (IS-IS or BGP) for node-SID distribution and liveness detection — the fabric must know *which* routers are alive. But the function traditionally performed by RSVP-TE, PCE, or CSPF — *discovering and computing paths* — is eliminated entirely. The encap node synthesizes the full SP + NSP segment-list set from the destination's coordinates alone. Where Spraypoint must compute and disseminate waypoint levels by protocol, WMP-PolarFly's paths are implicit in the topology's algebra. This is a built-in structural simplicity.

### 3.3 Weighted multipath (WMP)

Traffic between a source-destination pair splits across the derived SP and NSP segment lists with explicit weights: a fraction w_SP on the shortest path and (1 − w_SP) spread across the NSP set.

In plain terms: at small fabric sizes (low q), giving the SP a larger share of traffic makes sense — it is the most efficient path (2 hops vs. 3), and there are only a few NSP alternatives to spread across. As the fabric grows (higher q), the NSP count increases roughly with q, and each individual NSP carries proportionally less traffic. The optimal strategy shifts: spread more traffic across the larger NSP set, because concentrating on the single SP wastes the path diversity the topology provides. At q = 7, a 40/60 split (40% SP, 10% each across 6 NSPs) loads the SP at roughly 4× the per-path rate of each NSP — a reasonable allocation, since the 2-hop path consumes fewer link-traversals per bit. At q = 127, the same 40% on one path out of ~128 would be grossly imbalanced; the weight shifts toward a more even distribution.

We deliberately specify the weight as a **derived function, not a constant**. The optimal demand-oblivious split follows from the same capacity accounting underlying the Valiant/UGAL literature, and a single path's share of total pair capacity shrinks as 1/(q + 1). The weight formula is not a tuning knob the operator must guess at — though operators *can* override it for specific traffic patterns.

The weight function takes as inputs: q; the path-length ratio (2 vs. 3 hops); the pair type (Section 3.4); and — critically for incremental deployment — the **live-vertex set**. In a partially built fabric, the SP relay between a live pair may not yet be installed; the encap node detects this from the installed-coordinate set and re-derives weights over the realized subgraph, again with no protocol convergence. Conditional weighting over the realized subgraph is, to our knowledge, novel, and is among the elements identified for internal invention disclosure.

> **[FIGURE 2 placeholder: WMP weight as a function of q; SP vs. per-NSP load curves]**

### 3.4 What RNG retains

**Heterogeneous router degrees.** RNG supports switches with different port counts in a single fabric. If a new-generation switch has 64 ports and the existing fleet has 32, the new switch simply takes more neighbors — the random graph's statistical properties degrade gracefully rather than breaking. In principle, operators can also vary the server-to-fabric port ratio per switch. In practice, the RNG paper does not quantify how path diversity and Spraypoint's load-balancing guarantees degrade as the degree distribution becomes uneven — a heavily lopsided mix (some switches at degree 16, others at degree 64) would weaken expansion properties for the low-degree nodes even though the graph remains connected and routable. WMP-PolarFly is not as flexibile as it requires uniform degree within each plane; the multi-plane slicing of Section 4 provides a coarser but operationally cleaner heterogeneity model (e.g., a 400G plane alongside a 100G plane).

**Unquantized sizing and continuous growth.** RNG can be built at any node count *n* — 2,073 or 13,067, whatever the building needs. PolarFly is quantized to q² + q + 1 for the available odd prime powers, and growth beyond the chosen q is a forklift. At modern radix this constraint is mild (see q = 127) and partial deployment within a chosen q is additive. For example:

q = 7 | Radix 16 | 57 switches
q = 61 | Radix 128 | 3,783 switches
q = 127 | Radix 256 | 16,257 switches
*`Bruce`*: can you convert this to a markdown table?

However, the maximum WMP-Polarfly fabric size is locked to the math and the operator must pick q at design time and live with the ceiling.

**Stateless operational philosophy.** RNG's transit routers hold destination-based LPM and ECMP groups — the same state any IP router carries. There are no policies, no segment lists, no per-pair configuration anywhere in the fabric. The fabric cannot be misconfigured because it holds no per-path configuration to get wrong. WMP-PolarFly concentrates correctness in the encap-node policy computation. The computation is algebraically deterministic (Section 3.2), but it *is* computation — and the encap node must be right. RNG spends topology to keep routing minimal-state; WMP-PolarFly spends routing intelligence to keep topology optimal.

Sections 4 and 5 narrow the gap on heterogeneity and scale; Section 8 names the regimes where each bet wins.

---

## 4. Multi-Plane Slicing

PolarFly's odd-prime-power quantization and uniform-degree requirement soften considerably once switch radix substantially exceeds the desired fabric degree. We treat a single physical switch as a member of multiple logical PolarFly *planes*.
*`Bruce`*: can we re-phrase this "PolarFly's odd-prime-power quantization and uniform-degree requirement soften considerably once switch radix substantially exceeds the desired fabric degree." What are we trying to communicate with this sentence?

For reference, the following table shows the fabric sizes available at selected values of q:

| q | Type | N = q²+q+1 (switches) | Fabric degree (q+1) | Notes |
|---|---|---|---|---|
| 7 | prime | 57 | 8 | Lab validation target |
| 31 | prime | 993 | 32 | Dual-plane on 64-port switch |
| 61 | prime | 3,783 | 62 | Max single-plane on 64-port |
| 127 | prime | 16,257 | 128 | Dual-plane on 512-port (51.2T) |
| 251 | prime | 63,253 | 252 | Single-plane on 512-port |
| 509 | prime | 259,591 | 510 | Future 102.4T single-plane |

### 4.1 Dual-plane: every switch in both planes

A 64-port switch (fabric-degree ceiling q = 61, and 64 = 2⁶ is excluded as even characteristic) can instead run as 2×32 fabric ports across two parallel q = 31 planes over the same vertex set. What this buys:
*`Bruce`*: this introductory sentence is confusing. Let's create an example and intro discussion using a baseline 12.8T switch with 128x100G radix. In this case we use q=61 (61 fabric ports, then anywhere from 61-67 server ports depending on oversubscription). However, the 128x100G switch can also be 2xq=31 providing 62 fabric ports (31 to each plane) and 62-66 server ports - a more optimal port utilization and dual-plane redundancy/load balancing, etc. The 2xq=31 example means we lose scale vs. q=61 (2x993 switches vs. 3783 switches), but we gain in bisectional bandwidth. The sweetspot for q value appears to be 127 (16k switches) as operating single-plane fabrics using super-high radix q values (251, 509, etc.) far exceed any known or planned DC size.

**Minimal-path redundancy.** Every pair now holds two edge-disjoint minimal paths, one per plane. The discrete failure transition of single-plane PolarFly — minimal path dies, 2-hop traffic steps to 3-hop with a visible RTT shift — largely disappears: the flow hash already had a length-identical twin in the surviving plane, and only a weight rebalance remains.

**Plane-granular heterogeneity.** Each plane is internally uniform, but planes may differ: a 400G plane beside a 100G plane, with WMP weights proportional to plane bandwidth. A hardware refresh becomes "stand up a new plane" — coarser than RNG's per-node degree mixing, but a far saner operational unit.

**Additive expansion.** Because the complete edge set of each plane is known in advance, growth never breaks an existing link: a landing router patches into q + 1 pre-planned positions per plane. With pre-provisioned passive patch frames carrying the polarity-graph permutation — the structured analogue of the ShuffleBox, though it must encode the *specific* edge set rather than a blind permutation — PolarFly expansion is arguably cleaner than RNG's break-and-splice appendix. The residual costs: q is a day-1 ceiling (the next odd prime power is a forklift), and the partial graph's path multiplicity is nonuniform, which the live-vertex-aware weight function of Section 3.3 absorbs.

The price is scale-per-port: the same 993 chassis running one q = 61 plane instead of two q = 31 planes would reach 3,783 switches. The Moore bound goes as q², so halving the radix quarters the reach; parallel planes over the same vertex set buy redundancy, not size. Slicing closes the failure-continuity and heterogeneity gaps against RNG while widening the scale gap — an excellent trade at 1–2K switches, a poor one at hyperscale. Section 5 shows that modern radix dissolves the dilemma.
*`Bruce`*: I believe the last sentence is incorrect and contradicted by 5.1. Polarfly doesn't need to compete with RNG on scale (q=509 is 260k switches). Rather, polarfly needs to address HA, heterogeneity, and available bandwidth, which we largely do with 4.1

### 4.2 k-plane membership and the intersection trick

Generalizing, let each switch join 2 of k planes. Reachability at diameter 2 requires the memberships of any pair to intersect. For **k = 3**, any two 2-subsets of {A, B, C} necessarily share a plane: diameter 2 is preserved globally while scaling to 3·993/2 ≈ 1,489 switches on 64-port hardware. Path multiplicity becomes pair-type-dependent — same-type pairs (both AB) share two planes and enjoy dual minimal paths; cross-type pairs share exactly one — and the pair type is simply two more coordinates in the address, so the weight derivation remains closed-form.
*`Bruce`*: k is a confusing variable here. Does it mean the same thing as k in k-shortest-paths? Also, I don't understand the math of this paragraph, can you explain it more simply?

At k ≥ 4 disjoint memberships appear (AB vs. CD): such pairs share no plane and must transit a bridging switch, giving bounded diameter 4 (2 hops in the source plane to a bridge whose membership intersects both, 2 in the destination plane) — still coordinate-derivable, but no longer diameter-2. At this point the construction is effectively a hand-rolled star product, and the honest comparison is no longer against vanilla PolarFly but against **PolarStar** (the diameter-3 star product of ER_q with Paley or inductive-quad graphs — the literature's official answer to scaling past q² + q + 1) and BundleFly. Our expectation, to be validated: PolarStar wins on scale-per-port; k-plane slicing wins on plane-granular heterogeneity and operational modularity.

> **[FIGURE 3 placeholder: k=3 plane membership diagram; pair-type path multiplicity table]**

To our knowledge, plane-membership combinatorics used as the *diameter-preservation mechanism*, with cross-plane WMP weights derived from pair-type labels, is novel; it is the second element identified for invention disclosure.
*`Bruce`*: these two paragraphs seem out of place unless we want to include a discussion of N-S traffic entering and leaving the Polarfly cluster. Or perhaps I'm just not seeing what they're trying to say (I definitely want to preserve potential novelty for future patent filing!). Are these paragraphs describing multi-planar scenarios where we might take 512x100G radix switches and slice them across 3 planes (q=83?) or 4 planes (q=61)?

---

## 5. Scale at Modern Radix

### 5.1 The Moore ceiling moves above building size

Radix growth is asymmetric between the two designs: it repairs PolarFly's largest weakness while only marginally improving RNG's position.

At 51.2T (512×100G effective lanes), q = 127 yields a 16,257-switch plane at fabric degree 128 — against a Moore bound of d² + 1 = 16,385, i.e., **99% of the theoretical maximum reach for diameter 2**. A pure-transit 4×q=127 configuration is possible but leaves no room for server attachment ports; the realistic ToR-integrated build is **2×q=127** — 256 lanes fabric, 256 lanes server downlink — giving 16,257 ToRs × 256 ports ≈ **4M attachment points at 1:1, dual minimal paths, diameter 2**. That exceeds the footprint of any single building in production today. Carving the 512x100G fabric into 4 slices (q = 61) gives us 3783 switches and nearly 1M attachment points, which still far exceeds the compute footprint of any single DC building.
*`Bruce`*: I simplified this paragraph. Please feel free to edit my 'Carving' sentence for accuracy. Also, I think the current largest DC buildings in the world might house up to 1M servers (maybe?). So it might make sense to use 4xq=61 as our baseline and 2xq=127 as a 'super-scale' reference. If we do that, we lose scale (but at 1M server ports do we care?) and gain on HA and bandwidth. I would be interested in getting your opinion on this discussion.

### 5.2 Per-bit economics compound with bandwidth

Fabric capacity consumed per delivered bit is proportional to hop count. The WMP mix runs at roughly L ≈ 2.6 effective hops (weighted across 2-hop minimal and 3-hop non-minimal sets); Spraypoint's spray-plus-waypoint structure runs meaningfully longer — typically 4–5 hops. At 100G lanes this isn't trivial; at 200G per lane and beyond, each extra hop is another traversal of increasingly expensive and power-hungry optics and serdes. A near-Moore fabric at L ≈ 2.6 sits close to the information-theoretic floor of fabric-capacity-per-delivered-bit. RNG's cost case is "up to 45% cheaper than fat tree" — but the fat tree is a soft target; against a Moore-optimal structured fabric, RNG's hop tax becomes an economic consideration, and it grows in absolute dollars and watts with every silicon generation. The structured topology's advantage here strengthens with scale.
*`Bruce`*: I made some minor edits

### 5.3 RNG's pressure points at 16K+ flat nodes

RNG has no topological ceiling, but three practical pressures emerge in this regime. First, the control plane: Spraypoint is a distributed protocol over a flat domain with no hierarchy; dissemination and convergence behavior at 16K+ nodes is unproven, and the published production fabrics are presumably well below it. Second, ECMP hardware: spraying across the full neighbor set implies ECMP groups approaching the lane count, and ASIC ECMP member tables are a finite, contested resource — 512-wide groups per destination class is real pressure even with group sharing. SRv6-WMP-PolarFly sidesteps this entirely: explicit paths consume encap-node policy memory, not transit ASIC tables. Third, expansion recabling complexity scales with d: at d = 512, every rack land touches 256 existing links spread across the building. None of these is fatal — they are engineering, and Amazon has the bodies — but all worsen with radix, while additive pre-planned algebraic expansion improves relatively.
*`Bruce`*: "convergence behavior at 16K+ nodes is unproven" - another reason to maybe consider q=61 or ~4k switches as the reasonable ceiling of today. Or 3xq=83 (~7000 switches)?

---

## 6. Failure Models: Statistical Headroom vs. Repair Logic

RNG's resilience claim is best understood as a claim about *blast-radius shape*, and a precision matters: Spraypoint absolutely reacts to failure — it is a routing protocol in the OSPF/BGP mold and reconverges on topology change. What RNG eliminates is *protection machinery*: no FRR, no precomputed backups, no TI-LFA-style repair, because steady-state forwarding already encodes the redundancy. When a link dies, the adjacent router locally prunes the member from its ECMP groups and traffic redistributes in the data plane instantly; the failed link carried roughly 1/d of any affected pair's capacity, so the loss is a thin statistical shave across many pairs rather than a mode change for any one. There are no special routers; every failure is small and uniform. Protocol convergence cleans up in the background with nothing waiting on it.

Single-plane PolarFly, by contrast, undergoes a discrete transition when a pair's unique minimal path dies: 2-hop traffic steps to the 3-hop set, with an RTT shift congestion control will notice. The response is fast — the encap node re-derives weights algebraically, arguably faster than any IGP floods — but it is a *reaction*, with a detectable before/after. Dual-plane slicing (Section 4.1) converts the transition from a length change into a weight rebalance among length-identical paths, substantially closing the gap; and in the backend deployment of Section 7, MRC moves failure handling into the transport entirely.

The honest framing for operators: PolarFly offers deterministic best-case behavior with discrete failure modes; RNG offers probabilistic behavior with continuous failure modes. Preference depends on whether the workload fears tail latency or fears variance.

---

## 7. The AI Backend: MRC and Packet Spraying on PolarFly

### 7.1 Why the backend is the natural home

RNG's authors explicitly scope to multi-tenant general-purpose fabrics and defer AI training, noting that such workloads may demand rail-optimized structures and local capacity islands that flat random topologies lack. The backend is simultaneously the regime where every PolarFly disadvantage evaporates: the fabric is built once at known size (q ceiling irrelevant), the operator owns the stack end to end (encap intelligence is an asset, not a liability), the hardware population is uniform per build (heterogeneity moot), and per-bit cost and power compound directly into training economics (Section 5.2). Collective-driven traffic additionally rewards deterministic path lengths: flow-completion-time skew across parallel transfers gates the collective, and a hard diameter-2 bound with enumerable path lengths is precisely the property a scheduler can reason about.

What the structured Ethernet fabric has historically lacked in this regime is a transport that can exploit its path set. With MRC that transport now exists.

### 7.2 MRC in brief

MRC (Multipath Reliable Connection), contributed to OCP in May 2026 by OpenAI with AMD, Broadcom, Intel, Microsoft, and NVIDIA, extends RDMA-over-Ethernet semantics so that **a single RDMA connection distributes traffic across multiple network paths**, with reordering tolerated by the transport and congestion managed per path (AMD's NSCC algorithm, now part of the UEC congestion-control specification). It is implemented on shipping 400/800G NICs (ConnectX-8, Pollara, Vulcano, Thor Ultra) with **SRv6 switch support** on Spectrum-4/5 (Cumulus, SONiC) and Tomahawk 5 (EOS), and is deployed in production on OpenAI's largest GB200 clusters (OCI Abilene, Microsoft Fairwater). The companion paper is explicitly titled "Resilient AI Supercomputer Networking using MRC and SRv6." Reported topology practice mirrors the breakout philosophy: rather than one 800G link, the NIC is split into multiple smaller links to create natural path redundancy, enabling two-tier builds at 100K+ GPU scale with roughly two-thirds the optics and 40% fewer switches than three-tier baselines.
*`Bruce`*: Cisco G200 also supports SRv6, but has not yet been implemented in production MRC builds

Three properties matter for our purposes. MRC is **reorder-tolerant**, so per-packet (or per-message-slice) spraying is admissible where general purpose cloud requires per-flow distribution. MRC is **path-aware**, maintaining per-path state and congestion signals within one connection. And MRC's deployed path-steering mechanism **is already SRv6** — the same encapsulation substrate as the WMP-Polarfly design.

### 7.3 The synthesis: per-packet WMP over algebraic path sets

Recall why WMP was specified at flow level (Section 3.3 context): general-cloud tenants run vanilla TCP on stock NICs, and per-packet spraying would have required reorder-tolerant transports that cannot be assumed across an adversarial tenant population. The backend inverts the assumption — every endpoint is an MRC-capable RDMA NIC — and the design strengthens along four axes.

**Spraying granularity.** The WMP weights of Section 3.3 apply per packet rather than per flow. Elephant-flow collision risk — the residual weakness of any flow-hashed scheme, RNG's included — vanishes: a single connection's load spreads across the full minimal-plus-non-minimal path set in proportion to the derived weights. This is, notably, a capability RNG's general-cloud deployment does not have; Spraypoint sprays flows, not packets. 

**Path-set provisioning.** MRC requires each connection to be provisioned with a set of paths (EVs or Entropy Values). On a Clos this set is implicit (ECMP up, ECMP down); on PolarFly it is *explicit and enumerable* — exactly q + 1-ish edge-disjoint segment lists per pair, synthesized from projective coordinates with no path discovery protocol. PolarFly converts MRC's path-set abstraction from a fabric-dependent configuration burden into a direct algebraic computation at connection setup. The diameter-2 bound additionally caps the path-length spread within a connection's set at one hop (2 vs. 3), simplifying the transport's reordering and completion-tracking window relative to a random graph's longer-tailed length distribution.

**Adaptive weighting.** NSCC's per-path congestion signals provide the feedback channel that pure demand-oblivious WMP lacks. The static algebraic weights become *priors*, modulated at the NIC by per-path congestion state — UGAL-like adaptivity realized at the transport rather than in switch hardware, on commodity Ethernet ASICs. The lineage is satisfying: PolarFly's original authors assumed HPC-style adaptive routing in switches; MRC relocates exactly that function to the place the backend operator controls.

**Failure handling.** MRC's headline operational result — switch reboots during frontier training runs without job disruption — derives from per-path health tracking: the transport stops scheduling onto a dead path within one RTT-scale detection window. On PolarFly this composes with algebraic re-derivation: the NIC's transport masks the failure instantly; the encap layer re-synthesizes the path set from the updated live-vertex set in the background; no IGP convergence sits anywhere on the critical path. The discrete-transition concern of Section 6 is fully retired in this deployment model — the surviving paths in the MRC set absorb the weight shift per packet, and dual-plane slicing (where used) makes even the length distribution invariant.

> **[FIGURE 4 placeholder: MRC connection over PolarFly — one minimal + q non-minimal segment lists, per-packet weighted spray, NSCC feedback loop]**

### 7.4 Positioning against MRC's deployed topologies and against RNG

MRC is topology-agnostic and its production deployments to date run on two-tier rail-style Clos fabrics. The proposal here is therefore not MRC-versus-PolarFly but MRC-*on*-PolarFly as the structured direct-topology alternative to MRC-on-Clos: diameter 2 instead of 4-hop worst-case through a spine, ~99% Moore efficiency instead of Clos port overheads, and a path set the transport can enumerate algebraically. The breakout philosophy is shared — MRC deployments already split NICs into multiple lower-rate links for path redundancy, which is precisely the lane-level adjacency model PolarFly's degree budget wants. On the other hand RNG's authors generally concede it is not a great match to collective-driven traffic. A quantitative bake-off — MRC-on-PolarFly vs. MRC-on-Clos at matched port count, on allreduce/all-to-all completion-time distributions — is the natural next experiment and an open invitation in this paper.
*`Bruce`*: made some edits, can you double-check my work/accuracy?

### 7.5 All-to-All collectives and bisection bandwidth

All-to-All is the adversarial traffic pattern for any topology: O(n²) simultaneous flows, uniform demand across every pair. Under full All-to-All, every link in any non-blocking fabric saturates simultaneously, and no topology — Clos, RNG, or PolarFly — escapes bisection-bandwidth limits. The question is not whether PolarFly saturates but how it compares at matched cost.

PolarFly's near-Moore structure gives it close to optimal bisection bandwidth for its degree and node count — structurally higher than a Clos at matched port investment, because Clos strands capacity in its tree hierarchy. Under uniform All-to-All, a diameter-2 fabric with L ≈ 2.6 effective hops consumes roughly half the link-traversals per delivered bit compared to Spraypoint's 4–5 hop paths, meaning PolarFly delivers more aggregate throughput from the same total link budget. This is the per-bit economics argument of Section 5.2 applied to the worst-case traffic matrix.
*`Bruce`*: I got a little confused reading this paragraph the first time...the jump from Clos comparison to Spraypoint and hop count feels abrupt

The practical concern is not aggregate throughput but **incast at individual switches**: in All-to-All, each router receives traffic from all N−1 peers simultaneously. On PolarFly, roughly q+1 of these arrive via direct (1-hop) links, while the remaining ~q² arrive via 2-hop paths through q+1 relay neighbors. Each relay therefore concentrates traffic from ~q senders, creating per-relay load of ~q flows — manageable at q=7 or q=31, but worth modeling carefully at q=127 where each relay carries ~127 simultaneous inbound flows toward the destination. MRC's per-path congestion control (NSCC) provides the backpressure mechanism, and the WMP weights can be adjusted to spread load across the non-minimal 3-hop set when relay congestion is detected. This adaptive rebalancing under All-to-All load is a natural target for simulation validation.
*`Bruce [open]`*: This section is a first pass. The relay-concentration analysis needs simulation to validate, and the interaction between All-to-All incast and NSCC backpressure is the key open question. Worth testing at q=7 in the lab before making strong claims. *`Bruce`*: agreed. How do we feel about incast and 4xq=61?

---

## 8. Scorecard and Conclusions

| Dimension | RNG (quasi-random + Spraypoint) | SRv6-WMP-PolarFly (incl. slicing) | Notes |
|---|---|---|---|
| Scale per port | Unbounded n | ~16K ToRs / ~4M ports at 2×q=127 | Gap closed at ≥51.2T radix |
| Diameter / latency | Probabilistic, longer (≈4–5 hops sprayed) | Deterministic 2 (L ≈ 2.6 effective) | PolarFly; gap grows with optics cost |
| Per-bit cost & power | 9–45% under fat tree | Near Moore-bound floor | Tips to PolarFly; compounds with bandwidth |
| Minimal-path diversity | High (spray), non-minimal | 1 per plane; k planes ⇒ k minimal paths | Slicing closes; backend MRC retires |
| Transit ASIC state | LPM + wide ECMP groups | LPM only; paths in encap memory | PolarFly avoids ECMP table pressure |
| Control plane | Distributed protocol (Spraypoint) | IS-IS/BGP for liveness; paths algebraic | PolarFly, surprisingly |
| Heterogeneity | Per-node degree mixing, in place | Plane-granular | RNG finer; slicing operationally cleaner |
| Incremental growth | Unquantized; break-and-splice | Additive to q ceiling; pre-planned | Different shapes; PolarFly cleaner per step |
| Failure model | Continuous, statistical, no protection logic | Discrete → continuous with planes/MRC | RNG single-plane; parity with slicing+MRC |
| Operational philosophy | Stateless fabric, minimal-state everywhere | Intelligence concentrated at encap | The irreducible difference |
| Availability | Amazon-internal; not open-sourced | Open standards (SRv6), open NOS (SONiC/FRR) | PolarFly deployable today |

The two topology families do not converge with scale; they sort by operating model. **Engineered randomness wins the elastic-fleet regime**: daily rack lands, rolling hardware generations, adversarial multi-tenant traffic, and an operational culture that prizes a fabric incapable of holding misconfiguration. **Structured optimality wins the deliberate-fabric regime**: build-once footprints, operator-owned stacks, per-bit economics that compound, and workloads — above all AI training collectives — that reward deterministic latency and enumerable paths. Modern radix removes scale as a discriminator; SRv6 removes the forwarding-state objection; MRC removes the transport objection. What remains is a genuine philosophical choice about where complexity should live, and the thesis of this paper is that for the backend, the answer has quietly become the encap node.

The boundary between regimes is less sharp than the literature implies. A fixed-footprint general-cloud datacenter — a sovereign cloud build, a large enterprise private cloud, a neocloud region — shares many characteristics of the "deliberate-fabric" regime: known size at build time, operator-owned stack, uniform hardware generation. SRv6-WMP-PolarFly is a legitimate candidate for such deployments, and the remaining RNG advantages in that context (unquantized n, per-node heterogeneity) are operational preferences rather than hard technical requirements. The interesting open question is not "which topology for cloud?" but whether "general cloud" is really one regime at all.

A closing observation on the literature: RNG's published case is argued against the fat tree, and its dismissal of structured alternatives rests on a forwarding-state analysis that predates compressed source routing as a deployable mechanism. The comparison that matters next is not flat-versus-tree but structured-flat-versus-random-flat — and on current silicon, with current transports, that comparison is live.

---

## 9. Open Questions and Future Work

The quantitative bake-offs this paper motivates: k-plane sliced PolarFly versus PolarStar and BundleFly at matched port count (minimal-path multiplicity, worst-case diameter, cost); the closed-form optimal WMP weight function w(q, pair-type, live-vertex set, plane bandwidths) against simulated optima across traffic matrices; MRC-on-PolarFly versus MRC-on-Clos on collective completion-time distributions at 100K-GPU scale, with specific attention to All-to-All relay concentration effects; Spraypoint convergence behavior and ECMP-table occupancy at 16K+ flat nodes (an RNG question, but one whose answer calibrates this comparison); and the passive patch-frame design encoding polarity-graph permutations — whether the structured analogue of the ShuffleBox can match its manufacturing economics given that it must realize a specific rather than statistical edge set.

Patent-relevant elements consolidated for internal disclosure: (1) algebraically derived WMP weights as a function of q, pair type, live-vertex set, and plane bandwidths; (2) k=3 pairwise-intersecting plane membership as a diameter-preservation mechanism with pair-type-derived cross-plane weights; (3) plane-granular heterogeneity model; (4) MRC path-set provisioning via closed-form coordinate synthesis with congestion-modulated algebraic priors. *(Prior-art caveats from internal discussion apply: WCMP, RFC 9256 weighted candidate paths, and UGAL/Valiant minimal/non-minimal splits are established; novelty concentrates in topology-specific algebraic derivation.)*

---

## References (to be completed)

*Placeholder — full citations to be added:* Bernardi et al., "Expanding into Reality: Random Graphs for Datacenter Networks" (RNG), arXiv:2604.15261, 2026 · Lakhotia et al., "PolarFly: A Cost-Effective and Flexible Low-Diameter Topology," SC22, [arXiv:2208.01695](https://arxiv.org/abs/2208.01695) · Lakhotia et al., PolarStar · Singla et al., "Jellyfish: Networking Data Centers Randomly," NSDI 2012 · Valadarsky et al., "Xpander," 2016 · Besta & Hoefler, "Slim Fly," SC14 · OpenAI et al., MRC specification, OCP, May 2026 · OpenAI et al., "Resilient AI Supercomputer Networking using MRC and SRv6" · Zhou et al., "WCMP: Weighted Cost Multipathing," EuroSys 2014 · RFC 9256 (SR Policy Architecture) · RFC 8986 (SRv6 Network Programming) · Erdős–Rényi polarity graph / Brown graph literature · EvalNet toolchain, arXiv:2105.12663.

---

## Changelog

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
- Bruce's review comments preserved as *`Bruce [status]`* annotations
