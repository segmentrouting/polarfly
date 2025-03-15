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
    imix_sizes = [128, 570, 1280]  # Default values (changed max size to 1280)
    imix_weights = [0.7, 0.2, 0.1]  # Default values
    pps_base = 100  # Default value
    
    if 'traffic_patterns' in config and 'imix' in config['traffic_patterns']:
        imix_config = config['traffic_patterns']['imix']
        if 'packet_sizes' in imix_config and len(imix_config['packet_sizes']) > 0:
            imix_sizes = imix_config['packet_sizes']
            # Ensure max packet size is 1280
            imix_sizes = [min(size, 1280) for size in imix_sizes]
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
    
    # Extract source prefix without /64
    src_prefix = src_subnet.split('/')[0]
    if src_prefix.endswith(':'):
        src_prefix = src_prefix[:-1]
    
    # Create source address
    src_addr = f"{src_prefix}::2"
    
    with open(script_path, 'w') as f:
        f.write(f"""from trex_stl_lib.api import *

class STLIPv6Imix(object):

    def __init__(self):
        # Source and destination IPv6 addresses
        self.src_addr = '{src_addr}'
        self.dst_subnets = {dst_subnets}
        
        # IMIX properties
        self.imix_table = [
            {{'size': {imix_sizes[0]}, 'pps': {int(pps_base * imix_weights[0])}, 'isg': 0}},
            {{'size': {imix_sizes[1]}, 'pps': {int(pps_base * imix_weights[1])}, 'isg': 0.1}},
            {{'size': {imix_sizes[2]}, 'pps': {int(pps_base * imix_weights[2])}, 'isg': 0.2}}
        ]

    def create_stream(self, dst_addr, size, pps, isg, stream_id):
        # Create base packet with IPv6
        base_pkt = Ether() / IPv6(src=self.src_addr, dst=dst_addr) / UDP(sport=1025, dport=1025)
        
        # Pad to desired size
        pad_size = max(0, size - len(base_pkt))
        if pad_size > 0:
            base_pkt = base_pkt / ('x' * pad_size)
        
        # Create stream
        return STLStream(
            isg=isg,
            packet=STLPktBuilder(pkt=base_pkt),
            mode=STLTXCont(pps=pps),
            flow_stats=STLFlowStats(pg_id=stream_id)
        )

    def get_streams(self, direction=0, **kwargs):
        streams = []
        stream_id = 0
        
        # Create streams for each destination subnet and IMIX size
        for dst_subnet in self.dst_subnets:
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            if dst_prefix.endswith(':'):
                dst_prefix = dst_prefix[:-1]
            
            # Create multiple destination addresses for this subnet
            dst_addrs = [f"{{dst_prefix}}::{{i}}" for i in range(2, 10)]
            
            for dst_addr in dst_addrs:
                for imix in self.imix_table:
                    stream = self.create_stream(
                        dst_addr,
                        imix['size'],
                        imix['pps'],
                        imix['isg'],
                        stream_id
                    )
                    streams.append(stream)
                    stream_id += 1
        
        return streams

def register():
    return STLIPv6Imix()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLIPv6Imix()
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
    print(f"\nGenerating bulk script for {host}")
    
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
            packet_size = min(bulk_config['packet_size'], 1280)  # Limit to 1280
        if 'pps' in bulk_config:
            pps = bulk_config['pps']
    
    # Create output directory for host
    host_dir = os.path.join(output_dir, host)
    os.makedirs(host_dir, exist_ok=True)
    
    # Generate bulk script
    script_path = os.path.join(host_dir, 'bulk.py')
    
    # If no source subnet, use a default
    if not src_subnet:
        print(f"Warning: No subnet found for {host}, using default")
        src_subnet = "fc00:0:f800:0::/64"
    
    # Extract source prefix without /64
    src_prefix = src_subnet.split('/')[0]
    if src_prefix.endswith(':'):
        src_prefix = src_prefix[:-1]
    
    # Create source address
    src_addr = f"{src_prefix}::2"
    
    with open(script_path, 'w') as f:
        f.write(f"""from trex_stl_lib.api import *

class STLIPv6Bulk(object):

    def __init__(self):
        # Source and destination IPv6 addresses
        self.src_addr = '{src_addr}'
        self.dst_subnets = {dst_subnets}
        
        # Packet size and rate
        self.packet_size = {packet_size}
        self.pps = {pps}

    def create_stream(self, dst_addr, stream_id):
        # Create base packet with IPv6
        base_pkt = Ether() / IPv6(src=self.src_addr, dst=dst_addr) / UDP(sport=1025, dport=1025)
        
        # Pad to desired size
        pad_size = max(0, self.packet_size - len(base_pkt))
        if pad_size > 0:
            base_pkt = base_pkt / ('x' * pad_size)
        
        # Create stream
        return STLStream(
            packet=STLPktBuilder(pkt=base_pkt),
            mode=STLTXCont(pps=self.pps),
            flow_stats=STLFlowStats(pg_id=stream_id)
        )

    def get_streams(self, direction=0, **kwargs):
        streams = []
        stream_id = 0
        
        # Create streams for each destination subnet
        for dst_subnet in self.dst_subnets:
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            if dst_prefix.endswith(':'):
                dst_prefix = dst_prefix[:-1]
            
            # Create multiple destination addresses for this subnet
            dst_addrs = [f"{{dst_prefix}}::{{i}}" for i in range(2, 10)]
            
            for dst_addr in dst_addrs:
                stream = self.create_stream(dst_addr, stream_id)
                streams.append(stream)
                stream_id += 1
        
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
    print(f"\nGenerating SRv6 IMIX script for {host}")
    
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
    srv6_encap_format = 'fc00:0:fe00:fe00:fe04:fe04::'
    if 'srv6_defaults' in config and 'encap_format' in config['srv6_defaults']:
        srv6_encap_format = config['srv6_defaults']['encap_format']
    
    # Get IMIX configuration if available
    imix_sizes = [128, 570, 1280]  # Default values (changed max size to 1280)
    imix_weights = [0.7, 0.2, 0.1]  # Default values
    pps_base = 100  # Default value
    
    if 'traffic_patterns' in config and 'imix' in config['traffic_patterns']:
        imix_config = config['traffic_patterns']['imix']
        if 'packet_sizes' in imix_config and len(imix_config['packet_sizes']) > 0:
            imix_sizes = imix_config['packet_sizes']
            # Ensure max packet size is 1280
            imix_sizes = [min(size, 1280) for size in imix_sizes]
        if 'weights' in imix_config and len(imix_config['weights']) > 0:
            # Convert to normalized weights
            total = sum(imix_config['weights'])
            imix_weights = [w/total for w in imix_config['weights']]
        if 'pps_base' in imix_config:
            pps_base = imix_config['pps_base']
    
    # Create output directory for host
    host_dir = os.path.join(output_dir, host)
    os.makedirs(host_dir, exist_ok=True)
    
    # Extract source prefix without /64
    src_prefix = src_subnet.split('/')[0]
    if src_prefix.endswith(':'):
        src_prefix = src_prefix[:-1]
    
    # Create source address
    src_addr = f"{src_prefix}::2"
    
    # Generate SRv6 IMIX script
    script_path = os.path.join(host_dir, 'srv6_imix.py')
    with open(script_path, 'w') as f:
        f.write(f"""from trex_stl_lib.api import *

class STLSRv6IMIX(object):

    def __init__(self):
        # Source and destination IPv6 addresses
        self.src_addr = '{src_addr}'
        self.dst_subnets = {dst_subnets}
        
        # SRv6 segment routing address
        self.srv6_sid = '{srv6_encap_format}'
        
        # IMIX properties
        self.imix_table = [
            {{'size': {imix_sizes[0]}, 'pps': {int(pps_base * imix_weights[0])}, 'isg': 0}},
            {{'size': {imix_sizes[1]}, 'pps': {int(pps_base * imix_weights[1])}, 'isg': 0.1}},
            {{'size': {imix_sizes[2]}, 'pps': {int(pps_base * imix_weights[2])}, 'isg': 0.2}}
        ]

    def create_stream(self, dst_addr, size, pps, isg, stream_id):
        # Create base packet with SRv6
        base_pkt = (Ether() / 
                   IPv6(src=self.src_addr, dst=self.srv6_sid) /
                   IPv6(src=self.src_addr, dst=dst_addr) /
                   UDP(sport=1025, dport=1025))
        
        # Pad to desired size
        pad_size = max(0, size - len(base_pkt))
        if pad_size > 0:
            base_pkt = base_pkt / ('x' * pad_size)
        
        # Create stream
        return STLStream(
            isg=isg,
            packet=STLPktBuilder(pkt=base_pkt),
            mode=STLTXCont(pps=pps),
            flow_stats=STLFlowStats(pg_id=stream_id)
        )

    def get_streams(self, direction=0, **kwargs):
        streams = []
        stream_id = 0
        
        # Create streams for each destination subnet and IMIX size
        for dst_subnet in self.dst_subnets:
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            if dst_prefix.endswith(':'):
                dst_prefix = dst_prefix[:-1]
            
            # Create multiple destination addresses for this subnet
            dst_addrs = [f"{{dst_prefix}}::{{i}}" for i in range(2, 6)]
            
            for dst_addr in dst_addrs:
                for imix in self.imix_table:
                    stream = self.create_stream(
                        dst_addr,
                        imix['size'],
                        imix['pps'],
                        imix['isg'],
                        stream_id
                    )
                    streams.append(stream)
                    stream_id += 1
        
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
    
    print(f"Generated SRv6 IMIX script for {host}")
    return script_path

def generate_srv6_bulk_script(host, config, output_dir):
    """Generate SRv6 bulk traffic script for a host"""
    host_config = config['hosts'][host]
    print(f"\nGenerating SRv6 bulk script for {host}")
    
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
    srv6_encap_format = 'fc00:0:fe00:fe00:fe04:fe04::'
    if 'srv6_defaults' in config and 'encap_format' in config['srv6_defaults']:
        srv6_encap_format = config['srv6_defaults']['encap_format']
    
    # Get bulk configuration if available
    packet_size = 1250  # Default value
    pps = 1000  # Default value
    
    if 'traffic_patterns' in config and 'bulk' in config['traffic_patterns']:
        bulk_config = config['traffic_patterns']['bulk']
        if 'packet_size' in bulk_config:
            packet_size = min(bulk_config['packet_size'], 1280)  # Limit to 1280
        if 'pps' in bulk_config:
            pps = bulk_config['pps']
    
    # Create output directory for host
    host_dir = os.path.join(output_dir, host)
    os.makedirs(host_dir, exist_ok=True)
    
    # Extract source prefix without /64
    src_prefix = src_subnet.split('/')[0]
    if src_prefix.endswith(':'):
        src_prefix = src_prefix[:-1]
    
    # Create source address
    src_addr = f"{src_prefix}::2"
    
    # Generate SRv6 bulk script
    script_path = os.path.join(host_dir, 'srv6_bulk.py')
    with open(script_path, 'w') as f:
        f.write(f"""from trex_stl_lib.api import *

class STLSRv6Bulk(object):

    def __init__(self):
        # Source and destination IPv6 addresses
        self.src_addr = '{src_addr}'
        self.dst_subnets = {dst_subnets}
        
        # SRv6 segment routing address
        self.srv6_sid = '{srv6_encap_format}'
        
        # Packet size and rate
        self.packet_size = {packet_size}
        self.pps = {pps}

    def create_stream(self, dst_addr, stream_id):
        # Create base packet with SRv6
        base_pkt = (Ether() / 
                   IPv6(src=self.src_addr, dst=self.srv6_sid) /
                   IPv6(src=self.src_addr, dst=dst_addr) /
                   UDP(sport=1025, dport=1025))
        
        # Pad to desired size
        pad_size = max(0, self.packet_size - len(base_pkt))
        if pad_size > 0:
            base_pkt = base_pkt / ('x' * pad_size)
        
        # Create stream
        return STLStream(
            packet=STLPktBuilder(pkt=base_pkt),
            mode=STLTXCont(pps=self.pps),
            flow_stats=STLFlowStats(pg_id=stream_id)
        )

    def get_streams(self, direction=0, **kwargs):
        streams = []
        stream_id = 0
        
        # Create streams for each destination subnet
        for dst_subnet in self.dst_subnets:
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            if dst_prefix.endswith(':'):
                dst_prefix = dst_prefix[:-1]
            
            # Create multiple destination addresses for this subnet
            dst_addrs = [f"{{dst_prefix}}::{{i}}" for i in range(2, 10)]
            
            for dst_addr in dst_addrs:
                stream = self.create_stream(dst_addr, stream_id)
                streams.append(stream)
                stream_id += 1
        
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
    
    print(f"Generated SRv6 bulk script for {host}")
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