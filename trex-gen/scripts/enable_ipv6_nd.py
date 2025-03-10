#!/usr/bin/env python3
from trex_stl_lib.api import *
import argparse
import yaml
import os
import sys

def load_host_config(topology, host, config_dir='../config'):
    """Load configuration for a specific host"""
    config_file = os.path.join(config_dir, 'topologies', f'{topology}.yaml')
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            
        if host not in config['hosts']:
            print(f"Error: Host {host} not found in topology {topology}")
            return None
            
        return config['hosts'][host]
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def enable_ipv6_nd(host_config, server='localhost', ports=None):
    """Enable IPv6 ND on specified ports using host configuration"""
    if ports is None:
        ports = [0, 1]  # Default to first two ports
        
    client = STLClient(server=server)
    
    try:
        # connect to server
        client.connect()
        
        # Enable service mode on ports
        client.set_service_mode(ports=ports, enabled=True)
        print(f"Enabled service mode on ports {ports}")
        
        # Configure IPv6 and enable ND on each port
        for port_idx, port in enumerate(ports):
            if port_idx >= len(host_config['interfaces']):
                print(f"Warning: No interface configuration for port {port}, skipping")
                continue
                
            interface = host_config['interfaces'][port_idx]
            
            # Set IPv6 configuration
            client.set_port_attr(port=port, attr_name='ipv6', attr_value=interface['ipv6'])
            client.set_port_attr(port=port, attr_name='ipv6_subnet', attr_value=interface['ipv6_subnet'])
            client.set_port_attr(port=port, attr_name='ipv6_nd_enabled', attr_value=True)
            client.set_port_attr(port=port, attr_name='src_ipv6_enabled', attr_value=True)
            
            print(f"Configured IPv6 {interface['ipv6']} with subnet {interface['ipv6_subnet']} on port {port}")
            print(f"Enabled IPv6 ND on port {port}")
        
        print("\nIPv6 ND is now enabled. Press Ctrl+C to exit...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except STLError as e:
        print(f"Error: {e}")
    finally:
        if client.is_connected():
            # Disable service mode before disconnecting
            client.set_service_mode(ports=ports, enabled=False)
            client.disconnect()

def main():
    parser = argparse.ArgumentParser(description='Enable IPv6 ND on TRex ports')
    parser.add_argument('topology', help='Topology name')
    parser.add_argument('host', help='Host name')
    parser.add_argument('-s', '--server', type=str, default='localhost',
                        help='TRex server address')
    parser.add_argument('-p', '--ports', type=int, nargs='+', default=[0, 1],
                        help='Ports to enable IPv6 ND on')
    parser.add_argument('--config-dir', default='../config', 
                        help='Configuration directory')
    
    args = parser.parse_args()
    
    # Load host configuration
    host_config = load_host_config(args.topology, args.host, args.config_dir)
    if not host_config:
        sys.exit(1)
        
    # Enable IPv6 ND
    enable_ipv6_nd(host_config, args.server, args.ports)

if __name__ == "__main__":
    main() 