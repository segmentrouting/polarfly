#!/usr/bin/env python3
"""
TRex Server Manager for Polarfly Topology

This script manages TRex servers across multiple containers in the Polarfly topology.
It can start, stop, and check the status of TRex instances on specified hosts or all hosts.

Usage:
  python3 trex_server.py start --hosts 0 1 2 3  # Start TRex on specific hosts
  python3 trex_server.py stop --all              # Stop TRex on all hosts
  python3 trex_server.py status --all            # Check status of all TRex instances

Options:
  --hosts LIST     Specific host IDs to manage
  --all            Apply to all hosts (0-56)
  --parallel N     Number of parallel operations (default: 10)
  --log-dir DIR    Directory for logs (default: ./trex_logs)
  --trex-path PATH Path to TRex installation (default: /opt/trex/v3.04)
"""
import subprocess
import os
import time
import argparse
import concurrent.futures
import signal
import sys
import threading

# Maximum log file size in bytes (10MB)
MAX_LOG_SIZE = 10 * 1024 * 1024

def truncate_log(log_file, max_size=MAX_LOG_SIZE, keep_lines=1000):
    """Truncate log file if it exceeds the maximum size"""
    if os.path.exists(log_file) and os.path.getsize(log_file) > max_size:
        # Read the last 'keep_lines' lines
        with open(log_file, 'r') as f:
            lines = f.readlines()
            kept_lines = lines[-keep_lines:] if len(lines) > keep_lines else lines
        
        # Write only those lines back to the file
        with open(log_file, 'w') as f:
            f.writelines(kept_lines)

def log_monitor(log_dir, interval=60):
    """Monitor and truncate log files periodically"""
    while True:
        try:
            # Check all log files in the directory
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    log_file = os.path.join(log_dir, filename)
                    truncate_log(log_file)
        except Exception as e:
            print(f"Error in log monitor: {e}")
        
        # Sleep for the specified interval
        time.sleep(interval)

def start_trex(host_id, trex_path="/opt/trex/v3.04", log_dir="./trex_logs"):
    """Start TRex on a specific container"""
    container = f"clab-radix8-host{host_id:02d}"
    log_file = os.path.join(log_dir, f"{container}.log")
    
    # Use the --no-scapy-server flag to reduce some output
    cmd = f"docker exec -w {trex_path} {container} ./t-rex-64 -i --no-scapy-server"
    
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
    parser.add_argument('--monitor-logs', action='store_true',
                        help='Start log monitoring thread')
    
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

    # Start log monitor thread if requested
    if args.action == 'start' and args.monitor_logs:
        monitor_thread = threading.Thread(target=log_monitor, args=(args.log_dir,), daemon=True)
        monitor_thread.start()
        print(f"Started log monitor thread (checking every 60 seconds)")

if __name__ == "__main__":
    main()