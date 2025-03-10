#!/usr/bin/env python3
import yaml
import os

def generate_radix8_yaml(output_file='../config/topologies/radix-8.yaml'):
    """Generate the complete radix-8.yaml file with 57 hosts"""
    
    # Create the base structure
    config = {
        'topology': {
            'name': 'radix-8',
            'description': 'Polarfly topology with 57 XRd routers',
            'reference_path': '../../../radix-8/'
        },
        'hosts': {},
        'traffic_patterns': {
            'imix': {
                'description': 'IMIX traffic pattern',
                'packet_sizes': [128, 570, 1518],
                'weights': [7, 4, 1],
                'pps_base': 100
            },
            'bulk': {
                'description': 'Bulk traffic for AI training simulation',
                'packet_size': 1250,
                'pps': 1000
            }
        },
        'srv6_defaults': {
            'encap_format': 'fc00:0:{usid1_hex}:{usid2_hex}:{usid3_hex}:{usid4_hex}:{usid5_hex}:{usid6_hex}::'
        }
    }
    
    # Generate host configurations
    for i in range(57):
        host_name = f'host{i:02d}'
        router_name = f'node{i:02d}'
        
        # Calculate IPv4 and IPv6 addresses
        # Each host gets two interfaces with consecutive IPs
        ipv4_base = 0 + (i * 2)  # Start from 10.10.0.x and increment by 2 for each host
        ipv6_base = i * 2  # Start from fc00:0:f800:0:: and increment by 2 for each host
        
        host_config = {
            'router': router_name,
            'ip': f'198.18.4.{200 + i}',
            'interfaces': [
                {
                    'name': 'eth1',
                    'ipv4': f'10.10.{ipv4_base}.2',
                    'ipv4_gw': f'10.10.{ipv4_base}.1',
                    'ipv6': f'fc00:0:f800:{ipv6_base}::2',
                    'ipv6_gw': f'fc00:0:f800:{ipv6_base}::1',
                    'ipv6_subnet': f'fc00:0:f800:{ipv6_base}::/64'
                },
                {
                    'name': 'eth2',
                    'ipv4': f'10.10.{ipv4_base + 1}.2',
                    'ipv4_gw': f'10.10.{ipv4_base + 1}.1',
                    'ipv6': f'fc00:0:f800:{ipv6_base + 1}::2',
                    'ipv6_gw': f'fc00:0:f800:{ipv6_base + 1}::1',
                    'ipv6_subnet': f'fc00:0:f800:{ipv6_base + 1}::/64'
                }
            ]
        }
        
        config['hosts'][host_name] = host_config
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the configuration to the YAML file
    with open(output_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Generated {output_file} with configurations for 57 hosts")

if __name__ == "__main__":
    generate_radix8_yaml() 