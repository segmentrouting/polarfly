#!/usr/bin/env python3
"""
Traffic Controller for Polarfly Topology

This script controls traffic generation across multiple hosts in the Polarfly topology.
It can start and stop traffic with different patterns between specified source and destination hosts.

Usage:
  python3 traffic_generator.py radix-8 start --type imix --src host00 host01 --dst host02 host03
  python3 traffic_generator.py radix-8 stop --src host00 host01

Options:
  start/stop       Action to perform
  --type TYPE      Traffic type (imix, bulk, srv6_imix, srv6_bulk)
  --src HOSTS      Source hosts
  --dst HOSTS      Destination hosts
  -s, --server     TRex server address (default: localhost)
"""
import argparse
import yaml
import os
import sys
import time
from trex_stl_lib.api import *

def load_topology_config(topology, config_dir='../config'):
    """Load configuration for a topology"""
    config_file = os.path.join(config_dir, 'topologies', f'{topology}.yaml')
    
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

class TrafficController:
    def __init__(self, topology, config_dir='../config'):
        """Initialize the traffic controller"""
        self.topology = topology
        self.config = load_topology_config(topology, config_dir)
        if not self.config:
            raise ValueError(f"Failed to load configuration for topology {topology}")
            
        self.clients = {}
        
    def connect_to_hosts(self, hosts=None):
        """Connect to specified hosts or all hosts"""
        if hosts is None:
            hosts = self.config['hosts'].keys()
            
        for host in hosts:
            if host not in self.config['hosts']:
                print(f"Warning: Unknown host {host}, skipping")
                continue
                
            host_config = self.config['hosts'][host]
            try:
                client = STLClient(server=host_config['ip'])
                client.connect()
                client.reset()
                self.clients[host] = client
                print(f"Connected to {host} at {host_config['ip']}")
            except STLError as e:
                print(f"Failed to connect to {host}: {e}")
                
    def start_traffic(self, traffic_type, src_hosts=None, dst_hosts=None):
        """
        Start traffic from source hosts to destination hosts
        
        Args:
            traffic_type: Type of traffic ('imix', 'srv6-imix', 'bulk', 'srv6-bulk')
            src_hosts: List of source hosts (or None for all)
            dst_hosts: List of destination hosts (or None for all)
        """
        if src_hosts is None:
            src_hosts = list(self.clients.keys())
            
        # Map traffic type to script name
        script_map = {
            'imix': 'imix.py',
            'srv6-imix': 'srv6-imix.py',
            'bulk': 'bulk.py',
            'srv6-bulk': 'srv6-bulk.py'
        }
        
        script_name = script_map.get(traffic_type)
        if not script_name:
            print(f"Error: Unknown traffic type {traffic_type}")
            return
            
        for host in src_hosts:
            if host not in self.clients:
                print(f"Warning: Not connected to {host}, skipping")
                continue
                
            client = self.clients[host]
            try:
                # Reset port before starting traffic
                client.reset(ports=[0])
                
                # Start traffic with the appropriate script
                script_path = f"{host}/{script_name}"
                client.start_line(f" -f {script_path} --port 0")
                print(f"Started {traffic_type} traffic on {host}")
                
            except STLError as e:
                print(f"Failed to start traffic on {host}: {e}")
                
    def stop_traffic(self, hosts=None):
        """Stop traffic on specified hosts or all connected hosts"""
        if hosts is None:
            hosts = list(self.clients.keys())
            
        for host in hosts:
            if host not in self.clients:
                continue
                
            client = self.clients[host]
            try:
                client.stop(ports=[0])
                print(f"Stopped traffic on {host}")
            except STLError as e:
                print(f"Failed to stop traffic on {host}: {e}")
                
    def disconnect_all(self):
        """Disconnect from all connected hosts"""
        for host, client in list(self.clients.items()):
            try:
                client.disconnect()
                print(f"Disconnected from {host}")
                del self.clients[host]
            except STLError as e:
                print(f"Failed to disconnect from {host}: {e}")
                
    def get_stats(self, hosts=None):
        """Get traffic statistics from specified hosts or all connected hosts"""
        if hosts is None:
            hosts = list(self.clients.keys())
            
        stats = {}
        for host in hosts:
            if host not in self.clients:
                continue
                
            client = self.clients[host]
            try:
                host_stats = client.get_stats()
                stats[host] = host_stats
            except STLError as e:
                print(f"Failed to get stats from {host}: {e}")
                
        return stats
        
    def print_stats(self, stats):
        """Print traffic statistics in a readable format"""
        print("\n=== Traffic Statistics ===")
        for host, host_stats in stats.items():
            print(f"\nHost: {host}")
            if 'global' in host_stats:
                global_stats = host_stats['global']
                print(f"  Total Tx: {global_stats['tx_bps']/1e6:.2f} Mbps, {global_stats['tx_pps']} pps")
                print(f"  Total Rx: {global_stats['rx_bps']/1e6:.2f} Mbps, {global_stats['rx_pps']} pps")
                
            if 'port-0' in host_stats:
                port_stats = host_stats['port-0']
                print(f"  Port 0 Tx: {port_stats['tx_bps']/1e6:.2f} Mbps, {port_stats['tx_pps']} pps")
                print(f"  Port 0 Rx: {port_stats['rx_bps']/1e6:.2f} Mbps, {port_stats['rx_pps']} pps")

def main():
    parser = argparse.ArgumentParser(description='Control TRex traffic')
    parser.add_argument('topology', help='Topology name')
    parser.add_argument('action', choices=['start', 'stop', 'stats'],
                       help='Action to perform')
    parser.add_argument('--type', choices=['imix', 'srv6-imix', 'bulk', 'srv6-bulk'],
                       help='Traffic type (required for start action)')
    parser.add_argument('--src', nargs='+', help='Source hosts (default: all)')
    parser.add_argument('--dst', nargs='+', help='Destination hosts (default: all)')
    parser.add_argument('--config-dir', default='../config',
                       help='Configuration directory')
    parser.add_argument('--interval', type=int, default=5,
                       help='Statistics update interval in seconds')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.action == 'start' and not args.type:
        parser.error("--type is required for start action")
        
    # Create traffic controller
    try:
        controller = TrafficController(args.topology, args.config_dir)
        
        # Connect to hosts
        controller.connect_to_hosts(args.src)
        
        if not controller.clients:
            print("No hosts connected. Exiting.")
            return
            
        # Perform requested action
        if args.action == 'start':
            controller.start_traffic(args.type, args.src, args.dst)
            
            print("\nTraffic is running. Press Ctrl+C to stop...")
            try:
                while True:
                    time.sleep(args.interval)
                    stats = controller.get_stats()
                    controller.print_stats(stats)
            except KeyboardInterrupt:
                print("\nStopping traffic...")
                controller.stop_traffic()
                
        elif args.action == 'stop':
            controller.stop_traffic(args.src)
            
        elif args.action == 'stats':
            try:
                while True:
                    stats = controller.get_stats(args.src)
                    controller.print_stats(stats)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nExiting stats view")
                
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if 'controller' in locals():
            controller.disconnect_all()

if __name__ == "__main__":
    main() 