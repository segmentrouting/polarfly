#!/usr/bin/env python3
"""
TRex Console Connector for Polarfly Topology

This script connects to the TRex console of a specified host in the Polarfly topology.
It can connect either from inside the container or from outside using the host's IP.

Usage:
  python3 trex_console.py 0                # Connect to host00 from inside the container
  python3 trex_console.py 0 --external     # Connect to host00 from outside using its IP

Options:
  --external       Connect from outside the container using IP
  --trex-path PATH Path to TRex installation (default: /opt/trex/v3.04)
"""
import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Connect to TRex console')
    parser.add_argument('host_id', type=int, help='Host ID to connect to')
    parser.add_argument('--external', action='store_true', 
                        help='Connect from outside the container using IP')
    parser.add_argument('--trex-path', default='/opt/trex/v3.04',
                        help='Path to TRex installation')
    
    args = parser.parse_args()
    
    host_id = args.host_id
    container = f"clab-radix8-host{host_id:02d}"
    
    if args.external:
        # Connect from outside using IP (assumes IP format from your config)
        ip = f"198.18.4.{200 + host_id}"
        cmd = f"{args.trex_path}/trex-console -s {ip}"
        print(f"Connecting to TRex server at {ip}...")
        subprocess.run(cmd, shell=True)
    else:
        # Connect from inside the container
        cmd = f"docker exec -itw {args.trex_path} {container} {args.trex_path}/trex-console -s localhost"
        print(f"Connecting to TRex server in container {container}...")
        subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main() 