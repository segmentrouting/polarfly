#!/bin/bash
# polarfly config deploy script.
#
# This script lives at polarfly/q<q>/q<q>-config.sh and consumes per-switch
# config_db.json + frr.conf from polarfly/q<q>/sonic-config/sw###/.
#
# It auto-discovers all sw### containers spawned by containerlab and pushes
# the matching configs into them, plus the SRv6/VRF kernel state that bind
# mounts can't do (sysctl, vrfdefault, sr0 dummy, kernel admin-up).
#
# Usage:
#   ./qN-config.sh                  # configure ALL sw### containers in parallel
#   ./qN-config.sh --jobs 16        # cap parallelism at 16 (default: 32)
#   ./qN-config.sh --serial         # one at a time
#   ./qN-config.sh swNNN [swNNN...] # configure specific switches only
#
# Prerequisites:
#   sudo containerlab deploy -t sonic-polarfly-qN-nobinds.clab.yaml
#   (the binds variant works too, but isn't required - this script docker cp's
#    the configs at runtime.)

set +e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIGS_DIR="$SCRIPT_DIR/sonic-config"

# Derive q from the parent directory name (q7, q13, ...). Used only for the
# summary banner; the script logic itself is q-independent.
Q_FROM_DIR="$(basename "$SCRIPT_DIR" | sed -n 's/^q\([0-9][0-9]*\)$/\1/p')"
Q="${Q_FROM_DIR:-?}"

# Pattern to match Polarfly switch containers. Containerlab with prefix: ""
# names containers exactly after the node name (sw001, sw002, ...).
SWITCH_REGEX='^sw[0-9]{3}$'

# Default parallel job cap (overridable with --jobs N).
DEFAULT_JOBS=32

discover_switches() {
    docker ps --format '{{.Names}}' | awk -v re="$SWITCH_REGEX" '$0 ~ re' | sort
}

deploy_node() {
    local NODE_ID="$1"
    local CONTAINER="$NODE_ID"

    echo "  Deploying $NODE_ID -> $CONTAINER"

    if ! docker inspect "$CONTAINER" &>/dev/null; then
        echo "    SKIP: container $CONTAINER not found"
        return 1
    fi

    if [ ! -d "$CONFIGS_DIR/$NODE_ID" ]; then
        echo "    SKIP: $CONFIGS_DIR/$NODE_ID does not exist"
        return 1
    fi

    # Create Loopback0 if missing (SONiC won't create dummy loopbacks itself)
    docker exec "$CONTAINER" bash -c \
        "ip link show Loopback0 &>/dev/null || { ip link add Loopback0 type dummy && ip link set Loopback0 up; }" \
        2>/dev/null || true

    # Push config_db.json
    if [ -f "$CONFIGS_DIR/$NODE_ID/config_db.json" ]; then
        docker cp "$CONFIGS_DIR/$NODE_ID/config_db.json" \
            "$CONTAINER:/etc/sonic/config_db.json"
        echo "    config_db.json pushed"
    else
        echo "    WARN: no config_db.json found for $NODE_ID"
    fi

    # IMPORTANT: bring kernel netdevs up FIRST. containerlab attaches veth pairs
    # AFTER sonic-vs has booted; without this step intfmgrd silently skips IP
    # assignment for not-yet-existent interfaces. Note that sonic-vs has
    # already renamed the eth1..ethN containerlab veths to Ethernet0..EthernetN
    # via syncd's virtual SAI hostif binding, so we look for Ethernet*.
    docker exec "$CONTAINER" bash -c '
        for nd in $(ls /sys/class/net | grep -E "^Ethernet[0-9]+$"); do
            ip link set "$nd" mtu 9100 up 2>/dev/null
        done
    ' 2>/dev/null || true
    echo "    Ethernet netdevs brought up at kernel level"

    # Reload SONiC config DB and restart all SONiC services.
    docker exec "$CONTAINER" bash -c \
        "sonic-cfggen -j /etc/sonic/config_db.json --write-to-db" \
        2>/dev/null || true
    docker exec "$CONTAINER" bash -c "supervisorctl restart all" 2>/dev/null || true
    echo "    SONiC config reloaded"

    # Linux-side prerequisites for SRv6 / VRF that SONiC doesn't manage
    docker exec "$CONTAINER" ip link add vrfdefault type vrf table main 2>/dev/null || true
    docker exec "$CONTAINER" ip link set vrfdefault up 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.vrf.strict_mode=1 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.ipv4.conf.vrfdefault.rp_filter=0 2>/dev/null || true
    docker exec "$CONTAINER" ip link add sr0 type dummy 2>/dev/null || true
    docker exec "$CONTAINER" ip link set sr0 up 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.ipv6.conf.all.forwarding=1 2>/dev/null || true
    echo "    vrfdefault, sr0, and sysctl configured"

    # Re-assert kernel admin-up after supervisorctl restart, plus per-iface
    # IPv6 forwarding and disable RA so static addresses stick.
    docker exec "$CONTAINER" bash -c '
        for nd in $(ls /sys/class/net | grep -E "^Ethernet[0-9]+$"); do
            ip link set "$nd" up 2>/dev/null
            sysctl -w net.ipv6.conf.$nd.forwarding=1 2>/dev/null
            sysctl -w net.ipv6.conf.$nd.accept_ra=0 2>/dev/null
        done
    ' 2>/dev/null || true
    echo "    Ethernet netdevs re-asserted up after service restart"

    # Re-write config DB in case the supervisor restart raced with an empty DB.
    docker exec "$CONTAINER" bash -c \
        'sonic-cfggen -j /etc/sonic/config_db.json --write-to-db 2>/dev/null' \
        2>/dev/null || true

    # Wait for FRR vtysh to come up
    for _ in $(seq 1 30); do
        if docker exec "$CONTAINER" vtysh -c "show version" &>/dev/null; then
            break
        fi
        sleep 2
    done

    # Push and load FRR config
    if [ -f "$CONFIGS_DIR/$NODE_ID/frr.conf" ]; then
        local FRR_DIR=""
        if docker exec "$CONTAINER" test -d /etc/sonic/frr 2>/dev/null; then
            FRR_DIR="/etc/sonic/frr"
        elif docker exec "$CONTAINER" test -d /etc/frr 2>/dev/null; then
            FRR_DIR="/etc/frr"
        else
            FRR_DIR="/etc/sonic/frr"
            docker exec "$CONTAINER" mkdir -p "$FRR_DIR" 2>/dev/null || true
        fi

        docker cp "$CONFIGS_DIR/$NODE_ID/frr.conf" "$CONTAINER:$FRR_DIR/frr.conf"
        echo "    frr.conf copied to $FRR_DIR/frr.conf"

        # Restart FRR daemons cleanly
        docker exec "$CONTAINER" supervisorctl stop bgpd zebra staticd 2>/dev/null || true
        sleep 2
        docker exec "$CONTAINER" supervisorctl start bgpd zebra staticd 2>/dev/null || true
        sleep 3

        # Purge SONiC's default 'router bgp 65100' stub before applying ours.
        docker exec "$CONTAINER" vtysh \
            -c "configure terminal" -c "no router bgp 65100" -c "exit" \
            2>/dev/null || true
        docker exec "$CONTAINER" vtysh -f "$FRR_DIR/frr.conf" 2>/dev/null || true
        echo "    frr.conf loaded"
    else
        echo "    WARN: no frr.conf found for $NODE_ID"
    fi

    echo "    OK: $NODE_ID deployed"
}

# Run jobs in parallel with a concurrency cap. Pure bash; no GNU parallel needed.
deploy_throttled() {
    local NODES="$1"
    local JOBS="$2"
    local count=0
    local total
    total=$(echo "$NODES" | wc -w)
    echo "=== Deploying $total switches with concurrency=$JOBS ==="
    for n in $NODES; do
        deploy_node "$n" &
        count=$((count + 1))
        # Throttle: wait for any job to finish once we hit the cap
        if [ "$count" -ge "$JOBS" ]; then
            wait -n 2>/dev/null || wait
            count=$((count - 1))
        fi
    done
    wait
    echo "=== throttled batch done ==="
}

deploy_serial() {
    local NODES="$1"
    local total
    total=$(echo "$NODES" | wc -w)
    echo "=== Deploying $total switches serially ==="
    for n in $NODES; do
        deploy_node "$n"
    done
    echo "=== serial batch done ==="
}

# -----------------------------------------------------------------------------
# Argument dispatch
# -----------------------------------------------------------------------------
SERIAL=0
JOBS="$DEFAULT_JOBS"
NODE_ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --serial) SERIAL=1; shift ;;
        --jobs)
            JOBS="$2"
            if ! [[ "$JOBS" =~ ^[0-9]+$ ]] || [ "$JOBS" -lt 1 ]; then
                echo "ERROR: --jobs needs a positive integer"
                exit 2
            fi
            shift 2
            ;;
        --jobs=*) JOBS="${1#--jobs=}"; shift ;;
        --help|-h)
            sed -n '2,22p' "$0"
            exit 0
            ;;
        *) NODE_ARGS+=("$1"); shift ;;
    esac
done

if [ "${#NODE_ARGS[@]}" -gt 0 ]; then
    NODES="${NODE_ARGS[*]}"
else
    NODES="$(discover_switches | tr '\n' ' ')"
fi

if [ -z "${NODES// }" ]; then
    echo "ERROR: no Polarfly switch containers found. Did containerlab deploy succeed?"
    echo "Looking for containers matching: $SWITCH_REGEX"
    exit 1
fi

echo "Targets: $(echo "$NODES" | wc -w) switches"
echo ""

if [ "$SERIAL" -eq 1 ]; then
    deploy_serial "$NODES"
else
    deploy_throttled "$NODES" "$JOBS"
fi

# -----------------------------------------------------------------------------
# Summary banner (computed from q)
# -----------------------------------------------------------------------------
if [ "$Q" != "?" ]; then
    N=$(( Q*Q + Q + 1 ))
    R=$(( Q + 1 ))
    LAST_FAB=$(( (R - 1) * 4 ))           # last fabric Ethernet index (eg q=7 -> 28)
    HOST_PORT=$(( R * 4 ))                # host port (eg q=7 -> Ethernet32, q=13 -> Ethernet56)
    ABS=$(( Q + 1 ))
    ASN_LO=65001
    ASN_HI=$(( 65000 + N ))
fi

echo ""
echo "============================================================"
echo "  Polarfly q=${Q} SONiC-VS Fabric"
echo "============================================================"
if [ "$Q" != "?" ]; then
    echo "  Switches:        ${N}       (sw$(printf %03d 1)..sw$(printf %03d $N))"
    echo "  Fabric radix:    ${R}        (Ethernet0..Ethernet${LAST_FAB}; absolute pts have radix $((R-1)))"
    echo "  Host port:       Ethernet${HOST_PORT}"
    echo "  Absolute points: ${ABS}"
    echo "  Locator pattern: fc00:0:1<NNN>::/48 per switch"
    echo "  uA SIDs:         fc00:0:f<port>::/48 (port = local fabric idx 0..$((R-1)))"
    echo "  uDT6 SID:        fc00:0:1<NNN>:e000::/64 -> Vrf-tenant"
    echo "  P2P fabric:      2001:db8:1:<edge>::/127"
    echo "  ASNs:            ${ASN_LO}..${ASN_HI} (eBGP)"
fi
echo "============================================================"
echo ""
echo "Deploy complete!"
