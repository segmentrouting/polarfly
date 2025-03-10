#!/usr/bin/env python3
import subprocess
import os
import time
import argparse
import concurrent.futures

def start_trex(host_id, trex_path="/opt/trex/v3.04", log_dir="./trex_logs"):
    """Start TRex on a specific container"""
    container = f"clab-radix8-host{host_id:02d}"
    log_file = os.path.join(log_dir, f"{container}.log")
    
    cmd = f"docker exec -w {trex_path} {container} ./t-rex-64 -i"
    
    try:
        with open(log_file, 'w') as f:
            process = subprocess.Popen(cmd, shell=True, stdout=f, stderr=subprocess.STDOUT)
        
        # Wait a moment to check if process started successfully
        time.sleep(1)
        if process.poll() is not None:
            return (host_id, False, f"Process exited immediately with code {process.returncode}")
        
        return (host_id, True, "Started successfully")
    except Exception as e:
        return (host_id, False, str(e))

def main():
    parser = argparse.ArgumentParser(description='Start TRex on all containers')
    parser.add_argument('--hosts', type=int, nargs='+', help='Specific host IDs to start')
    parser.add_argument('--all', action='store_true', help='Start on all hosts (0-56)')
    parser.add_argument('--parallel', type=int, default=10, help='Number of parallel starts')
    parser.add_argument('--log-dir', default='./trex_logs', help='Directory for logs')
    
    args = parser.parse_args()
    
    # Create log directory
    os.makedirs(args.log_dir, exist_ok=True)
    
    # Determine which hosts to start
    if args.all:
        hosts = list(range(57))
    elif args.hosts:
        hosts = args.hosts
    else:
        parser.error("Either --all or --hosts must be specified")
    
    print(f"Starting TRex on {len(hosts)} containers with {args.parallel} parallel processes...")
    
    # Start TRex on all containers in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = [executor.submit(start_trex, host_id, log_dir=args.log_dir) for host_id in hosts]
        
        for future in concurrent.futures.as_completed(futures):
            host_id, success, message = future.result()
            status = "SUCCESS" if success else "FAILED"
            print(f"Host {host_id:02d}: {status} - {message}")
    
    print(f"Completed starting TRex. Logs are in {args.log_dir}/")

if __name__ == "__main__":
    main() 