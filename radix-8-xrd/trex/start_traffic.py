import sys
import argparse
import os

# adding trex location to the system path
sys.path.insert(0, '/home/cisco/trex/v3.06/trex_client/interactive/')
from trex_stl_lib.api import *

class TRexController:
    def __init__(self):
        # Define all TRex servers and their configurations
        self.servers = {}
        
        # Generate server configurations for host00 through host28
        for i in range(29):
            host_name = f'host{i:02d}'
            self.servers[host_name] = {
                'ip': f'198.18.4.{200 + i}',
                'ua_script': f'{host_name}/uA.py',
                'un_script': f'{host_name}/uN.py',
                'imix_script': f'{host_name}/imix.py'
            }
            
        self.clients = {}

    def connect_to_hosts(self, hostnames=None):
        """
        Connect to specified TRex servers or all if hostnames is None
        Args:
            hostnames: List of hostnames to connect to, or None for all
        """
        hosts_to_connect = hostnames if hostnames else self.servers.keys()
        
        for host in hosts_to_connect:
            if host not in self.servers:
                print(f"Warning: Unknown host {host}, skipping")
                continue
                
            config = self.servers[host]
            try:
                client = STLClient(server=config['ip'])
                client.connect()
                client.reset()
                self.clients[host] = client
                print(f"Connected to {host} at {config['ip']}")
            except STLError as e:
                print(f"Failed to connect to {host}: {e}")

    def start_traffic(self, modes, hostnames=None):
        """
        Start traffic on specified servers or all if hostnames is None
        Args:
            modes: list containing 'ua', 'un', and/or 'imix'
            hostnames: List of hostnames to start traffic on, or None for all
        """
        hosts_to_start = hostnames if hostnames else self.clients.keys()
        
        for host in hosts_to_start:
            if host not in self.clients:
                print(f"Warning: Not connected to {host}, skipping")
                continue
                
            client = self.clients[host]
            try:
                for mode in modes:
                    if mode == 'ua':
                        script_key = 'ua_script'
                    elif mode == 'un':
                        script_key = 'un_script'
                    elif mode == 'imix':
                        script_key = 'imix_script'
                    else:
                        continue
                        
                    script_path = self.servers[host][script_key]
                    
                    # Reset the port before adding streams
                    client.reset(ports=[0])
                    
                    # Try to use the direct API approach
                    try:
                        # Use start_line with explicit port specification
                        client.start_line(f" -f {script_path} --port 0")
                        print(f"Started {mode.upper()} traffic on {host} using {script_path} (port 0 only)")
                    except STLError as e:
                        print(f"Failed to start traffic with script {script_path}: {e}")
                        
            except STLError as e:
                print(f"Failed to start traffic on {host}: {e}")

    def stop_traffic(self, hostnames=None):
        """
        Stop traffic on specified servers or all if hostnames is None
        Args:
            hostnames: List of hostnames to stop traffic on, or None for all
        """
        hosts_to_stop = hostnames if hostnames else self.clients.keys()
        
        for host in hosts_to_stop:
            if host not in self.clients:
                continue
                
            client = self.clients[host]
            try:
                client.stop(ports=[0])  # Stop only port 0
                print(f"Stopped traffic on {host} (port 0)")
            except STLError as e:
                print(f"Failed to stop traffic on {host}: {e}")

    def disconnect_all(self, hostnames=None):
        """
        Disconnect from specified servers or all if hostnames is None
        Args:
            hostnames: List of hostnames to disconnect from, or None for all
        """
        hosts_to_disconnect = hostnames if hostnames else list(self.clients.keys())
        
        for host in hosts_to_disconnect:
            if host not in self.clients:
                continue
                
            client = self.clients[host]
            try:
                client.disconnect()
                print(f"Disconnected from {host}")
                del self.clients[host]
            except STLError as e:
                print(f"Failed to disconnect from {host}: {e}")

def main():
    # Add TRex client to Python path
    sys.path.insert(0, '/home/cisco/trex/v3.06/trex_client/interactive/')

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Start TRex traffic streams')
    parser.add_argument('mode', choices=['ua', 'un', 'imix', 'all'],
                       help='Traffic mode: ua (uA only), un (uN only), imix (IMIX only), or all (all types)')
    parser.add_argument('-hn', '--hostname', nargs='+',
                       help='Specific host(s) to run traffic on (e.g., host00 host01). If not specified, runs on all hosts.')
    args = parser.parse_args()

    # Determine which modes to run
    if args.mode == 'all':
        modes = ['ua', 'un', 'imix']
    else:
        modes = [args.mode]

    controller = TRexController()
    
    try:
        # Connect to specified hosts or all hosts
        controller.connect_to_hosts(args.hostname)
        
        if not controller.clients:
            print("No hosts connected. Exiting.")
            return
        
        # Start traffic with specified modes on specified hosts
        controller.start_traffic(modes, args.hostname)
        
        print("\nTraffic is running. Press Enter to stop...")
        input()
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    
    finally:
        # Clean up
        controller.stop_traffic(args.hostname)
        controller.disconnect_all(args.hostname)

if __name__ == "__main__":
    main() 