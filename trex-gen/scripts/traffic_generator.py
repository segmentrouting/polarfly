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
import re

# Add TRex client library to Python path
TREX_CLIENT_PATHS = [
    '/home/cisco/trex/v3.06/trex_client/interactive',
    '/opt/trex/v3.04/trex_client/interactive',
    '/opt/trex/v3.06/trex_client/interactive',
    '/opt/trex/current/trex_client/interactive',
    os.path.expanduser('~/trex/v3.04/trex_client/interactive'),
    os.path.expanduser('~/trex/v3.06/trex_client/interactive'),
    os.path.expanduser('~/trex/current/trex_client/interactive'),
]

for path in TREX_CLIENT_PATHS:
    if os.path.exists(path):
        sys.path.append(path)
        print(f"Using TRex client library from: {path}")
        break
else:
    print("ERROR: Could not find TRex client library. Please specify the correct path.")
    print("Edit this script and update TREX_CLIENT_PATHS at the top.")
    sys.exit(1)

# Now import TRex libraries
try:
    from trex_stl_lib.api import *
except ImportError:
    print("ERROR: Failed to import TRex STL API. Check your TRex installation.")
    sys.exit(1)

def load_topology_config(topology, config_dir='../config'):
    """Load configuration for a topology"""
    config_file = os.path.join(config_dir, 'topologies', f'{topology}.yaml')
    
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def fix_traffic_script(script_path):
    """Fix common issues in traffic scripts"""
    try:
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for empty imix_sizes and imix_weights
        if 'imix_sizes = ' in content and 'imix_weights = ' in content:
            # Add default IMIX values
            content = content.replace(
                'imix_sizes = ', 
                'imix_sizes = [64, 570, 1518]'
            )
            content = content.replace(
                'imix_weights = ', 
                'imix_weights = [0.7, 0.2, 0.1]'
            )
        
        # Fix the *weight syntax error
        content = re.sub(
            r'STLTXCont\(pps=\*weight\)', 
            r'STLTXCont(pps=1000*weight)', 
            content
        )
        
        # Write the fixed content back
        with open(script_path, 'w') as f:
            f.write(content)
            
        print(f"Fixed issues in {script_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing script {script_path}: {e}")
        return False

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
                
                # Check if the script exists
                output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output', self.topology)
                full_script_path = os.path.join(output_dir, script_path)
                
                if not os.path.exists(full_script_path):
                    print(f"Error: Script {full_script_path} does not exist")
                    continue
                    
                print(f"Using script: {full_script_path}")
                
                # Fix common issues in the script
                fix_traffic_script(full_script_path)
                
                # Try to start traffic
                try:
                    client.start_line(f" -f {script_path} --port 0")
                    print(f"Started {traffic_type} traffic on {host}")
                    
                    # Verify traffic is actually running
                    time.sleep(1)
                    stats = client.get_stats()
                    if 'global' in stats and stats['global']['tx_pps'] > 0:
                        print(f"Confirmed traffic is running on {host}: {stats['global']['tx_pps']} pps")
                    else:
                        print(f"Warning: Traffic may not be running on {host}. Stats: {stats}")
                        
                except STLError as e:
                    print(f"Failed to start traffic on {host} with error: {e}")
                    print("Trying alternative method...")
                    
                    # Try alternative method - load the script directly
                    try:
                        # Create a temporary directory for the script
                        import tempfile
                        temp_dir = tempfile.mkdtemp()
                        temp_script = os.path.join(temp_dir, "temp_script.py")
                        
                        # Copy the script content to the temporary file
                        with open(full_script_path, 'r') as src, open(temp_script, 'w') as dst:
                            dst.write(src.read())
                        
                        # Add the temporary directory to the Python path
                        sys.path.append(temp_dir)
                        
                        # Import the script
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("temp_script", temp_script)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Get the profile
                        if hasattr(module, 'register'):
                            profile = module.register()
                        else:
                            # Try to find a class that starts with STL
                            for attr_name in dir(module):
                                if attr_name.startswith('STL') and attr_name != 'STLClient':
                                    profile_class = getattr(module, attr_name)
                                    profile = profile_class()
                                    break
                            else:
                                raise ValueError("Could not find profile class in module")
                        
                        # Get streams and start traffic
                        streams = profile.get_streams()
                        client.add_streams(streams, ports=[0])
                        client.start(ports=[0])
                        print(f"Started {traffic_type} traffic on {host} using alternative method")
                        
                    except Exception as e2:
                        print(f"Alternative method also failed: {e2}")
                
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