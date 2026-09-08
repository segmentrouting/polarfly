# traffic-gen

Tools for validating WMP-PolarFly's weighted multipath SRv6 routing
(`../docs/wmp-polarfly-whitepaper-v06.md`) against the q=7 `docker-sonic-vs`
lab topology in `../q7/sonic/`. See `CLAUDE.md` in this directory for the
project background.

## Where to run these: on host server, not inside a container

All four scripts are orchestrators: they compute
paths locally and then issue their own `docker exec ...` calls out to the
relevant switch/host containers. 

They're plain Python 3, stdlib-only (`argparse`, `json`, `subprocess`, ...)
— no `pip install` needed. The `scapy`/`iperf3` dependencies
live inside the host containers (`bmcdougall/alpine-srv6-scapy:1.0`) and are
invoked there via `docker exec`, not imported on the host running these
scripts.

## Prerequisites

- The q7 `docker-sonic-vs` topology already deployed and configured:
  ```sh
  cd ../q7/sonic
  sudo containerlab deploy -t sonic-polarfly-q7-nobinds.clab.yaml
  ./q7-config.sh
  ```
- `docker` CLI access to that deployment

## Scripts, in the order you'd normally use them

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
weights at once.

### 2. `provision.py` — push routes for a pair into the live topology

This is the step that actually touches the deployed containers. Pick a
pair (see "choosing pairs" below), then:

```sh
python3 provision.py --q 7 --pair sw001 sw019 --dry-run   # preview first
python3 provision.py --q 7 --pair sw001 sw019              # then for real
```

For each `--pair` (repeatable), this installs a *single weighted IPv6
multipath route* on the source host, targeting the destination host's
one real, existing address — analogous to how multi-tenant frontend-DC
traffic gets encapsulated toward a single remote VTEP-like address, not a
different address per path. Each nexthop in that multipath route carries
its own `seg6` encap (a different SP/NSP segment list) and its own
integer weight derived from the WMP weights (e.g. `4:1:1:1:1:1:1` for the
q=7 40%-SP/60%-split-across-6-NSP case), so the kernel's own per-flow hash
picks a path per flow according to those weights. It also sets
`net.ipv6.fib_multipath_hash_policy=1` on the source host — required, since
the default (L3-only) hash policy would send every flow between the same
two hosts down the same nexthop regardless of weight, because the
addresses never change between paths in this design — plus a single
SP-only return route on the destination for basic reachability (iperf3's
control channel is TCP even for UDP tests, so some return path is needed —
only the *forward* direction's split across SP/NSP is what's under test).

Segment lists default to **uN** (node SID, BGP-routed) per intermediate
hop rather than uA (interface-bound End.X) — safe here because every hop
in a computed path is, by construction, a direct graph-neighbor of the
previous one, so uN resolves to the identical physical links uA would
pick, just via normal BGP-learned reachability instead of hardcoded
interface binding. Pass `--uA` (to both `path_calculator.py` and
`provision.py`) to test the uA mechanism specifically instead:

```sh
python3 provision.py --q 7 --pair sw001 sw019 --uA
```

### 3. `run_test.py` — measure the achieved weighted split

Requires a pair already provisioned by step 2:

```sh
python3 run_test.py --q 7 --pair sw001 sw019 --streams 40 --duration 5
```

`--streams` defaults to 40 -- empirically the largest `iperf3 -P` this
lab's veth/seg6-encap path reliably sustains at once; higher values
(tested up to 100) intermittently fail with iperf3's `unable to receive
results` under this containerlab setup's per-container overhead, not a
bug in the script's measurement logic (confirmed working correctly at
`-P 20`: SP achieved its 40% target and NSPs split roughly evenly across
the remaining 60% on a live sw001->sw019 run).

Since every flow now targets the *same* destination address (the single
multipath route from step 2), paths can't be told apart by destination
the way an older per-path-address design would. Instead: starts one
`iperf3` server on the destination, runs one `iperf3 -P <streams>` client
from the source (many parallel streams, each getting its own ephemeral
source port — exactly the entropy the kernel's L4 multipath hash needs),
then for each stream uses `ip -6 route get ... sport <port> dport <port>`
on the source to ask the kernel which nexthop that exact flow would
resolve to (the same FIB lookup real forwarding uses), matches the
returned segment list's first segment against each path's precomputed
first segment to attribute that stream's bytes (from the client's
`--json` output) to a path, and prints achieved-vs-target percentages.

### 4. `verify_packet.py` — confirm each path actually delivers

Also requires a pair already provisioned by step 2. Separate from the
throughput test above — this checks correctness (does each path's
segment list actually deliver a packet end to end), not volume. Since
there's no per-path address to target directly, it tests paths one at a
time by temporarily replacing the multipath route with a single-nexthop
route for just that path, sending one UDP packet, and confirming via a
`tcpdump` capture on the destination that it arrives with its expected
payload — then restores the real weighted multipath route once all paths
are checked:

```sh
python3 verify_packet.py --q 7 --pair sw001 sw019
```

## Choosing pairs

Any two switches that aren't directly fabric-adjacent work (adjacent pairs
have no SP/NSP split to test — `provision.py` will refuse them). `sw001`
and `sw019` (used in the examples above, and already referenced in
`../q7/sonic/README.md`'s manual SRv6 example) is a convenient default: a
typical non-adjacent pair with the common 6-NSP case. For variety, try a
pair where one switch is self-conjugate/absolute (`sw026`, `sw027`,
`sw032`, `sw035`, `sw039`, `sw042`, `sw047`, `sw048` — see `AGENTS.md`) to
exercise the degree-q case.
