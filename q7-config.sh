#!/bin/bash
# q7-config.sh — Polarfly q=7 SONiC-VS lab configuration deploy script
#
# Adapted from ../config.sh (legacy SRv6 SONiC lab) for the Polarfly fabric.
# Auto-discovers all sw### containers spawned by containerlab and pushes
# the matching q7/<sw>/{config_db.json,frr.conf} configs.
#
# Usage:
#   ./q7-config.sh                  # configure ALL sw### containers in parallel
#   ./q7-config.sh swNNN [swNNN...] # configure specific switches
#   ./q7-config.sh --serial         # configure all, but one at a time
#
# Prerequisites:
#   1. Topology deployed:
#        sudo containerlab deploy -t sonic-polarfly-q7.clab.yaml
#   2. binds: in the YAML have already mounted config_db.json + frr.conf at
#        /etc/sonic/config_db.json and /etc/sonic/frr/frr.conf
#      This script still ensures the configs are loaded into running SONiC
#      (sonic-cfggen --write-to-db) and into FRR (vtysh -f), and applies the
#      sysctl / dummy-iface / vrfdefault setup that bind mounts can't do.

set +e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIGS_DIR="$SCRIPT_DIR/q7"

# Pattern to match Polarfly switch containers. Containerlab with prefix: ""
# names containers exactly after the node name (sw001, sw002, ...).
SWITCH_REGEX='^sw[0-9]{3}$'

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

    # Push config_db.json into running SONiC (bind mount also covers /etc/sonic
    # at startup, but a re-deploy after the container is running needs this).
    if [ -f "$CONFIGS_DIR/$NODE_ID/config_db.json" ]; then
        docker cp "$CONFIGS_DIR/$NODE_ID/config_db.json" \
            "$CONTAINER:/etc/sonic/config_db.json"
        echo "    config_db.json pushed"
    else
        echo "    WARN: no config_db.json found for $NODE_ID"
    fi

    # IMPORTANT: bring the kernel netdevs up FIRST. containerlab attaches the
    # Ethernet veth pairs after sonic-vs has already booted, so portmgrd/intfmgrd
    # never noticed them and they sit admin-down with no IPv6. We need them up
    # at the kernel level before sonic-cfggen --write-to-db, otherwise intfmgrd
    # silently skips the IP assignment for not-yet-existent interfaces.
    docker exec "$CONTAINER" bash -c '
        for nd in $(ls /sys/class/net | grep -E "^Ethernet[0-9]+$"); do
            ip link set "$nd" mtu 9100 up 2>/dev/null
        done
    ' 2>/dev/null || true
    echo "    Ethernet netdevs brought up at kernel level"

    # Now reload SONiC config DB and restart all SONiC services so intfmgrd
    # runs against ports that already exist as kernel netdevs.
    docker exec "$CONTAINER" bash -c \
        "sonic-cfggen -j /etc/sonic/config_db.json --write-to-db" \
        2>/dev/null || true
    docker exec "$CONTAINER" bash -c "supervisorctl restart all" 2>/dev/null || true
    echo "    SONiC config reloaded"

    # Linux-side prerequisites for SRv6 / VRF that SONiC doesn't manage:
    docker exec "$CONTAINER" ip link add vrfdefault type vrf table main 2>/dev/null || true
    docker exec "$CONTAINER" ip link set vrfdefault up 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.vrf.strict_mode=1 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.ipv4.conf.vrfdefault.rp_filter=0 2>/dev/null || true
    docker exec "$CONTAINER" ip link add sr0 type dummy 2>/dev/null || true
    docker exec "$CONTAINER" ip link set sr0 up 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.ipv6.conf.all.forwarding=1 2>/dev/null || true
    echo "    vrfdefault, sr0, and sysctl configured"

    # Re-assert kernel admin-up after supervisorctl restart (services may have
    # taken interfaces down during restart). Also enable IPv6 per-iface forwarding
    # and disable autoconf so static addresses stick.
    docker exec "$CONTAINER" bash -c '
        for nd in $(ls /sys/class/net | grep -E "^Ethernet[0-9]+$"); do
            ip link set "$nd" up 2>/dev/null
            sysctl -w net.ipv6.conf.$nd.forwarding=1 2>/dev/null
            sysctl -w net.ipv6.conf.$nd.accept_ra=0 2>/dev/null
        done
    ' 2>/dev/null || true
    echo "    Ethernet netdevs re-asserted up after service restart"

    # If sonic-cfggen didn't apply INTERFACE IPs (e.g. intfmgrd race), do it
    # via redis-cli directly. This pokes APPL_DB which intfmgrd will reconcile.
    # (No-op if it already worked.)
    docker exec "$CONTAINER" bash -c '
        sonic-cfggen -j /etc/sonic/config_db.json --write-to-db 2>/dev/null
    ' 2>/dev/null || true

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

        # Restart the FRR daemons cleanly so they pick up only our config
        docker exec "$CONTAINER" supervisorctl stop bgpd zebra staticd 2>/dev/null || true
        sleep 2
        docker exec "$CONTAINER" supervisorctl start bgpd zebra staticd 2>/dev/null || true
        sleep 3

        # SONiC's default FRR ships with a stub 'router bgp 65100'. Purge it
        # before applying our config so neighbor/local-as values don't fight.
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

deploy_parallel() {
    local NODES="$1"
    echo "=== Deploying $(echo $NODES | wc -w) switches in parallel ==="
    for n in $NODES; do
        deploy_node "$n" &
    done
    wait
    echo "=== parallel batch done ==="
}

deploy_serial() {
    local NODES="$1"
    echo "=== Deploying $(echo $NODES | wc -w) switches serially ==="
    for n in $NODES; do
        deploy_node "$n"
    done
    echo "=== serial batch done ==="
}

# -----------------------------------------------------------------------------
# Argument dispatch
# -----------------------------------------------------------------------------
SERIAL=0
NODE_ARGS=()
for arg in "$@"; do
    case "$arg" in
        --serial) SERIAL=1 ;;
        --help|-h)
            sed -n '2,18p' "$0"
            exit 0
            ;;
        *) NODE_ARGS+=("$arg") ;;
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

echo "Targets: $NODES"
echo ""

if [ "$SERIAL" -eq 1 ]; then
    deploy_serial "$NODES"
else
    deploy_parallel "$NODES"
fi

echo ""
echo "============================================================"
echo "  Polarfly q=7 SONiC-VS Fabric"
echo "============================================================"
echo "  Switches:        57       (sw001..sw057)"
echo "  Fabric radix:    8        (Ethernet0..Ethernet28; absolute pts: 7)"
echo "  Host port:       Ethernet32"
echo "  Locator pattern: fc00:0:1<NNN>::/48 per switch"
echo "  uA SIDs:         fc00:0:f<port>::/48 (port = local fabric idx 0..7)"
echo "  uDT6 SID:        fc00:0:1<NNN>:e000::/64 -> Vrf-tenant"
echo "  P2P fabric:      2001:db8:1:<edge>::/127"
echo "  ASNs:            65001..65057 (eBGP)"
echo "============================================================"
echo ""
echo "Deploy complete!"
