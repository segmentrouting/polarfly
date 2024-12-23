#!/usr/bin/env python3

import yaml
from pathlib import Path

def verify_polarfly_topology(links):
    # Track all connections and interfaces used
    node_connections = {f"node{i:02d}": set() for i in range(57)}
    node_interfaces = {f"node{i:02d}": set() for i in range(57)}
    
    # Parse each link
    for link in links:
        endpoints = link['endpoints']
        node1, intf1 = endpoints[0].split(':')
        node2, intf2 = endpoints[1].split(':')
        
        # Track connections
        node_connections[node1].add(node2)
        node_connections[node2].add(node1)
        
        # Track interfaces
        node_interfaces[node1].add(intf1)
        node_interfaces[node2].add(intf2)
    
    errors_found = False
    
    # Verify each node
    for node in sorted(node_connections.keys()):
        # Check connection count
        conn_count = len(node_connections[node])
        if not (7 <= conn_count <= 8):
            print(f"Error: {node} has {conn_count} connections")
            errors_found = True
            
        # Check interface sequence
        interfaces = sorted(list(node_interfaces[node]))
        for i, intf in enumerate(interfaces):
            expected = f"Gi0-0-0-{i}"
            if intf != expected:
                print(f"Error: {node} has out of sequence interface {intf}, expected {expected}")
                errors_found = True
        
        # Print summary
        print(f"{node}: {conn_count} connections, interfaces: {interfaces}")
    
    if not errors_found:
        print("\nVerification passed! No errors found in the topology.")
    else:
        print("\nVerification failed! Please check the errors above.")

def main():
    # Read the topology file
    topology_file = Path('../xrd/polarfly-topology.yml')
    with open(topology_file, 'r') as f:
        topology = yaml.safe_load(f)
    
    # Verify the topology
    verify_polarfly_topology(topology['topology']['links'])

if __name__ == "__main__":
    main() 