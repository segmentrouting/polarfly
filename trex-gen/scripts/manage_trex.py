#!/usr/bin/env python3
import subprocess
import os
import time
import argparse
import concurrent.futures
import signal
import sys

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

def stop_trex(host_id):
    """Stop TRex on a specific container"""
    container = f"clab-radix8-host{host_id:02d}"
    
    # First try graceful shutdown
    cmd_graceful = f"docker exec {container} pkill -SIGINT -f t-rex-64"
    
    try:
        subprocess.run(cmd_graceful, shell=True, check=False)
        
        # Wait a moment to see if it stopped
        time.sleep(2)
        
        # Check if it's still running
        check_cmd = f"docker exec {container} pgrep -f t-rex-64"
        result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # If still running, force kill
        if result.returncode == 0:
            cmd_force = f"docker exec {container} pkill -SIGKILL -f t-rex-64"
            subprocess.run(cmd_force, shell=True, check=False)
            return (host_id, True, "Stopped with force")
        else:
            return (host_id, True, "Stopped gracefully")
            
    except Exception as e:
        return (host_id, False, str(e))

def check_trex_status(host_id):
    """Check if TRex is running on a specific container"""
    container = f"clab-radix8-host{host_id:02d}"
    
    cmd = f"docker exec {container} pgrep -f t-rex-64"
    
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return (host_id, True, "Running")
        else:
            return (host_id, False, "Not running")
    except Exception as e:
        return (host_id, False, f"Error checking status: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Manage TRex on containers')
    parser.add_argument('action', choices=['start', 'stop', 'status'], 
                        help='Action to perform')
    parser.add_argument('--hosts', type=int, nargs='+', help='Specific host IDs')
    parser.add_argument('--all', action='store_true', help='Apply to all hosts (0-56)')
    parser.add_argument('--parallel', type=int, default=10, 
                        help='Number of parallel operations')
    parser.add_argument('--log-dir', default='./trex_logs', 
                        help='Directory for logs (start only)')
    
    args = parser.parse_args()
    
    # Determine which hosts to manage
    if args.all:
        hosts = list(range(57))
    elif args.hosts:
        hosts = args.hosts
    else:
        parser.error("Either --all or --hosts must be specified")
    
    # Create log directory if starting
    if args.action == 'start':
        os.makedirs(args.log_dir, exist_ok=True)
    
    print(f"{args.action.capitalize()}ing TRex on {len(hosts)} containers with {args.parallel} parallel processes...")
    
    # Perform the requested action
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as executor:
        if args.action == 'start':
            futures = [executor.submit(start_trex, host_id, log_dir=args.log_dir) for host_id in hosts]
        elif args.action == 'stop':
            futures = [executor.submit(stop_trex, host_id) for host_id in hosts]
        else:  # status
            futures = [executor.submit(check_trex_status, host_id) for host_id in hosts]
        
        for future in concurrent.futures.as_completed(futures):
            host_id, success, message = future.result()
            if args.action == 'status':
                status = "RUNNING" if success else "STOPPED"
            else:
                status = "SUCCESS" if success else "FAILED"
            print(f"Host {host_id:02d}: {status} - {message}")
    
    if args.action == 'start':
        print(f"Completed {args.action}ing TRex. Logs are in {args.log_dir}/")
    else:
        print(f"Completed {args.action}ing TRex.")

if __name__ == "__main__":
    main()