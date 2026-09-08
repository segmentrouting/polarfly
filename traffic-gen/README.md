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

For each `--pair` (repeatable), this assigns the destination host one
extra IPv6 address per forward path (SP + each NSP) and installs the
matching `ip -6 route ... encap seg6 mode encap.red segs ...` on the
source host, plus a single SP-only return route on the destination for
basic reachability (iperf3's control channel is TCP even for UDP tests, so
some return path is needed — only the *forward* direction's split across
SP/NSP is what's under test).

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
python3 run_test.py --q 7 --pair sw001 sw019 --duration 10
```

Starts one `iperf3` server per path on the destination (each on its own
port — plain `iperf3 -s` doesn't multiplex concurrent clients on one
port), runs one client per path concurrently from the source with
parallel-stream counts weighted to approximate the target split (e.g. 4
streams on SP vs. 1 on each NSP for the whitepaper's 40/10 split), then
prints achieved-vs-target percentages per path.

### 4. `verify_packet.py` — confirm each path actually delivers

Also requires a pair already provisioned by step 2. Separate from the
throughput test above — this checks correctness (does each path's
segment list actually deliver a packet end to end), not volume:

```sh
python3 verify_packet.py --q 7 --pair sw001 sw019
```

Sends one UDP packet per path from the source (via the *kernel's* own
`seg6` encap — the same route step 2 installed, not a hand-built SRv6
header) and confirms via a `tcpdump` capture on the destination that each
one arrives with its expected payload.

## Choosing pairs

Any two switches that aren't directly fabric-adjacent work (adjacent pairs
have no SP/NSP split to test — `provision.py` will refuse them). `sw001`
and `sw019` (used in the examples above, and already referenced in
`../q7/sonic/README.md`'s manual SRv6 example) is a convenient default: a
typical non-adjacent pair with the common 6-NSP case. For variety, try a
pair where one switch is self-conjugate/absolute (`sw026`, `sw027`,
`sw032`, `sw035`, `sw039`, `sw042`, `sw047`, `sw048` — see `AGENTS.md`) to
exercise the degree-q case.
