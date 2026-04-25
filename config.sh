#!/bin/bash
# Config script for SRv6 SONiC lab
# Pushes config_db.json and frr.conf to all SONiC containers
# Usage: ./deploy.sh [all|frh|lrh|dc|<node_name>]

set +e

SCOPE="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIGS_DIR="$SCRIPT_DIR/config-sonic"

# All node names
ALL_NODES="frh1 frh2 lrh1 lrh2 lrh3 lrh4 dc1-t2 dc2-t2 dc3-t2"
FRH_NODES="frh1 frh2"
LRH_NODES="lrh1 lrh2 lrh3 lrh4"
DC_NODES="dc1-t2 dc2-t2 dc3-t2"

deploy_node() {
    local NODE_ID="$1"
    local CONTAINER="$NODE_ID"

    echo "  Deploying $NODE_ID -> $CONTAINER"

    if ! docker inspect "$CONTAINER" &>/dev/null; then
        echo "    SKIP: container $CONTAINER not found"
        return 1
    fi

    # Create Loopback0 if missing
    docker exec "$CONTAINER" bash -c "ip link show Loopback0 &>/dev/null || { ip link add Loopback0 type dummy && ip link set Loopback0 up; }" 2>/dev/null || true

    # Copy config_db.json
    if [ -f "$CONFIGS_DIR/$NODE_ID/config_db.json" ]; then
        docker cp "$CONFIGS_DIR/$NODE_ID/config_db.json" "$CONTAINER:/etc/sonic/config_db.json"
        echo "    config_db.json copied"
    else
        echo "    WARN: no config_db.json found for $NODE_ID"
    fi

    # Reload SONiC config
    docker exec "$CONTAINER" bash -c "sonic-cfggen -j /etc/sonic/config_db.json --write-to-db" 2>/dev/null || true
    docker exec "$CONTAINER" bash -c "supervisorctl restart all" 2>/dev/null || true
    echo "    config reloaded"

    # Setup VRF default and sysctl
    docker exec "$CONTAINER" ip link add vrfdefault type vrf table main 2>/dev/null || true
    docker exec "$CONTAINER" ip link set vrfdefault up 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.vrf.strict_mode=1 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.ipv4.conf.vrfdefault.rp_filter=0 2>/dev/null || true
    docker exec "$CONTAINER" ip link add sr0 type dummy 2>/dev/null || true
    docker exec "$CONTAINER" ip link set sr0 up 2>/dev/null || true
    docker exec "$CONTAINER" sysctl -w net.ipv6.conf.all.forwarding=1 2>/dev/null || true
    echo "    vrfdefault, sr0, and sysctl configured"

    # Enable ports (admin up) - SONiC default may have them down
    docker exec "$CONTAINER" bash -c 'for port in $(sonic-cfggen -d --var-json PORT | python3 -c "import sys,json; print(\" \".join(json.load(sys.stdin).keys()))"); do config interface startup $port 2>/dev/null; done' 2>/dev/null || true

    # Wait for FRR to be ready
    for i in $(seq 1 30); do
        if docker exec "$CONTAINER" vtysh -c "show version" &>/dev/null; then
            break
        fi
        sleep 2
    done

    # Copy and load FRR config
    if [ -f "$CONFIGS_DIR/$NODE_ID/frr.conf" ]; then
        # Find FRR config directory
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

        # Restart FRR to pick up new config cleanly
        docker exec "$CONTAINER" supervisorctl stop bgpd zebra staticd 2>/dev/null || true
        sleep 2
        docker exec "$CONTAINER" supervisorctl start bgpd zebra staticd 2>/dev/null || true
        sleep 3
        # Clear default BGP config and load custom
        docker exec "$CONTAINER" vtysh -c "configure terminal" -c "no router bgp 65100" -c "exit" 2>/dev/null || true
        docker exec "$CONTAINER" vtysh -f "$FRR_DIR/frr.conf" 2>/dev/null || true
        echo "    frr.conf loaded"
    else
        echo "    WARN: no frr.conf found for $NODE_ID"
    fi

    echo "    OK: $NODE_ID deployed"
}

deploy_group() {
    local NODES="$1"
    local GROUP_NAME="$2"
    echo "=== Deploying $GROUP_NAME (parallel) ==="
    for node in $NODES; do
        deploy_node "$node" &
    done
    wait
    echo "=== $GROUP_NAME done ==="
    echo ""
}

case "$SCOPE" in
    all)
        deploy_group "$FRH_NODES" "FRH tier"
        deploy_group "$LRH_NODES" "LRH tier"
        deploy_group "$DC_NODES" "DC tier"
        ;;
    frh)  deploy_group "$FRH_NODES" "FRH tier" ;;
    lrh)  deploy_group "$LRH_NODES" "LRH tier" ;;
    dc)   deploy_group "$DC_NODES" "DC tier" ;;
    *)
        # Single node
        if echo "$ALL_NODES" | grep -qw "$SCOPE"; then
            deploy_node "$SCOPE"
        else
            echo "Unknown scope: $SCOPE"
            echo "Valid: all, frh, lrh, dc, or node name (frh1, lrh1, dc1-t2, etc.)"
            exit 1
        fi
        ;;
esac

echo ""
echo "============================================================"
echo "  SRv6 Fabric Summary"
echo "============================================================"
echo "  Confed AS:  64915"
echo "  FRH (AS 100):  frh1, frh2        — SRv6 locators fc00:0:1::/48, fc00:0:2::/48"
echo "  LRH (AS 300):  lrh1-4            — SRv6 locators fc00:0:21-24::/48"
echo "  DC T2:         dc1-t2 (AS 64900) — 10.100.1.0/24"
echo "                 dc2-t2 (AS 64901) — 10.100.2.0/24"
echo "                 dc3-t2 (AS 64902) — 10.100.3.0/24"
echo "============================================================"
echo ""
echo "Deploy complete!"
