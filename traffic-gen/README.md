# traffic-gen

Tools for validating WMP-PolarFly's weighted multipath SRv6 routing
(`../docs/wmp-polarfly-whitepaper-v06.md`) against the q=7 `docker-sonic-vs`
lab topology in `../q7/sonic/`. See `CLAUDE.md` in this directory for the
project background.

## Where to run these: on host server, not inside a container

All four scripts are orchestrators: they compute paths locally and then
issue their own `docker exec ...` calls out to the relevant switch/host
containers.

They're plain Python 3, stdlib-only (`argparse`, `json`, `subprocess`, ...)
— no `pip install` needed. The `scapy`/`iperf3` dependencies live inside
the host containers (`bmcdougall/alpine-srv6-scapy:1.0`) and are invoked
there via `docker exec`, not imported on the host running these scripts.
Pairs files are plain JSON for the same reason (no PyYAML dependency).

## Prerequisites

- The q7 `docker-sonic-vs` topology already deployed and configured:
  ```sh
  cd ../q7/sonic
  sudo containerlab deploy -t sonic-polarfly-q7-nobinds.clab.yaml
  ./q7-config.sh
  ```
- `docker` CLI access to that deployment

## Scripts

### 1. `path_calculator.py` — inspect the algebra (optional, no deployment needed)

Pure graph/path math — doesn't touch docker at all, so it's safe to run
anytime, even before deploying anything, to sanity-check what a pair's SP
and NSP set look like:

```sh
python3 path_calculator.py --q 7 --pair sw001 sw019
```

Runs two self-tests on every invocation (the whitepaper's own worked
example, and an NSP-count sanity check across all 1,372 non-adjacent
pairs) before printing anything, so a clean run is itself a correctness
signal. `--out FILE.json` dumps every pair's computed paths/segments/
weights at once. Each pair's detail includes both the expanded per-hop
`segments` list and the compressed `usid_carrier` (see step 2) that
actually goes on the wire.

### 2. `provision.py` — push routes for one or more pairs into the live topology

This is the step that actually touches the deployed containers.

```sh
python3 provision.py --q 7 --pair sw001 sw019 --dry-run   # preview first
python3 provision.py --q 7 --pair sw001 sw019              # then for real
python3 provision.py --q 7 --pair sw001 sw019 --pair sw002 sw033   # repeatable
python3 provision.py --q 7 --pairs-file pairs.json          # many pairs at once
```

`--pairs-file` takes a JSON file: a flat list of `[SRC, DST]` pairs, e.g.

```json
[["sw001","sw019"], ["sw002","sw033"], ["sw026","sw014"], ["sw048","sw005"]]
```

It's combined with any `--pair` flags on the same invocation. `run_test.py`
(step 3) takes the exact same `--pair`/`--pairs-file` options, so one pairs
file drives both provisioning and testing for a given scenario.

For each pair, this:

1. Bumps both hosts' `eth1` (the host-to-switch link) to jumbo MTU 9100,
   matching the switch-side host-facing port. **This matters a lot**: the
   host side of that link defaults to 1500, and SRv6's per-hop SID
   overhead can push an encapsulated packet over 1500, causing
   fragmentation-driven retransmits that were measured to cut TCP
   throughput by roughly 900x (~3.5 Kbps vs ~3 Gbps on the same pair,
   before/after this fix) — see "Known findings" below.
2. Sets `net.ipv6.fib_multipath_hash_policy=1` on the source host — required
   for the kernel's ECMP hash to consider L4 ports, not just addresses
   (the default policy sends every flow between the same two hosts down
   the same nexthop regardless of weight, since addresses never change
   between paths in this design).
3. Installs a *single weighted IPv6 multipath route* on the source host,
   targeting the destination host's one real, existing address —
   analogous to how multi-tenant frontend-DC traffic gets encapsulated
   toward a single remote VTEP-like address, not a different address per
   path. Each nexthop carries its own `seg6 encap.red` and its own integer
   weight derived from the WMP weights (e.g. `4:1:1:1:1:1:1` for the q=7
   40%-SP/60%-split-across-6-NSP case), so the kernel's own per-flow hash
   picks a path per flow according to those weights. Each nexthop's
   `segs` is a **single compressed uSID carrier** (one 128-bit address
   packing the whole hop chain, e.g. `fc00:0:1033:1013:e000::` for a
   2-hop SP) rather than a comma-separated list of per-hop addresses —
   confirm with `docker exec <host> ip -6 route show <dst>`, which should
   show `segs 1 [ ... ]` per nexthop.
4. Installs a single SP-only *return* route on the destination, for basic
   reachability only (iperf3's control channel is TCP even for UDP tests)
   — not part of what's under test.

Segment lists default to **uN** (node SID, BGP-routed) per intermediate
hop rather than uA (interface-bound End.X) — safe here because every hop
in a computed path is, by construction, a direct graph-neighbor of the
previous one. Pass `--uA` (to `path_calculator.py`, `provision.py`, and
`run_test.py` together — they must agree) to test the uA mechanism
specifically instead.

### 3. `run_test.py` — measure the achieved weighted split

Requires the pair(s) already provisioned by step 2, and takes the same
`--pair`/`--pairs-file` options:

```sh
python3 run_test.py --q 7 --pair sw001 sw019 --streams 40 --duration 5
python3 run_test.py --q 7 --pairs-file pairs.json --duration 5
```

With more than one pair, every pair's iperf3 client runs **concurrently**
(each is a separate `docker exec` against a different source container,
so they genuinely overlap) — this exercises real fabric-wide load,
multiple source/dest hosts contending for shared links at once, not one
pair's traffic in isolation. Each pair gets its own results table, plus a
grand aggregate across all pairs at the end.

Since every flow within a pair targets the *same* destination address
(the single multipath route from step 2), paths can't be told apart by
destination. Instead: starts one `iperf3` server per destination host,
runs one `iperf3 -P <streams>` client per pair (many parallel streams,
each getting its own ephemeral source port — exactly the entropy the
kernel's L4 multipath hash needs), then for each stream uses `ip -6 route
get ... sport <port> dport <port>` on the source to ask the kernel which
nexthop that exact flow would resolve to (the same FIB lookup real
forwarding uses), matches the resolved nexthop's single compressed uSID
carrier against each path's precomputed carrier to attribute that
stream's bytes to a path, and prints achieved-vs-target percentages.

`--streams` defaults to 40 per pair -- empirically the largest `iperf3 -P`
this lab's veth/seg6-encap path reliably sustains at once; higher values
(tested up to 100) intermittently fail with iperf3's `unable to receive
results` under this containerlab setup's per-container overhead.
**Stream count also matters a lot for UDP loss readings** — see "Known
findings" below; don't compare loss% across runs with different
`--streams`.

The report ends with an aggregate line straight from iperf3's own
summary (`sum_sent`/`sum_received` for TCP, summed across all pairs),
independent of the per-path attribution above — a sanity cross-check on
each pair's `total`, and the only place `retransmits` shows up. Note that
for TCP, comparing sent vs. received bytes does *not* reveal loss (TCP
retransmits until the receiver has everything, so they converge
regardless) — `retransmits` is the actual tell; a nonzero sent-vs-received
gap on its own is normal measurement-timing skew (in-flight/unacked data
at the moment each side's counter was snapshotted), not lost data.

Pass `--udp` (with `--bandwidth`, per-stream target, default `100M`, and
optionally `--length` to also control datagram size / derived pps) to
switch every client to UDP instead of TCP. UDP has no retransmit-based
recovery, so its `lost_packets`/`lost_percent` (printed per path and in
aggregate) are a direct, unmasked loss measurement — unlike TCP, where
loss just gets silently resent. This isn't directly comparable to a TCP
run at the same nominal rate: TCP self-paces via ACKs/congestion control
down to whatever the path actually sustains, while `iperf3 -b` UDP blasts
at a fixed rate with no backoff, so a `--bandwidth`/`--streams` combo that
this software dataplane can't smoothly absorb will show high loss well
below TCP's proven throughput — that's expected UDP-vs-TCP (and
stream-count) behavior, not automatically evidence of an SRv6 forwarding
problem; see "Known findings" before concluding a real fabric limit.

```sh
python3 run_test.py --q 7 --pair sw001 sw019 --udp --bandwidth 50M
```

`--sweep START STOP STEP` (Mbps per stream, UDP only) automates finding
where loss appears: it repeats the whole (possibly multi-pair, concurrent)
test at each bandwidth step from START to STOP, printing aggregate
throughput/loss at each step and flagging the first step where loss
exceeds `--loss-threshold` (default 1.0%):

```sh
python3 run_test.py --q 7 --pairs-file pairs.json --udp --sweep 25 200 25 --duration 3
```

Each row also shows how many pairs actually completed (`pairs ok`); a row
marked `!` had at least one client fail for a reason unrelated to that
step's bandwidth (seen: `unable to read from stream socket` under heavy
concurrent `docker exec` load on the orchestrating host itself, not the
fabric) — those rows are excluded from threshold detection since they're
a partial sample, not a real loss/capacity signal. If you see a lot of
`!` rows, the orchestrating host may be under load from something other
than this test; re-run rather than trust that step's numbers.

### 4. `verify_packet.py` — confirm each path actually delivers

Requires a pair already provisioned by step 2 (single pair only — this
one doesn't take `--pairs-file`). Separate from the throughput test above
— this checks correctness (does each path's segment list actually
deliver a packet end to end), not volume. Since there's no per-path
address to target directly, it tests paths one at a time by temporarily
replacing the multipath route with a single-nexthop route for just that
path, sending one UDP packet via a plain kernel-routed socket (not
scapy's `send()`, which bypasses the kernel routing table entirely and
never sees the `encap seg6` route), and confirming via a `tcpdump`
capture on the destination that it arrives with its expected payload —
then restores the real weighted multipath route once all paths are
checked:

```sh
python3 verify_packet.py --q 7 --pair sw001 sw019
```

An occasional single-path `FAILED` on an otherwise-clean run is usually a
capture-timing race (the ~0.3s gap between installing that path's route
and `tcpdump` attaching), not a real delivery failure — re-run that one
path (or the whole check) to confirm before treating it as a finding.

## Systematic testing walkthrough

A reasonable order for exercising all of this, from cheapest/most basic
to most demanding:

1. **Algebra sanity check** (no deployment needed): `path_calculator.py`
   with no args runs its self-tests; add `--pair`/`--out` to inspect
   specific pairs.
2. **Single-pair correctness**: `provision.py --pair A B`, then
   `verify_packet.py --pair A B` — confirms every one of that pair's
   paths (SP + all NSPs) actually delivers before trusting any throughput
   number from it.
3. **Single-pair weighted-split baseline (TCP)**: `run_test.py --pair A B`
   — confirms the achieved split roughly tracks the target weights
   (40% SP / evenly split NSPs) and that `retransmits` is low. Run more
   than once; per-run variance is expected (see "Known findings").
4. **Single-pair UDP loss baseline**: `run_test.py --pair A B --udp` at a
   modest `--bandwidth` (well under what step 3's TCP run achieved) —
   loss should be near zero. This is your reference point before pushing
   rate up.
5. **Build a pairs file** covering a representative spread: at least one
   pair per "Choosing pairs" category below. Re-run steps 2-4 with
   `--pairs-file` instead of `--pair` to provision/verify/baseline the
   whole set.
6. **Fabric-wide concurrent load**: `run_test.py --pairs-file pairs.json`
   (TCP) — multiple source/dest hosts contending for shared links at
   once; check the grand aggregate and each pair's `retransmits`.
7. **Find the loss threshold**: `run_test.py --pairs-file pairs.json --udp
   --sweep START STOP STEP`. Before concluding a bandwidth number *is*
   the fabric's capacity, repeat the sweep at a couple of different
   `--streams` values (e.g. 1, 4, 40) — if loss at the same aggregate
   bandwidth is wildly different across `--streams` values, what you
   found is a stream-count-sensitive measurement artifact, not a fabric
   capacity limit (this is exactly what happened in initial testing: 40
   streams/pair showed ~52% loss essentially flat from 1.6 to 8 Gbps
   aggregate, while 1 and 4 streams/pair showed 0% loss across the same
   range — see "Known findings").
8. **Vary q or the segment mechanism**: rerun any of the above with
   `--uA` (all three scripts must agree) to test the interface-bound
   adjacency mechanism instead of uN, or regenerate at a different `--q`
   (see `../AGENTS.md`) for a different fabric scale.

## Known findings (read before drawing conclusions from a new result)

- **Host-side MTU**: `provision.py` bumps host `eth1` to jumbo 9100 to
  match the switch's host-facing port. Without it, SRv6 overhead pushes
  packets over the host's default 1500 MTU and TCP throughput on a single
  pair measured ~3.5 Kbps; with it, ~3 Gbps on the same pair (~900x). If a
  throughput number ever looks anomalously low, check `docker exec <host>
  ip link show eth1` for the MTU before looking anywhere else.
- **L4 hash policy**: without `net.ipv6.fib_multipath_hash_policy=1` on
  the source host, every flow to the same destination takes the same
  nexthop regardless of source port, so the achieved split collapses to
  100% on whichever path the L3-only hash happens to pick. `provision.py`
  sets this; if you provision by hand, don't skip it.
- **Per-run variance is normal, especially at high per-stream throughput**:
  at multi-Gbps per stream, a handful of long-lived elephant flows can
  dominate a fixed-duration window's byte totals regardless of which
  nexthop weight put them there, so the achieved split can swing well
  away from target (e.g. SP hitting 50% against a 40% target) run to run.
  Longer `--duration` and/or more `--streams` reduces this variance.
- **TCP sent-vs-received gap ≠ loss**: TCP retransmits until delivered, so
  a several-MB gap between `sum_sent` and `sum_received` bytes on a short
  run is normal in-flight/unacked data at the snapshot instant, not
  dropped data. `retransmits` is the real TCP-layer loss signal.
- **UDP loss is extremely sensitive to `--streams`, not just
  `--bandwidth`**: a 4-pair concurrent sweep from 10-50 Mbps/stream at
  `--streams 40` showed ~52-53% loss *flat* across the whole range
  (including at just 1.6 Gbps aggregate, far below proven TCP capacity on
  the same pairs) — a flat curve that doesn't climb with rate is a sign
  it's not really a bandwidth-saturation curve. The same sweep at
  `--streams 1` and `--streams 4` showed 0% loss throughout. Read this as
  an artifact of how many concurrent UDP flows this environment's
  receive path (iperf3's UDP demux under this containerized dataplane)
  can absorb cleanly, not as the fabric's real per-pair capacity — when
  characterizing capacity, sweep bandwidth at a fixed, modest `--streams`
  count rather than defaulting to a high one.
- **Sweep client failures are usually the orchestrating host, not the
  fabric**: an occasional `unable to read from stream socket: Resource
  temporarily unavailable` under many concurrent `docker exec`
  invocations has been observed even at low load average on the host —
  flaky, not deterministic. `--sweep`'s `pairs ok` column and `!` flag
  exist to catch this; don't trust a flagged step's numbers.
- **`ip route get` needs an explicit `ipproto`**: omitting it happens to
  match TCP's real hash (confirmed empirically), but resolves to the
  *wrong* nexthop for a UDP 5-tuple. `run_test.py` already passes the
  right one for whichever mode you ran; only matters if you're doing your
  own manual `ip route get` probes.

## Choosing pairs

Any two switches that aren't directly fabric-adjacent work (adjacent pairs
have no SP/NSP split to test — `provision.py`/`run_test.py` will refuse
them). For a representative pairs file, include at least one of each:

- **Typical non-adjacent pair, both non-absolute** (the common 6-NSP
  case) — e.g. `sw001`/`sw019` (used throughout the examples above, and
  already referenced in `../q7/sonic/README.md`'s manual SRv6 example).
- **A pair involving a self-conjugate/absolute switch** (degree q instead
  of q+1; still exactly 6 NSPs at q=7, but the SP relay has one fewer
  fabric port to work with) — absolute switches at q=7 are `sw026`,
  `sw027`, `sw032`, `sw035`, `sw039`, `sw042`, `sw047`, `sw048` (see
  `../AGENTS.md`).
- **A handful of arbitrary others** spread across switch-index ranges, to
  get some variety of hop chains under fabric-wide concurrent load.

Example `pairs.json` covering the above:

```json
[["sw001","sw019"], ["sw002","sw033"], ["sw026","sw014"], ["sw048","sw005"]]
```
