#!/usr/bin/env python3
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
        cmd = f"docker exec -it {container} {args.trex_path}/trex-console -s localhost"
        print(f"Connecting to TRex server in container {container}...")
        subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main() 