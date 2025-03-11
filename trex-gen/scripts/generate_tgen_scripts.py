#!/usr/bin/env python3
"""
Traffic Script Generator for Polarfly Topology

This script generates TRex traffic scripts and configuration files for all hosts
in the Polarfly topology based on the topology YAML configuration.

Usage:
  python3 generate_tgen_scripts.py radix-8      # Generate scripts for radix-8 topology

The script reads the topology configuration from ../config/topologies/[topology].yaml
and generates output files in ../output/[topology]/ organized by host.
"""
import os
import sys
import yaml
import argparse
import ipaddress
import pprint

def load_topology_config(topology, config_dir='../config'):
    """Load configuration for a topology"""
    config_file = os.path.join(config_dir, 'topologies', f'{topology}.yaml')
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            print(f"Loaded configuration from {config_file}")
            print(f"Configuration has {len(config['hosts'])} hosts")
            return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def get_host_ipv6_subnet(host_config):
    """Extract the first IPv6 subnet from a host's interfaces"""
    if 'interfaces' not in host_config:
        return None
    
    for interface in host_config['interfaces']:
        if 'ipv6_subnet' in interface:
            return interface['ipv6_subnet']
    
    return None

def get_host_ipv4_subnet(host_config):
    """Extract the first IPv4 subnet from a host's interfaces"""
    if 'interfaces' not in host_config:
        return None
    
    for interface in host_config['interfaces']:
        if 'ipv4' in interface and 'ipv4_gw' in interface:
            # Construct subnet from IP (assuming /24)
            ip_parts = interface['ipv4'].split('.')
            return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
    
    return None

def generate_imix_script(host, config, output_dir):
    """Generate IMIX traffic script for a host"""
    host_config = config['hosts'][host]
    print(f"\nGenerating IMIX script for {host}")
    
    # Get source subnet from host
    src_subnet = get_host_ipv6_subnet(host_config)
    print(f"Source subnet: {src_subnet}")
    
    # Get destination subnets (all other hosts)
    dst_subnets = []
    dst_hosts = []
    
    for other_host, other_config in config['hosts'].items():
        if other_host == host:
            continue
        
        other_subnet = get_host_ipv6_subnet(other_config)
        if other_subnet:
            dst_subnets.append(other_subnet)
            dst_hosts.append(other_host)
    
    # Limit to 8 destination subnets for simplicity
    if len(dst_subnets) > 8:
        dst_subnets = dst_subnets[:8]
        dst_hosts = dst_hosts[:8]
    
    print(f"Selected destination hosts: {dst_hosts}")
    print(f"Selected destination subnets: {dst_subnets}")
    
    # Get IMIX configuration if available
    imix_sizes = [64, 570, 1518]  # Default values
    imix_weights = [0.7, 0.2, 0.1]  # Default values
    pps_base = 100  # Default value
    
    if 'traffic_patterns' in config and 'imix' in config['traffic_patterns']:
        imix_config = config['traffic_patterns']['imix']
        if 'packet_sizes' in imix_config and len(imix_config['packet_sizes']) > 0:
            imix_sizes = imix_config['packet_sizes']
        if 'weights' in imix_config and len(imix_config['weights']) > 0:
            # Convert to normalized weights
            total = sum(imix_config['weights'])
            imix_weights = [w/total for w in imix_config['weights']]
        if 'pps_base' in imix_config:
            pps_base = imix_config['pps_base']
    
    # Create output directory for host
    host_dir = os.path.join(output_dir, host)
    os.makedirs(host_dir, exist_ok=True)
    
    # Generate IMIX script
    script_path = os.path.join(host_dir, 'imix.py')
    
    # If no source subnet, use a default
    if not src_subnet:
        print(f"Warning: No subnet found for {host}, using default")
        src_subnet = "fc00:0:f800:0::/64"
    
    with open(script_path, 'w') as f:
        f.write(f"""from trex_stl_lib.api import *
import random

class STLIPv6(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = {dst_subnets}
        
        # Source subnet
        src_subnet = '{src_subnet}'
        
        # IMIX packet sizes and weights
        imix_sizes = {imix_sizes}
        imix_weights = {imix_weights}
        
        # Base packets per second
        pps_base = {pps_base}
        
        # Create streams list
        streams = []
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Create streams for each packet size in IMIX
            for size_id, (size, weight) in enumerate(zip(imix_sizes, imix_weights)):
                # Calculate packets per second for this stream
                pps = int(pps_base * weight)
                
                # Create IPv6 header with VM
                vm = STLVM()
                
                # Add source IPv6 address variation
                vm.var(name="src", min_value=src_prefix + "::2", 
                       max_value=src_prefix + "::ffff", size=16, op="random")
                vm.write(fv_name="src", pkt_offset="IPv6.src")
                
                # Add destination IPv6 address variation
                vm.var(name="dst", min_value=dst_prefix + "::2", 
                       max_value=dst_prefix + "::ffff", size=16, op="random")
                vm.write(fv_name="dst", pkt_offset="IPv6.dst")
                
                # Create base packet
                base_pkt = Ether() / IPv6(src=src_prefix + "::1", dst=dst_prefix + "::1") / UDP()
                
                # Pad to desired size
                pad_size = max(0, size - len(base_pkt))
                if pad_size > 0:
                    base_pkt = base_pkt / ('x' * pad_size)
                
                # Create stream with VM
                vm_stream = STLStream(
                    packet=STLPktBuilder(pkt=base_pkt, vm=vm),
                    mode=STLTXCont(pps=pps),
                    flow_stats=STLFlowStats(pg_id=subnet_id * 10 + size_id)
                )
                
                streams.append(vm_stream)

        return streams

def register():
    return STLIPv6()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLIPv6()
        streams = profile.get_streams()
        
        # Add all streams to port 0
        client.add_streams(streams, ports=[0])
        print(f"Added {{len(streams)}} streams to port 0")
        
        # Start traffic on port 0
        client.start(ports=[0])
        
        print("Traffic started on port 0")
        print("Press Enter to stop...")
        input()
        
        # Stop traffic
        client.stop()
        
    except STLError as e:
        print(e)
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    main() 
""")
    
    print(f"Generated IMIX script for {host} at {script_path}")
    return script_path

def generate_bulk_script(host, config, output_dir):
    """Generate bulk traffic script for a host"""
    host_config = config['hosts'][host]
    
    # Get source subnet from host
    src_subnet = get_host_ipv6_subnet(host_config)
    
    # Get destination subnets (all other hosts)
    dst_subnets = []
    
    for other_host, other_config in config['hosts'].items():
        if other_host == host:
            continue
        
        other_subnet = get_host_ipv6_subnet(other_config)
        if other_subnet:
            dst_subnets.append(other_subnet)
    
    # Limit to 8 destination subnets for simplicity
    if len(dst_subnets) > 8:
        dst_subnets = dst_subnets[:8]
    
    # Get bulk configuration if available
    packet_size = 1250  # Default value
    pps = 1000  # Default value
    
    if 'traffic_patterns' in config and 'bulk' in config['traffic_patterns']:
        bulk_config = config['traffic_patterns']['bulk']
        if 'packet_size' in bulk_config:
            packet_size = bulk_config['packet_size']
        if 'pps' in bulk_config:
            pps = bulk_config['pps']
    
    # Create output directory for host
    host_dir = os.path.join(output_dir, host)
    os.makedirs(host_dir, exist_ok=True)
    
    # Generate bulk script
    script_path = os.path.join(host_dir, 'bulk.py')
    
    # If no source subnet, use a default
    if not src_subnet:
        src_subnet = "fc00:0:f800:0::/64"
    
    with open(script_path, 'w') as f:
        f.write(f"""from trex_stl_lib.api import *
import random

class STLIPv6Bulk(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = {dst_subnets}
        
        # Source subnet
        src_subnet = '{src_subnet}'
        
        # Packet size (in bytes)
        packet_size = {packet_size}
        
        # Packets per second
        pps = {pps}
        
        # Create streams list
        streams = []
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Create IPv6 header with VM
            vm = STLVM()
            
            # Add source IPv6 address variation
            vm.var(name="src", min_value=src_prefix + "::2", 
                   max_value=src_prefix + "::ffff", size=16, op="random")
            vm.write(fv_name="src", pkt_offset="IPv6.src")
            
            # Add destination IPv6 address variation
            vm.var(name="dst", min_value=dst_prefix + "::2", 
                   max_value=dst_prefix + "::ffff", size=16, op="random")
            vm.write(fv_name="dst", pkt_offset="IPv6.dst")
            
            # Create base packet
            base_pkt = Ether() / IPv6(src=src_prefix + "::1", dst=dst_prefix + "::1") / UDP()
            
            # Pad to desired size
            pad_size = max(0, packet_size - len(base_pkt))
            if pad_size > 0:
                base_pkt = base_pkt / ('x' * pad_size)
            
            # Create stream with VM
            vm_stream = STLStream(
                packet=STLPktBuilder(pkt=base_pkt, vm=vm),
                mode=STLTXCont(pps=pps),
                flow_stats=STLFlowStats(pg_id=subnet_id)
            )
            
            streams.append(vm_stream)

        return streams

def register():
    return STLIPv6Bulk()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLIPv6Bulk()
        streams = profile.get_streams()
        
        # Add all streams to port 0
        client.add_streams(streams, ports=[0])
        print(f"Added {{len(streams)}} streams to port 0")
        
        # Start traffic on port 0
        client.start(ports=[0])
        
        print("Traffic started on port 0")
        print("Press Enter to stop...")
        input()
        
        # Stop traffic
        client.stop()
        
    except STLError as e:
        print(e)
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    main() 
""")
    
    print(f"Generated bulk script for {host}")
    return script_path

def generate_srv6_imix_script(host, config, output_dir):
    """Generate SRv6 IMIX traffic script for a host"""
    host_config = config['hosts'][host]
    
    # Get source subnet from host
    src_subnet = get_host_ipv6_subnet(host_config)
    if not src_subnet:
        print(f"Warning: No IPv6 subnet found for {host}, skipping SRv6 script")
        return None
    
    # Get destination subnets (all other hosts)
    dst_subnets = []
    dst_hosts = []
    
    for other_host, other_config in config['hosts'].items():
        if other_host == host:
            continue
        
        other_subnet = get_host_ipv6_subnet(other_config)
        if other_subnet:
            dst_subnets.append(other_subnet)
            dst_hosts.append(other_host)
    
    # Limit to 8 destination subnets for simplicity
    if len(dst_subnets) > 8:
        dst_subnets = dst_subnets[:8]
        dst_hosts = dst_hosts[:8]
    
    # Skip if no destination subnets
    if not dst_subnets:
        print(f"Warning: No IPv6 destination subnets found for {host}, skipping SRv6 script")
        return None
    
    # Get SRv6 configuration
    srv6_encap_format = 'fc00:0:{usid1_hex}:{usid2_hex}:{usid3_hex}:{usid4_hex}:{usid5_hex}:{usid6_hex}::'
    if 'srv6_defaults' in config and 'encap_format' in config['srv6_defaults']:
        srv6_encap_format = config['srv6_defaults']['encap_format']
    
    # Get IMIX configuration if available
    imix_sizes = [64, 570, 1518]  # Default values
    imix_weights = [0.7, 0.2, 0.1]  # Default values
    pps_base = 100  # Default value
    
    if 'traffic_patterns' in config and 'imix' in config['traffic_patterns']:
        imix_config = config['traffic_patterns']['imix']
        if 'packet_sizes' in imix_config and len(imix_config['packet_sizes']) > 0:
            imix_sizes = imix_config['packet_sizes']
        if 'weights' in imix_config and len(imix_config['weights']) > 0:
            # Convert to normalized weights
            total = sum(imix_config['weights'])
            imix_weights = [w/total for w in imix_config['weights']]
        if 'pps_base' in imix_config:
            pps_base = imix_config['pps_base']
    
    # Create output directory for host
    host_dir = os.path.join(output_dir, host)
    os.makedirs(host_dir, exist_ok=True)
    
    # Generate SRv6 IMIX script
    script_path = os.path.join(host_dir, 'srv6_imix.py')
    with open(script_path, 'w') as f:
        f.write(f"""from trex_stl_lib.api import *
import random

class STLSRv6IMIX(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = {dst_subnets}
        
        # Source subnet
        src_subnet = '{src_subnet}'
        
        # SRv6 encapsulation format
        srv6_encap_format = '{srv6_encap_format}'
        
        # IMIX packet sizes and weights
        imix_sizes = {imix_sizes}
        imix_weights = {imix_weights}
        
        # Base packets per second
        pps_base = {pps_base}
        
        # Create streams list
        streams = []
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Create SRv6 segment list (simplified for demo)
            # In a real scenario, this would be based on the topology
            usid1_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid2_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid3_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid4_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid5_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid6_hex = format(random.randint(1, 255), 'x').zfill(4)
            
            srv6_sid = srv6_encap_format.format(
                usid1_hex=usid1_hex,
                usid2_hex=usid2_hex,
                usid3_hex=usid3_hex,
                usid4_hex=usid4_hex,
                usid5_hex=usid5_hex,
                usid6_hex=usid6_hex
            )
            
            # Create streams for each packet size in IMIX
            for size_id, (size, weight) in enumerate(zip(imix_sizes, imix_weights)):
                # Calculate packets per second for this stream
                pps = int(pps_base * weight)
                
                # Create IPv6 header with VM
                vm = STLVM()
                
                # Add source IPv6 address variation
                vm.var(name="src", min_value=src_prefix + "::2", 
                       max_value=src_prefix + "::ffff", size=16, op="random")
                vm.write(fv_name="src", pkt_offset="IPv6.src")
                
                # Add destination IPv6 address variation
                vm.var(name="dst", min_value=dst_prefix + "::2", 
                       max_value=dst_prefix + "::ffff", size=16, op="random")
                vm.write(fv_name="dst", pkt_offset="IPv6.dst")
                
                # Create base packet with SRv6 header
                base_pkt = (Ether() / 
                           IPv6(src=src_prefix + "::1", dst=srv6_sid) / 
                           IPv6ExtHdrSegmentRouting(addresses=[srv6_sid, dst_prefix + "::1"]) /
                           IPv6(src=src_prefix + "::1", dst=dst_prefix + "::1") / 
                           UDP())
                
                # Pad to desired size
                pad_size = max(0, size - len(base_pkt))
                if pad_size > 0:
                    base_pkt = base_pkt / ('x' * pad_size)
                
                # Create stream with VM
                vm_stream = STLStream(
                    packet=STLPktBuilder(pkt=base_pkt, vm=vm),
                    mode=STLTXCont(pps=pps),
                    flow_stats=STLFlowStats(pg_id=subnet_id * 10 + size_id)
                )
                
                streams.append(vm_stream)

        return streams

def register():
    return STLSRv6IMIX()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLSRv6IMIX()
        streams = profile.get_streams()
        
        # Add all streams to port 0
        client.add_streams(streams, ports=[0])
        print(f"Added {{len(streams)}} streams to port 0")
        
        # Start traffic on port 0
        client.start(ports=[0])
        
        print("Traffic started on port 0")
        print("Press Enter to stop...")
        input()
        
        # Stop traffic
        client.stop()
        
    except STLError as e:
        print(e)
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    main() 
""")
    
    return script_path

def generate_srv6_bulk_script(host, config, output_dir):
    """Generate SRv6 bulk traffic script for a host"""
    host_config = config['hosts'][host]
    
    # Get source subnet from host
    src_subnet = get_host_ipv6_subnet(host_config)
    if not src_subnet:
        print(f"Warning: No IPv6 subnet found for {host}, skipping SRv6 script")
        return None
    
    # Get destination subnets (all other hosts)
    dst_subnets = []
    dst_hosts = []
    
    for other_host, other_config in config['hosts'].items():
        if other_host == host:
            continue
        
        other_subnet = get_host_ipv6_subnet(other_config)
        if other_subnet:
            dst_subnets.append(other_subnet)
            dst_hosts.append(other_host)
    
    # Limit to 8 destination subnets for simplicity
    if len(dst_subnets) > 8:
        dst_subnets = dst_subnets[:8]
        dst_hosts = dst_hosts[:8]
    
    # Skip if no destination subnets
    if not dst_subnets:
        print(f"Warning: No IPv6 destination subnets found for {host}, skipping SRv6 script")
        return None
    
    # Get SRv6 configuration
    srv6_encap_format = 'fc00:0:{usid1_hex}:{usid2_hex}:{usid3_hex}:{usid4_hex}:{usid5_hex}:{usid6_hex}::'
    if 'srv6_defaults' in config and 'encap_format' in config['srv6_defaults']:
        srv6_encap_format = config['srv6_defaults']['encap_format']
    
    # Get bulk configuration if available
    packet_size = 1250  # Default value
    pps = 1000  # Default value
    
    if 'traffic_patterns' in config and 'bulk' in config['traffic_patterns']:
        bulk_config = config['traffic_patterns']['bulk']
        if 'packet_size' in bulk_config:
            packet_size = bulk_config['packet_size']
        if 'pps' in bulk_config:
            pps = bulk_config['pps']
    
    # Create output directory for host
    host_dir = os.path.join(output_dir, host)
    os.makedirs(host_dir, exist_ok=True)
    
    # Generate SRv6 bulk script
    script_path = os.path.join(host_dir, 'srv6_bulk.py')
    with open(script_path, 'w') as f:
        f.write(f"""from trex_stl_lib.api import *
import random

class STLSRv6Bulk(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = {dst_subnets}
        
        # Source subnet
        src_subnet = '{src_subnet}'
        
        # SRv6 encapsulation format
        srv6_encap_format = '{srv6_encap_format}'
        
        # Packet size (in bytes)
        packet_size = {packet_size}
        
        # Packets per second
        pps = {pps}
        
        # Create streams list
        streams = []
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Create SRv6 segment list (simplified for demo)
            # In a real scenario, this would be based on the topology
            usid1_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid2_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid3_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid4_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid5_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid6_hex = format(random.randint(1, 255), 'x').zfill(4)
            
            srv6_sid = srv6_encap_format.format(
                usid1_hex=usid1_hex,
                usid2_hex=usid2_hex,
                usid3_hex=usid3_hex,
                usid4_hex=usid4_hex,
                usid5_hex=usid5_hex,
                usid6_hex=usid6_hex
            )
            
            # Create IPv6 header with VM
            vm = STLVM()
            
            # Add source IPv6 address variation
            vm.var(name="src", min_value=src_prefix + "::2", 
                   max_value=src_prefix + "::ffff", size=16, op="random")
            vm.write(fv_name="src", pkt_offset="IPv6.src")
            
            # Add destination IPv6 address variation
            vm.var(name="dst", min_value=dst_prefix + "::2", 
                   max_value=dst_prefix + "::ffff", size=16, op="random")
            vm.write(fv_name="dst", pkt_offset="IPv6.dst")
            
            # Create base packet with SRv6 header
            base_pkt = (Ether() / 
                       IPv6(src=src_prefix + "::1", dst=srv6_sid) / 
                       IPv6ExtHdrSegmentRouting(addresses=[srv6_sid, dst_prefix + "::1"]) /
                       IPv6(src=src_prefix + "::1", dst=dst_prefix + "::1") / 
                       UDP())
            
            # Pad to desired size
            pad_size = max(0, packet_size - len(base_pkt))
            if pad_size > 0:
                base_pkt = base_pkt / ('x' * pad_size)
            
            # Create stream with VM
            vm_stream = STLStream(
                packet=STLPktBuilder(pkt=base_pkt, vm=vm),
                mode=STLTXCont(pps=pps),
                flow_stats=STLFlowStats(pg_id=subnet_id)
            )
            
            streams.append(vm_stream)

        return streams

def register():
    return STLSRv6Bulk()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLSRv6Bulk()
        streams = profile.get_streams()
        
        # Add all streams to port 0
        client.add_streams(streams, ports=[0])
        print(f"Added {{len(streams)}} streams to port 0")
        
        # Start traffic on port 0
        client.start(ports=[0])
        
        print("Traffic started on port 0")
        print("Press Enter to stop...")
        input()
        
        # Stop traffic
        client.stop()
        
    except STLError as e:
        print(e)
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    main() 
""")
    
    return script_path

def main():
    parser = argparse.ArgumentParser(description='Generate TRex traffic scripts for Polarfly topology')
    parser.add_argument('topology', help='Topology name (e.g., radix-8)')
    parser.add_argument('--hosts', nargs='+', help='Specific hosts to generate scripts for')
    parser.add_argument('--config-dir', default='../config', help='Configuration directory')
    parser.add_argument('--output-dir', default='../output', help='Output directory')
    args = parser.parse_args()
    
    # Load topology configuration
    config = load_topology_config(args.topology, args.config_dir)
    if not config:
        print(f"Failed to load configuration for topology {args.topology}")
        return 1
    
    # Determine which hosts to generate scripts for
    hosts = args.hosts if args.hosts else config['hosts'].keys()
    
    # Create output directory
    output_dir = os.path.join(args.output_dir, args.topology)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate scripts for each host
    for host in hosts:
        if host not in config['hosts']:
            print(f"Warning: Unknown host {host}, skipping")
            continue
        
        # Generate traffic scripts
        generate_imix_script(host, config, output_dir)
        generate_bulk_script(host, config, output_dir)
        generate_srv6_imix_script(host, config, output_dir)
        generate_srv6_bulk_script(host, config, output_dir)
    
    print(f"Generated traffic scripts for {len(hosts)} hosts in {output_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 