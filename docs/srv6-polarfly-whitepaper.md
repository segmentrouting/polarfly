# Structured Optimality vs. Engineered Randomness: SRv6 Routing on PolarFly Topologies as an Alternative to Random-Graph Datacenter Fabrics

**Author:** Bruce [LASTNAME]
**Status:** DRAFT v0.1 — for internal review
**Date:** June 2026

---

## Abstract

Two flat datacenter topologies now offer credible alternatives to the fat tree: Amazon's RNG, a quasi-random expander fabric deployed in production with the Spraypoint routing protocol and ShuffleBox passive optical cabling; and PolarFly, a deterministic diameter-2 topology built on Erdős–Rényi polarity graphs that asymptotically reaches the Moore bound. The two designs embody opposite philosophies: RNG spends topology (longer paths, statistical guarantees) to keep per-hop routing stateless and stupid; PolarFly achieves near-optimal scale and path length but is conventionally held back by sparse minimal-path diversity, prime-power size quantization, and cabling complexity.

This paper argues that SRv6 source routing dissolves the central objection to structured low-diameter fabrics — the forwarding-state explosion of k-path routing on commodity ASICs — and proposes **WCMP-SRv6-PolarFly**: a weighted multipath routing design in which segment lists and their traffic weights are derived algebraically from the polarity graph's projective-plane coordinates, with no path-computation protocol. We extend the design with multi-plane slicing of high-radix switches, which restores minimal-path ECMP redundancy, enables plane-granular hardware heterogeneity, and converts expansion into a purely additive operation. At current 51.2T (512×100G) and forthcoming 102.4T radixes, a 2×q=127 sliced configuration reaches ~16K ToRs and ~4M server ports at diameter 2 and ~99% Moore-bound efficiency, removing scale as a practical differentiator against RNG.

Finally, we examine the AI backend case, where the recently published MRC (Multipath Reliable Connection) transport — already deployed with SRv6 path steering on frontier training clusters — supplies exactly the missing ingredient for structured fabrics: reorder-tolerant, per-packet multipath spraying with path-aware congestion control. We show that MRC's path-set abstraction maps naturally onto PolarFly's enumerable, algebraically derivable path sets, yielding a backend fabric design that combines deterministic diameter-2 latency, near-Moore per-bit cost efficiency, and transport-layer failure resilience. We conclude that the two topology families sort cleanly by operating model rather than by scale: engineered randomness wins where fleets churn and tenants are adversarial strangers; structured optimality wins where fabrics are built deliberately and the operator owns the stack end to end.

---

## 1. Introduction

The fat tree's stark trade between cost and oversubscription is well documented: hierarchical structure pins traffic between endpoint pairs to small link subsets that congest while the rest of the fabric idles. Capacity is stranded structurally, not incidentally. Flat topologies — direct ToR-to-ToR interconnects with no aggregation or spine layers — have promised an escape for over a decade, but until 2026 no hyperscaler had deployed one in production.

That changed with Amazon's RNG (Resilient Network Graphs), now the default fabric for most new AWS datacenter builds. RNG validates the flat-topology thesis at production scale: 69% fewer routers, up to 33% higher throughput, 9–45% lower cost than equivalently oversubscribed fat trees. Its enabling contributions are a routing protocol (Spraypoint) that extracts near-degree edge-disjoint path counts from a quasi-random graph using only commodity ECMP, and a passive optical device (the ShuffleBox) that reduces random-graph cabling complexity to fat-tree levels.

RNG's authors frame randomness as the only practical route to a flat fabric, dismissing structured constructions (Slim Fly, Xpander) on the grounds that k-shortest-path routing cannot be realized on commodity switch memory. This paper contests that framing. The dismissal assumes hop-by-hop path state — MPLS tunnels, VRF multiplication, source-address forwarding — and does not engage with compressed source routing. SRv6 uSID moves path state out of transit ASICs entirely: the encapsulation node holds the policy; transit nodes perform a single longest-prefix match on the uSID carrier. The forwarding-state objection, once removed, exposes the underlying topology question on its merits — and on the merits, a Moore-bound-optimal structured graph holds advantages that strengthen with every silicon generation.

We develop this argument through PolarFly, the diameter-2 topology of Lakhotia et al. (SC22), and a routing design we call WCMP-SRv6-PolarFly. Section 2 reviews both topologies and identifies a structural irony we call the *path diversity inversion*. Section 3 presents the routing design, including algebraic path derivation and principled weight selection. Section 4 introduces multi-plane slicing for high-radix switches. Section 5 examines scale at 51.2T/102.4T radix. Section 6 compares failure models. Section 7 — the backend case — integrates MRC packet spraying. Section 8 offers an honest scorecard and identifies the regimes where each design wins.

> **[FIGURE 1 placeholder: side-by-side — generalized fat tree, RNG quasi-random graph, PolarFly ER_q structure for small q]**

---

## 2. Two Flat Topologies, Two Philosophies

### 2.1 RNG: engineered randomness

RNG interconnects routers as a quasi-random graph — a mix of randomized and deterministic cabling segments that reproduces the statistical properties of a true random graph, which is an asymptotically optimal expander. Physical ports are broken out into individual lanes (e.g., 400G into 4×100G), each forming an adjacency with a different remote router; degree d and node count n are free parameters, and heterogeneous degrees are supported natively.

Routing is Spraypoint: demand-oblivious, fully distributed, ECMP-only. The source "sprays" across its full neighbor set (flow-level 5-tuple hashing — not per-packet; flows stay ordered and stock TCP/NICs are untouched), and traffic converges on the destination through *waypoint* levels, randomly selected neighbor sets fanning in toward the target. The construction yields a number of edge-disjoint paths close to the node degree, minimally overlapping across endpoint pairs — the source of RNG's capacity fungibility. The cost is path length: sprayed paths run meaningfully longer than shortest paths, a hop tax accepted in exchange for diversity and statelessness.

Cabling uses ShuffleBoxes — passive optical devices that internally permute fiber connections, so that chained boxes at planned locations realize a quasi-random global topology with fat-tree-like physical cabling complexity. Critically, this is a *randomness-native* trick: the ShuffleBox works because RNG only needs the wiring's statistics to be right, not any specific edge set.

### 2.2 PolarFly: structured optimality

PolarFly connects N = q² + q + 1 routers (q a prime power) with fabric degree q + 1, as the Erdős–Rényi polarity graph ER_q derived from the projective plane PG(2, q). It is the first diameter-2 topology to asymptotically reach the Moore bound, exceeding 96% of theoretical peak at practical radixes — i.e., it packs nearly the maximum possible number of nodes for its degree and diameter. Every router pair is at most two hops apart, by construction, deterministically. PolarFly also offers roughly 50% more feasible degrees than Slim Fly, the prior state of the art, and supports modular incremental growth through its cluster structure.

### 2.3 The path diversity inversion

ER_q is C4-free: any two vertices share at most one common neighbor. This is precisely *why* it approaches the Moore bound — four-cycles waste edges — and it has a sharp routing consequence: between most non-adjacent pairs there exists **exactly one** minimal (2-hop) path. Moore-bound optimality and minimal-path diversity are structurally in tension; the closer a graph sits to the bound, the sparser its shortest paths.

The irony is that RNG begins from the same observation. Spraypoint exists because shortest-path routing on expanders congests singleton shortest paths; its answer is to abandon minimality and let randomness supply diversity. PolarFly's conventional answer (inherited from the Slim Fly / Dragonfly lineage) is non-minimal adaptive routing — UGAL-style congestion-sensed deflection — which implicitly assumes HPC-class adaptive-routing hardware. Neither answer is available to a structured topology on commodity Ethernet ASICs with conventional routing.

SRv6 source routing is the third answer, and it changes the economics entirely.

---

## 3. WCMP-SRv6-PolarFly

### 3.1 State economics: inverting the RNG critique

RNG's quantitative case against k-path routing: with n = 10K routers, k = 8 paths, ~4 routers per path, tunnel-based implementations require on the order of 320K forwarding entries per router against the 4–16K such entries commodity ASICs actually support — a 20–80× gap that state-reduction techniques cannot bridge.

SRv6 uSID restructures the problem. A 3-hop explicit path through a diameter-2 fabric fits within a single uSID carrier — in most cases no SRH is required at all. Path state concentrates at encapsulation nodes as O(k·n) segment lists in cheap policy memory (host or edge), while the transit FIB holds only the node-SID table: O(n), plain LPM, no per-path entries, no tunnels, no VRF multiplication. The fabric ASICs remain as "stupid" as RNG's — arguably stupider, since they carry no ECMP group pressure (Section 5.3). The intelligence relocates to the encap point, where memory is abundant and the computation is, as the next section shows, closed-form.

### 3.2 Algebraic path derivation

The property that elevates this design beyond generic source routing on a low-diameter graph: **PolarFly's path set is algebraically derivable**. Vertices of ER_q are points of PG(2, q); adjacency is the polarity (orthogonality) relation. The unique common neighbor of two non-adjacent vertices — the relay of the unique minimal path — is computable directly from their projective coordinates via finite-field arithmetic. The non-minimal path set (on the order of q edge-disjoint 3-hop paths; total pair connectivity ≈ q + 1, with exact counts varying for the self-conjugate, degree-q vertices) is likewise enumerable from coordinates.

The control-plane consequence is significant: **no path computation protocol exists in this design**. No SPF, no link-state flooding for path discovery, no PCE. The encap node synthesizes the full minimal-plus-non-minimal segment-list set from the destination's coordinates alone. Where Spraypoint must compute and disseminate waypoint levels by protocol, PolarFly's waypoints are implicit in the topology's algebra. This is a structural simplicity advantage on what is normally RNG's strongest ground.

### 3.3 Weighted multipath (W-CMP)

Traffic between a pair splits across the derived segment lists with explicit weights: a fraction w_min on the unique minimal path and (1 − w_min) spread across the non-minimal set. We deliberately specify the weight as a **derived function, not a constant**. A fixed split (e.g., 40/60) loads the minimal path at roughly 4–5× the per-path rate of each non-minimal path at q = 7 — defensible there, since the 2-hop path consumes fewer link-traversals per bit and "deserves" proportionally more — but the optimal demand-oblivious split follows from the same capacity accounting underlying the Valiant/UGAL literature, and it shifts toward the non-minimal set as q grows: a single path's share of total pair capacity shrinks as 1/(q + 1).

The weight function takes as inputs: q; the path-length ratio (2 vs. 3 hops); the pair type (Section 3.4); and — critically for incremental deployment — the **live-vertex set**. In a partially built fabric, the unique minimal relay between a live pair may not yet be installed; the encap node detects this from the installed-coordinate set and re-derives weights over the realized subgraph, again with no protocol convergence. Conditional weighting over the realized subgraph is, to our knowledge, novel, and is among the elements identified for internal invention disclosure.

> **[FIGURE 2 placeholder: W-CMP weight as a function of q; minimal vs. non-minimal per-path load curves]**

### 3.4 What RNG retains

Honesty requires stating where engineered randomness keeps decisive advantages. RNG supports heterogeneous router degrees in a single graph, arbitrary unquantized n, and continuous incremental growth (at the cost of break-and-splice recabling, managed by phased-expansion planning). Its failure mode is purely statistical (Section 6). And its operational philosophy — *the fabric cannot be misconfigured because it holds no configuration* — is an argument hyperscale operators feel in their incident-review bones, independent of throughput numbers. RNG spends topology to keep routing stupid; WCMP-SRv6-PolarFly spends routing intelligence to keep topology optimal. Sections 4 and 5 narrow the gap; Section 8 names the regimes where each bet wins.

---

## 4. Multi-Plane Slicing

PolarFly's prime-power quantization and uniform-degree requirement soften considerably once switch radix substantially exceeds the desired fabric degree. We treat a single physical switch as a member of multiple logical PolarFly *planes*.

### 4.1 Dual-plane: every switch in both planes

A 64-port switch (fabric-degree ceiling q = 61; 63 is not a prime power) can instead run as 2×32 fabric ports across two parallel q = 31 planes over the same vertex set. What this buys:

**Minimal-path ECMP redundancy.** Every pair now holds two edge-disjoint minimal paths, one per plane. The discrete failure transition of single-plane PolarFly — minimal path dies, 2-hop traffic steps to 3-hop with a visible RTT shift — largely disappears: the flow hash already had a length-identical twin in the surviving plane, and only a weight rebalance remains.

**Plane-granular heterogeneity.** Each plane is internally uniform, but planes may differ: a 400G plane beside a 100G plane, with W-CMP weights proportional to plane bandwidth. A hardware refresh becomes "stand up a new plane" — coarser than RNG's per-node degree mixing, but a far saner operational unit.

**Additive expansion.** Because the complete edge set of each plane is known in advance, growth never breaks an existing link: a landing router patches into q + 1 pre-planned positions per plane. With pre-provisioned passive patch frames carrying the polarity-graph permutation — the structured analogue of the ShuffleBox, though it must encode the *specific* edge set rather than a blind permutation — PolarFly expansion is arguably cleaner than RNG's break-and-splice appendix. The residual costs: q is a day-1 ceiling (the next prime power is a forklift), and the partial graph's path multiplicity is nonuniform, which the live-vertex-aware weight function of Section 3.3 absorbs.

The price is scale-per-port: the same 993 chassis running one q = 61 plane instead of two q = 31 planes would reach 3,783 switches. The Moore bound goes as q², so halving the radix quarters the reach; parallel planes over the same vertex set buy redundancy, not size. Slicing closes the failure-continuity and heterogeneity gaps against RNG while widening the scale gap — an excellent trade at 1–2K switches, a poor one at hyperscale. Section 5 shows that modern radix dissolves the dilemma.

### 4.2 k-plane membership and the intersection trick

Generalizing, let each switch join 2 of k planes. Reachability at diameter 2 requires the memberships of any pair to intersect. For **k = 3**, any two 2-subsets of {A, B, C} necessarily share a plane: diameter 2 is preserved globally while scaling to 3·993/2 ≈ 1,489 switches on 64-port hardware. Path multiplicity becomes pair-type-dependent — same-type pairs (both AB) share two planes and enjoy dual minimal paths; cross-type pairs share exactly one — and the pair type is simply two more coordinates in the address, so the weight derivation remains closed-form.

At k ≥ 4 disjoint memberships appear (AB vs. CD): such pairs share no plane and must transit a bridging switch, giving bounded diameter 4 (2 hops in the source plane to a bridge whose membership intersects both, 2 in the destination plane) — still coordinate-derivable, but no longer diameter-2. At this point the construction is effectively a hand-rolled star product, and the honest comparison is no longer against vanilla PolarFly but against **PolarStar** (the diameter-3 star product of ER_q with Paley or inductive-quad graphs — the literature's official answer to scaling past q² + q + 1) and BundleFly. Our expectation, to be validated: PolarStar wins on scale-per-port; k-plane slicing wins on plane-granular heterogeneity and operational modularity.

> **[FIGURE 3 placeholder: k=3 plane membership diagram; pair-type path multiplicity table]**

To our knowledge, plane-membership combinatorics used as the *diameter-preservation mechanism*, with cross-plane W-CMP weights derived from pair-type labels, is novel; it is the second element identified for invention disclosure.

---

## 5. Scale at Modern Radix

### 5.1 The Moore ceiling moves above building size

Radix growth is asymmetric between the two designs: it repairs PolarFly's largest weakness while only marginally improving RNG's position.

At 51.2T (512×100G effective lanes), q = 127 yields a 16,257-switch plane at fabric degree 128 — against a Moore bound of d² + 1 = 16,385, i.e., **99% of the theoretical maximum reach for diameter 2**. A pure-transit 4×q=127 configuration is possible but portless; the realistic ToR-integrated build is **2×q=127** — 256 lanes fabric, 256 lanes server downlink — giving 16,257 ToRs × 256 ports ≈ **4M attachment points at 1:1, dual minimal paths, diameter 2**. That exceeds the footprint of any single building in production today. Meanwhile the prime-power lattice (61, 64, 67, 71, 73, 79, 81, 83, …) is dense at high radix. Both classical objections — quantization and the q² ceiling — cease to be practical constraints at current-generation silicon.

### 5.2 Per-bit economics compound with bandwidth

Fabric capacity consumed per delivered bit is proportional to hop count. The W-CMP mix runs at roughly L ≈ 2.6 effective hops (weighted across 2-hop minimal and 3-hop non-minimal sets); Spraypoint's spray-plus-waypoint structure runs meaningfully longer — typically 4–5. At 100G lanes this is an accounting difference; at 200G per lane and beyond, each extra hop is another traversal of increasingly expensive and power-hungry optics and serdes. A near-Moore fabric at L ≈ 2.6 sits close to the information-theoretic floor of fabric-capacity-per-delivered-bit. RNG's cost case is "up to 45% cheaper than fat tree" — but the fat tree is a soft target; against a Moore-optimal structured fabric, RNG's hop tax becomes the headline line item, and it grows in absolute dollars and watts with every silicon generation. The structured topology's advantage is among the few in this comparison that strengthens with scale.

### 5.3 RNG's pressure points at 16K+ flat nodes

RNG has no topological ceiling, but three practical pressures emerge in this regime. First, the control plane: Spraypoint is a distributed protocol over a flat domain with no hierarchy; dissemination and convergence behavior at 16K+ nodes is unproven, and the published production fabrics are presumably well below it. Second, ECMP hardware: spraying across the full neighbor set implies ECMP groups approaching the lane count, and ASIC ECMP member tables are a finite, contested resource — 512-wide groups per destination class is real pressure even with group sharing. WCMP-SRv6-PolarFly sidesteps this entirely: explicit paths consume encap-node policy memory, not transit ASIC tables. Third, expansion recabling complexity scales with d: at d = 512, every rack land touches 256 existing links spread across the building. None of these is fatal — they are engineering, and Amazon has the bodies — but all worsen with radix, while additive pre-planned algebraic expansion improves relatively.

---

## 6. Failure Models: Statistical Headroom vs. Repair Logic

RNG's resilience claim is best understood as a claim about *blast-radius shape*, and a precision matters: Spraypoint absolutely reacts to failure — it is a routing protocol in the OSPF/BGP mold and reconverges on topology change. What RNG eliminates is *protection machinery*: no FRR, no precomputed backups, no TI-LFA-style repair, because steady-state forwarding already encodes the redundancy. When a link dies, the adjacent router locally prunes the member from its ECMP groups and traffic redistributes in the data plane instantly; the failed link carried roughly 1/d of any affected pair's capacity, so the loss is a thin statistical shave across many pairs rather than a mode change for any one. There are no special routers; every failure is small and uniform. Protocol convergence cleans up in the background with nothing waiting on it.

Single-plane PolarFly, by contrast, undergoes a discrete transition when a pair's unique minimal path dies: 2-hop traffic steps to the 3-hop set, with an RTT shift congestion control will notice. The response is fast — the encap node re-derives weights algebraically, arguably faster than any IGP floods — but it is a *reaction*, with a detectable before/after. Dual-plane slicing (Section 4.1) converts the transition from a length change into a weight rebalance among length-identical paths, substantially closing the gap; and in the backend deployment of Section 7, MRC moves failure handling into the transport entirely.

The honest framing for operators: PolarFly offers deterministic best-case behavior with discrete failure modes; RNG offers probabilistic behavior with continuous failure modes. Preference depends on whether the workload fears tail latency or fears variance.

---

## 7. The AI Backend: MRC and Packet Spraying on PolarFly

### 7.1 Why the backend is the natural home

RNG's authors explicitly scope to multi-tenant general-purpose fabrics and defer AI training, noting that such workloads may demand rail-optimized structures and local capacity islands that flat random topologies lack. The backend is simultaneously the regime where every PolarFly disadvantage evaporates: the fabric is built once at known size (q ceiling irrelevant), the operator owns the stack end to end (encap intelligence is an asset, not a liability), the hardware population is uniform per build (heterogeneity moot), and per-bit cost and power compound directly into training economics (Section 5.2). Collective-driven traffic additionally rewards deterministic path lengths: flow-completion-time skew across parallel transfers gates the collective, and a hard diameter-2 bound with enumerable path lengths is precisely the property a scheduler can reason about.

What the structured fabric has historically lacked in this regime is a transport that can exploit its path set. That transport now exists.

### 7.2 MRC in brief

MRC (Multipath Reliable Connection), contributed to OCP in May 2026 by OpenAI with AMD, Broadcom, Intel, Microsoft, and NVIDIA, extends RDMA-over-Ethernet semantics so that **a single RDMA connection distributes traffic across multiple network paths**, with reordering tolerated by the transport and congestion managed per path (AMD's NSCC algorithm, now part of the UEC congestion-control specification). It is implemented on shipping 400/800G NICs (ConnectX-8, Pollara, Vulcano, Thor Ultra) with **SRv6 switch support** on Spectrum-4/5 (Cumulus, SONiC) and Tomahawk 5 (EOS), and is deployed in production on OpenAI's largest GB200 clusters (OCI Abilene, Microsoft Fairwater). The companion paper is explicitly titled "Resilient AI Supercomputer Networking using MRC and SRv6." Reported topology practice mirrors the breakout philosophy: rather than one 800G link, the NIC is split into multiple smaller links to create natural path redundancy, enabling two-tier builds at 100K+ GPU scale with roughly two-thirds the optics and 40% fewer switches than three-tier baselines.

Three properties matter for our purposes. MRC is **reorder-tolerant**, so per-packet (or per-message-slice) spraying is admissible where general-cloud TCP forced flow-level hashing. MRC is **path-aware**, maintaining per-path state and congestion signals within one connection. And MRC's deployed path-steering mechanism **is already SRv6** — the same encapsulation substrate as our design.

### 7.3 The synthesis: per-packet W-CMP over algebraic path sets

Recall why W-CMP was specified at flow level (Section 3.3 context): general-cloud tenants run vanilla TCP on stock NICs, and per-packet spraying would have required reorder-tolerant transports that cannot be assumed across an adversarial tenant population. The backend inverts the assumption — every endpoint is an MRC-capable RDMA NIC — and the design strengthens along four axes.

**Spraying granularity.** The W-CMP weights of Section 3.3 apply per packet rather than per flow. Elephant-flow collision risk — the residual weakness of any flow-hashed scheme, RNG's included — vanishes: a single connection's load spreads across the full minimal-plus-non-minimal path set in proportion to the derived weights. This is, notably, a capability RNG's general-cloud deployment does not have; Spraypoint sprays flows, not packets. On the backend, the structured fabric out-sprays the spray.

**Path-set provisioning.** MRC requires each connection to be provisioned with a set of paths. On a Clos this set is implicit (ECMP up, ECMP down); on PolarFly it is *explicit and enumerable* — exactly q + 1-ish edge-disjoint segment lists per pair, synthesized from projective coordinates with no path discovery protocol. PolarFly converts MRC's path-set abstraction from a fabric-dependent configuration burden into a closed-form computation at connection setup. The diameter-2 bound additionally caps the path-length spread within a connection's set at one hop (2 vs. 3), simplifying the transport's reordering and completion-tracking window relative to a random graph's longer-tailed length distribution.

**Adaptive weighting.** NSCC's per-path congestion signals provide the feedback channel that pure demand-oblivious W-CMP lacks. The static algebraic weights become *priors*, modulated at the NIC by per-path congestion state — UGAL-like adaptivity realized at the transport rather than in switch hardware, on commodity Ethernet ASICs. The lineage is satisfying: PolarFly's original evaluation assumed HPC-style adaptive routing in switches; MRC relocates exactly that function to the place the backend operator controls.

**Failure handling.** MRC's headline operational result — switch reboots during frontier training runs without job disruption — derives from per-path health tracking: the transport stops scheduling onto a dead path within one RTT-scale detection window. On PolarFly this composes with algebraic re-derivation: the NIC's transport masks the failure instantly; the encap layer re-synthesizes the path set from the updated live-vertex set in the background; no IGP convergence sits anywhere on the critical path. The discrete-transition concern of Section 6 is fully retired in this deployment model — the surviving paths in the MRC set absorb the weight shift per packet, and dual-plane slicing (where used) makes even the length distribution invariant.

> **[FIGURE 4 placeholder: MRC connection over PolarFly — one minimal + q non-minimal segment lists, per-packet weighted spray, NSCC feedback loop]**

### 7.4 Positioning against MRC's deployed topologies and against RNG

MRC is topology-agnostic and its production deployments to date run on two-tier rail-style Clos fabrics. The proposal here is therefore not MRC-versus-PolarFly but MRC-*on*-PolarFly as the structured direct-topology alternative to MRC-on-Clos: diameter 2 instead of 4-hop worst-case through a spine, ~99% Moore efficiency instead of Clos port overheads, and a path set the transport can enumerate algebraically. The breakout philosophy is shared — MRC deployments already split NICs into multiple lower-rate links for path redundancy, which is precisely the lane-level adjacency model PolarFly's degree budget wants. Against RNG the backend comparison is largely by concession: Amazon defers the regime, and the properties RNG would bring to it (statistical path lengths, flow-level spraying, fleet-elasticity advantages that a build-once cluster cannot exercise) are mismatched to collective-driven traffic. A quantitative bake-off — MRC-on-PolarFly vs. MRC-on-Clos vs. a hypothetical MRC-on-RNG at matched port count, on allreduce/all-to-all completion-time distributions — is the natural next experiment and an open invitation in this paper.

---

## 8. Scorecard and Conclusions

| Dimension | RNG (quasi-random + Spraypoint) | WCMP-SRv6-PolarFly (incl. slicing) | Notes |
|---|---|---|---|
| Scale per port | Unbounded n | ~16K ToRs / ~4M ports at 2×q=127 | Gap closed at ≥51.2T radix |
| Diameter / latency | Probabilistic, longer (≈4–5 hops sprayed) | Deterministic 2 (L ≈ 2.6 effective) | PolarFly; gap grows with optics cost |
| Per-bit cost & power | 9–45% under fat tree | Near Moore-bound floor | Tips to PolarFly; compounds with bandwidth |
| Minimal-path diversity | High (spray), non-minimal | 1 per plane; k planes ⇒ k minimal ECMP | Slicing closes; backend MRC retires |
| Transit ASIC state | LPM + wide ECMP groups | LPM only; paths in encap memory | PolarFly avoids ECMP table pressure |
| Control plane | Distributed protocol (Spraypoint) | No path computation protocol (algebraic) | PolarFly, surprisingly |
| Heterogeneity | Per-node degree mixing, in place | Plane-granular | RNG finer; slicing operationally cleaner |
| Incremental growth | Unquantized; break-and-splice | Additive to q ceiling; pre-planned | Different shapes; PolarFly cleaner per step |
| Failure model | Continuous, statistical, no protection logic | Discrete → continuous with planes/MRC | RNG single-plane; parity with slicing+MRC |
| Operational philosophy | Stateless fabric, stupid everywhere | Intelligence concentrated at encap | The irreducible difference |

The two topology families do not converge with scale; they sort by operating model. **Engineered randomness wins the elastic-fleet regime**: daily rack lands, rolling hardware generations, adversarial multi-tenant traffic, and an operational culture that prizes a fabric incapable of holding misconfiguration. **Structured optimality wins the deliberate-fabric regime**: build-once footprints, operator-owned stacks, per-bit economics that compound, and workloads — above all AI training collectives — that reward deterministic latency and enumerable paths. Modern radix removes scale as a discriminator; SRv6 removes the forwarding-state objection; MRC removes the transport objection. What remains is a genuine philosophical choice about where complexity should live, and the thesis of this paper is that for the backend, the answer has quietly become the encap node.

A closing observation on the literature: RNG's published case is argued against the fat tree, and its dismissal of structured alternatives rests on a forwarding-state analysis that predates compressed source routing as a deployable mechanism. The comparison that matters next is not flat-versus-tree but structured-flat-versus-random-flat — and on current silicon, with current transports, that comparison is live.

---

## 9. Open Questions and Future Work

The quantitative bake-offs this paper motivates: k-plane sliced PolarFly versus PolarStar and BundleFly at matched port count (minimal-path multiplicity, worst-case diameter, cost); the closed-form optimal W-CMP weight function w(q, pair-type, live-vertex set, plane bandwidths) against simulated optima across traffic matrices; MRC-on-PolarFly versus MRC-on-Clos on collective completion-time distributions at 100K-GPU scale; Spraypoint convergence behavior and ECMP-table occupancy at 16K+ flat nodes (an RNG question, but one whose answer calibrates this comparison); and the passive patch-frame design encoding polarity-graph permutations — whether the structured analogue of the ShuffleBox can match its manufacturing economics given that it must realize a specific rather than statistical edge set.

Patent-relevant elements consolidated for internal disclosure: (1) algebraically derived W-CMP weights as a function of q, pair type, live-vertex set, and plane bandwidths; (2) k=3 pairwise-intersecting plane membership as a diameter-preservation mechanism with pair-type-derived cross-plane weights; (3) plane-granular heterogeneity model; (4) MRC path-set provisioning via closed-form coordinate synthesis with congestion-modulated algebraic priors. *(Prior-art caveats from internal discussion apply: WCMP, RFC 9256 weighted candidate paths, and UGAL/Valiant minimal/non-minimal splits are established; novelty concentrates in topology-specific algebraic derivation.)*

---

## References (to be completed)

*Placeholder — full citations to be added:* Bernardi et al., "Expanding into Reality: Random Graphs for Datacenter Networks" (RNG), arXiv:2604.15261, 2026 · Lakhotia et al., "PolarFly: A Cost-Effective and Flexible Low-Diameter Topology," SC22, arXiv:2208.01695 · Lakhotia et al., PolarStar · Singla et al., "Jellyfish: Networking Data Centers Randomly," NSDI 2012 · Valadarsky et al., "Xpander," 2016 · Besta & Hoefler, "Slim Fly," SC14 · OpenAI et al., MRC specification, OCP, May 2026 · OpenAI et al., "Resilient AI Supercomputer Networking using MRC and SRv6" · Zhou et al., "WCMP: Weighted Cost Multipathing," EuroSys 2014 · RFC 9256 (SR Policy Architecture) · RFC 8986 (SRv6 Network Programming) · Erdős–Rényi polarity graph / Brown graph literature · EvalNet toolchain, arXiv:2105.12663.
