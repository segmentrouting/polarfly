# Building docker-sonic-vpp (202511, bookworm)

Procedure for building a `docker-sonic-vpp:latest` image from the SONiC
`202511` monthly release branch, for use with this repo's
`--variant sonic-vpp` containerlab topology.

## Why `BLDENV=bookworm`, not trixie

The `202511` branch defaults `IMAGE_DISTRO` to trixie for the image as a
whole, but `platform/vpp/docker-sonic-vpp/Dockerfile.j2` (the pinned
`sonic-platform-vpp` submodule) still hardcodes:

```
FROM docker-swss-layer-bookworm-...
```

There is no `docker-swss-layer-trixie` anywhere in the buildimage tree yet.
So `BLDENV=bookworm` below is required, not a fallback — as of `202511`,
`docker-sonic-vpp` only builds on bookworm regardless of the branch's outer
default. A trixie `docker-sonic-vpp` would mean porting `docker-swss-layer`
yourself; not attempted here.

VPP itself (target version 25.06 per `rules/vpp.mk`) is compiled from source
in-tree, not pulled as a `.deb` from fd.io's package repo — so there's no
"does fd.io publish trixie packages yet" risk either way.

## Prerequisites

- Linux x86_64 build host (SONiC's docs recommend Ubuntu 20.04/22.04 as the
  *host* OS — this is independent of the bookworm/trixie choice above, which
  only affects the *build container* SONiC's `make` spins up).
- Docker installed, your user in the `docker` group.
- **Disk: 100GB+ free.** SONiC builds are disk-hungry; check `df -h` on
  whatever partition holds the clone before starting.
- 8+ CPU cores / 16GB+ RAM recommended. First build is multi-hour; it's
  building swss-common, sairedis, libsaivpp, FRR, syncd, and VPP from source,
  not just the platform layer.
- `git`, `make`.

## 1. Clone at the 202511 branch

```sh
git clone --branch 202511 --single-branch https://github.com/sonic-net/sonic-buildimage.git
cd sonic-buildimage
```

## 2. Pull in the VPP platform submodule

```sh
git submodule update --init --recursive platform/vpp
```

Optional — check what commit of `sonic-platform-vpp` you actually got:

```sh
git -C platform/vpp log -1 --oneline
```

## 3. Initialize the build tree

```sh
make init
```

This pulls/prepares the `sonic-slave-bookworm` build container that the rest
of the build runs inside (containerized build, not a bare-metal toolchain on
your host).

## 3a. Install `jinjanator` *before* `make configure` — confirmed gotcha

`make configure` renders `sonic-slave-bookworm/Dockerfile.j2` via a `j2`
command. If `j2` (the `jinjanator` package) isn't installed, this fails in a
very misleading way: `Makefile.work`'s own version-check for `j2` —

```make
J2_VER := $(shell j2 --version 2>&1 | grep j2 | awk '{printf $2}')
```

— is fooled by bash's own error message. `bash: j2: command not found`
*contains the substring "j2"*, so the grep matches it, `J2_VER` comes out
non-empty, and the intended `$(error Please install j2 ...)` never fires.
`make configure` then silently proceeds to render an empty/broken
`Dockerfile` and feeds it to `docker build`, which fails much later with:

```
ERROR: failed to build: failed to solve: no build stage in current context
```

pointing at an auto-generated `COPY ["buildinfo", ...]` line with no `FROM`
above it — a red herring; the real problem is upstream. Confirmed by
reproducing the `grep`/`awk` bug directly and by testing `j2 --version`,
which reported "command not found" via `apt`'s handler (i.e. genuinely not
installed, not just a `PATH` issue).

**Fix — install the package `Makefile.work`'s own error message names**
(`jinjanator`, not the older/unmaintained `j2cli` that `apt` suggests):

```sh
python3 -m venv ~/.venvs/sonic-build   # or: pip3 install --user jinjanator
source ~/.venvs/sonic-build/bin/activate
pip install jinjanator
j2 --version                            # must print a real version, not "command not found"
```

If you already ran `make configure` before installing `jinjanator`, force a
clean re-render before retrying:

```sh
rm -f sonic-slave-bookworm/Dockerfile sonic-slave-bookworm/Dockerfile.user
rm -rf sonic-slave-bookworm/buildinfo
```

## 4. Configure for the VPP platform

```sh
make configure PLATFORM=vpp BLDENV=bookworm
```

Sanity-check the result before moving on:

```sh
head -15 sonic-slave-bookworm/Dockerfile
```

Should show a real `FROM ...debian:bookworm@sha256:...` at/near the top
(SONiC pins the base image to a digest for reproducible builds — expect a
registry mirror prefix like `publicmirror.azurecr.io/`, not bare
`debian:bookworm`). Two other messages during this step are harmless noise,
not build failures: a `mv: cannot move '/etc/apt/sources.list.d/...'
Permission denied` (a host apt-mirror-config helper that doesn't have
permission to back up a host file) and `fatal: not a git repository` (a
version-cache probe run from a non-git path). Neither affects the generated
`Dockerfile`.

## 5. Two confirmed upstream bugs you must patch before building

Both were found by actually tracing the build (dry-run rule inspection,
reading the failing Dockerfile/source directly) — neither is environment- or
mirror-specific; they reproduce from a clean `202511` clone.

**5a. `platform/vpp/rules.mk` never includes `docker-sonic-vpp.mk`.** The
file `platform/vpp/rules/docker-sonic-vpp.mk` exists and is well-formed (it
depends only on standard, already-registered SONiC components), but
`platform/vpp/rules.mk` never `include`s it — even though its own last line
references `$(DOCKER_SONIC_VPP)`, a variable only `docker-sonic-vpp.mk`
defines. Without the include, that reference is silently empty and
`target/docker-sonic-vpp.gz` has **no rule at all** — `make` fails with
`No rule to make target 'target/docker-sonic-vpp.gz'.  Stop.`, deep inside a
`docker run` into the slave container, easy to miss among other noise. This
is also why the *official* CI VPP build artifact doesn't produce
`docker-sonic-vpp.gz` either — it's the same missing include, not something
specific to this build attempt.

Fix:

```sh
sed -i '/include $(PLATFORM_RULES)\/docker-gbsyncd-vpp.mk/a include $(PLATFORM_RULES)/docker-sonic-vpp.mk' platform/vpp/rules.mk
```

**5b. `sonic-host-services`'s bundled pytest suite fails inside a build
container**, and separately, its unversioned `PyGObject` dependency pulls an
incompatible release. Fix both:

```sh
# skip sonic-host-services' pytest run (needs a real device/platform dir —
# unrelated to VPP dataplane correctness; the build system has a
# purpose-built flag for exactly this)
echo '$(SONIC_HOST_SERVICES_PY3)_TEST = n' >> rules/sonic-host-services.mk
```

Then in `platform/vpp/docker-sonic-vpp/Dockerfile.j2`, right before the
per-wheel `pip install` loop (look for the comment `# use py3 to find
python3 package, which is forced by wheel as of now`), insert:

```
RUN pip3 install "PyGObject<3.50"
```

`sonic-host-services/setup.py` lists a bare `'PyGObject'` with no version
constraint, so pip grabs whatever's newest on PyPI (3.58.0 as of this
writing), which requires the newer `girepository-2.0` pkg-config API.
Bookworm only ships `libgirepository1.0-dev` (1.74.0, the *older* 1.0 API) —
which this same Dockerfile already installs and later purges, clearly
written against an older PyGObject that only needed 1.0. Pre-installing a
`<3.50` constraint satisfies the dependency before `sonic_host_services`'
wheel install ever looks for it, avoiding the incompatible from-source build
entirely.

**5c. `docker-sonic-vpp.mk` never depends on the actual VPP package.**
Fixing 5a gets the rule registered, but the build still fails with
`vpp_init.sh: line 89: /usr/bin/vpp: No such file or directory` at container
boot (not build time — this one only shows up once you actually deploy and
`docker exec` in). `rules/vpp.mk` defines `VPP_MAIN` (the real `vpp_*.deb`)
and `VPP_PLUGIN_CORE` (needed for the `af_packet_plugin.so` a veth-only
container actually uses), but `docker-sonic-vpp.mk`'s `_DEPENDS` list never
references either — only `$(SYNCD_VPP)`, a variable that is **defined
nowhere in the entire tree** (grep confirms it; likely a rename/refactor
that never got propagated here). Fix:

```sh
sed -i '/\$(DOCKER_SONIC_VPP)_DEPENDS += \$(SYNCD_VPP)/i $(DOCKER_SONIC_VPP)_DEPENDS += $(VPP_MAIN) $(VPP_PLUGIN_CORE)' platform/vpp/rules/docker-sonic-vpp.mk
```

**5d. `docker-sonic-vpp.mk` also depends on `$(SYNCD_VPP)` (undefined) for
the syncd binary**, and separately `vppcfgd` (the process that pushes VPP
config from `config_db`) fails with `ERROR (no such file)` at boot even
after installing `sonic_vppcfgd`'s wheel:

- Replace the dead `$(SYNCD_VPP)` reference with `$(SYNCD_VS)` — yes, `_VS`
  ("virtual switch"), not a typo. This is the same package
  `docker-syncd-vpp.mk`/`docker-gbsyncd-vpp.mk` (the platform's own sibling
  images, which *do* build successfully) depend on for their syncd binary
  too — see 5e below for what this actually means.
- `platform/vpp/rules.mk` never includes `platform/vpp/rules/vppcfgd.mk`
  either (same missing-include pattern as 5a). Add it:
  `sed -i '/include $(PLATFORM_RULES)\/docker-sonic-vpp.mk/a include $(PLATFORM_RULES)/vppcfgd.mk' platform/vpp/rules.mk`
- Even with that include, `vppcfgd.mk`'s own `_SRC_PATH` is wrong —
  `$(SRC_PATH)/sonic-vppcfgd` (a top-level `src/` path that doesn't exist)
  instead of `$(PLATFORM_PATH)/platform/mkrules/src/sonic-vppcfgd` (where the
  source actually lives inside the `sonic-platform-vpp` submodule's own
  nested tree). Fix: `sed -i 's#$(SRC_PATH)/sonic-vppcfgd#$(PLATFORM_PATH)/platform/mkrules/src/sonic-vppcfgd#' platform/vpp/rules/vppcfgd.mk`

**5e. IMPORTANT — even with all of 5a-5d applied, `syncd` links against the
reference stub `libsaivs.so.0`, not real `libsaivpp`.** Confirmed three
independent ways: `ldd $(which syncd)` inside a running container shows
`libsaivs.so.0`; `dpkg -l` describes the installed package as *"sync daemon
for SONiC project linked with virtual switch"*; and configuring an IP on an
interface via SONiC's own CLI never reaches VPP's actual state (`vppctl show
int addr` stays empty/down). This is **not specific to this build** — the
*official* Microsoft CI artifact's `docker-syncd-vpp.gz` (pulled from the
same pipeline that produces `sonic-vpp.img.gz`) shows the identical
`libsaivs.so.0` linkage. `libsaivpp`'s source exists in the tree
(`saivpp/`, `platform/mkrules/src/sonic-sairedis/debian/libsaivpp.install`)
but nothing in the current build graph — upstream included — actually
compiles/selects it over the stub. **Practical consequence: VPP runs as a
real, independent process, but nothing in the SAI/orchagent pipeline tells
it about routes, interfaces, or SRv6 SIDs.** FRR/BGP control-plane
convergence works fully; real dataplane forwarding through VPP does not.
Getting that would mean understanding how `sonic-sairedis` is supposed to
select a SAI backend and rewiring `syncd-vpp.mk` to build+depend on the real
thing — a materially bigger project than 5a-5d, not attempted here.

## 6. Build the docker-sonic-vpp target

**Do not use the top-level `make target/docker-sonic-vpp.gz`.** The
top-level `Makefile`'s catch-all rule fans out to *both* bookworm and trixie
builds by default (`NOBOOKWORM`/`NOTRIXIE` both default to enabled), routes
through a named `bookworm` target plus an `EXTRA_DOCKER_TARGETS` hint, and
that path silently never reaches `docker-sonic-vpp` at all — it'll run for
a long time, build unrelated things, and then fail on the (expected, since
trixie has no `docker-sonic-vpp` support) trixie leg, masking whether
anything real happened. Invoke `Makefile.work` directly instead, asking for
the exact target:

```sh
make -f Makefile.work PLATFORM=vpp BLDENV=bookworm target/docker-sonic-vpp.gz
```

This is the container image alone — enough for containerlab. If you also
want a full installer image (ONIE/ISO, what CI's own VPP pipeline stage
builds), use `target/sonic-vpp.img.gz` instead; it's a superset and takes
longer, and — per the official CI artifact inspected while debugging this —
produces the standard *split multi-container* SONiC image (many
`docker-<name>.gz` files), not the single-container `docker-sonic-vpp` this
topology needs.

Expect the *first* build to be slow (full dependency graph from scratch).
Incremental rebuilds after small changes are much faster — gbsyncd-vpp and
syncd-vpp, once built, stay cached across retries of this step.

## 7. Load and verify the image tag

```sh
docker load -i target/docker-sonic-vpp.gz
docker images | grep sonic-vpp
```

This repo's generator (`topogen2/polarfly_clab.py --variant sonic-vpp`)
assumes the image is tagged exactly `docker-sonic-vpp:latest`. If `docker
load` produced something else, retag it:

```sh
docker tag <loaded-tag> docker-sonic-vpp:latest
```

## 8. Check the FRR build for the BGP/SRv6 features you actually want

Since the point of building `202511` yourself is newer FRR SRv6/BGP support,
don't assume it — check the version and available `segment-routing srv6`
subcommands against what `202511`'s FRR package actually ships, once you
have a running container (step 9), e.g.:

```sh
docker exec -it sw001 vtysh -c "show version"
docker exec -it sw001 vtysh -c "conf t" -c "segment-routing" -c "srv6" -c "?"
```

## 9. Deploy into the q7 VPP topology

```sh
cd ../polarfly/q7/sonic-vpp
sudo containerlab deploy -t sonic-polarfly-q7-nobinds.clab.yaml
```

This is the real test of whether the image actually boots correctly under
containerlab — see the open item below.

## Addendum: `sonic-buildimage` master builds clean, no patches needed

After landing on all of 5a-5e above, a fresh clone of `sonic-buildimage`'s
own `master` branch (not `202511`) was tried as a comparison —
`platform/vpp` there is pinned 54 commits ahead of `202511`'s pin (3 commits
behind `sonic-platform-vpp`'s own tip). Result: **`docker-sonic-vpp.mk`,
`vpp.mk`, and `vppcfgd.mk` are already correctly `include`d, and
`docker-sonic-vpp.mk` already depends on `$(SYNCD_VS)` correctly** — i.e.
fixes 5a/5c/5d are already upstreamed on `master`. It also now builds from
`docker-swss-layer-trixie` (confirmed present on `master`, unlike `202511`),
so this path gets you genuine trixie, not bookworm:

```sh
git clone https://github.com/sonic-net/sonic-buildimage.git   # master, default branch
cd sonic-buildimage
make init
NOBULLSEYE=1 NOBUSTER=1 make configure PLATFORM=vpp   # BLDENV defaults to trixie
make -f Makefile.work PLATFORM=vpp BLDENV=trixie target/docker-sonic-vpp.gz
```

No `-f Makefile.work` workaround needed for `configure` (the top-level
`make configure` is fine there), but step 6's advice about the direct
`Makefile.work` invocation for the actual build target still applies. Built
clean end-to-end with zero patches on 2026-09-07: VPP 26.06, FRR 10.5.4,
477MB loaded image. **5e (stub `libsaivs`, not real `libsaivpp`) is
unchanged and still present** — confirmed via the identical `ldd`/`dpkg -l`
checks. If you want trixie specifically, start from master, not `202511`,
and skip straight to 5e's finding once you hit it — 5a/5c/5d don't apply
there.

## Risks / open items

- **The 202511 patches (5a-5e) are local to that checkout only**, applied
  directly to files under the `platform/vpp` git submodule and `rules/`.
  They are not upstreamed. Re-cloning or re-running `git submodule update`
  will lose them — keep this doc as the record, and re-apply after any
  fresh `202511` clone. Not needed at all if you build from `master`
  instead (see addendum above).
- **The real blocker is 5e, not 5a-5d.** Confirmed on `202511`, on
  `sonic-buildimage` master/trixie, and on the official Microsoft CI
  artifact: `docker-sonic-vpp`/`docker-syncd-vpp` link against the
  reference `libsaivs` stub, not real `libsaivpp`, on every path currently
  reachable through this build system. VPP itself boots and runs
  correctly (confirmed via `vppctl`, `af_packet` bound to the containerlab
  veth); FRR/BGP control-plane convergence works fully (confirmed:
  `vtysh`, `show running-config`). But nothing bridges SONiC's SAI/orchagent
  pipeline to VPP's actual state — this build is control-plane-only, not a
  working dataplane, regardless of branch. Treat 5a-5d (and their
  already-fixed equivalents on master) as "gets you a bootable image," not
  "gets you a working switch."
- If `make init` / `make configure` fail on proxy or DNS lookups, check
  `http_proxy` / `https_proxy` — common on corporate networks and not
  specific to this branch.
- Confirm disk space *before* starting; a build failing halfway through from
  a full disk is a slow way to find out.
