#!/usr/bin/env python3
"""
Traffic Script Generator for Polarfly Topology

This script generates TRex traffic scripts and configuration files for all hosts
in the Polarfly topology based on the topology YAML configuration.

Usage:
  python3 generate_traffic_gen_scripts.py radix-8      # Generate scripts for radix-8 topology

The script reads the topology configuration from ../config/topologies/[topology].yaml
and generates output files in ../output/[topology]/ organized by host.
"""
import os
import yaml
import jinja2
import argparse
from pathlib import Path

def load_config(config_file):
    """Load the configuration from a YAML file"""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def create_directory(directory):
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)

def render_template(template_file, context):
    """Render a Jinja2 template with the given context"""
    template_dir = os.path.dirname(template_file)
    template_name = os.path.basename(template_file)
    
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    
    return template.render(**context)

def generate_scripts(topology_name, config_dir='../config', output_dir='../output'):
    """Generate all scripts for a given topology"""
    # Load topology configuration
    config_file = os.path.join(config_dir, 'topologies', f'{topology_name}.yaml')
    config = load_config(config_file)
    
    # Load SRv6 paths if available
    srv6_file = os.path.join(config_dir, 'srv6_paths.yaml')
    if os.path.exists(srv6_file):
        srv6_paths = load_config(srv6_file)
    else:
        srv6_paths = {}
    
    # Create output directory for this topology
    topology_output_dir = os.path.join(output_dir, topology_name)
    create_directory(topology_output_dir)
    
    # Get template files
    template_dir = os.path.join(config_dir, 'templates')
    templates = {
        'imix': os.path.join(template_dir, 'imix.py.j2'),
        'srv6_imix': os.path.join(template_dir, 'srv6_imix.py.j2'),
        'bulk': os.path.join(template_dir, 'bulk.py.j2'),
        'srv6_bulk': os.path.join(template_dir, 'srv6_bulk.py.j2'),
        'trex_cfg': os.path.join(template_dir, 'trex_cfg.yaml.j2')
    }
    
    # Generate scripts for each host
    hosts = config['hosts']
    for host_name, host_config in hosts.items():
        host_dir = os.path.join(topology_output_dir, host_name)
        create_directory(host_dir)
        
        # Context for templates
        context = {
            'src_host': host_config,
            'dst_hosts': [h for n, h in hosts.items() if n != host_name],
            'traffic_pattern': config['traffic_patterns'],
            'srv6_paths': srv6_paths.get(host_name, {}),
            'srv6_defaults': config.get('srv6_defaults', {})
        }
        
        # Generate each script type
        for script_type, template_file in templates.items():
            if not os.path.exists(template_file):
                print(f"Warning: Template {template_file} not found, skipping")
                continue
                
            output_filename = script_type.replace('_', '-') + '.py' if script_type != 'trex_cfg' else 'trex_cfg.yaml'
            output_file = os.path.join(host_dir, output_filename)
            
            # Render template and write to file
            content = render_template(template_file, context)
            with open(output_file, 'w') as f:
                f.write(content)
                
            print(f"Generated {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate TRex traffic scripts')
    parser.add_argument('topology', help='Name of the topology to generate scripts for')
    parser.add_argument('--config-dir', default='../config', help='Configuration directory')
    parser.add_argument('--output-dir', default='../output', help='Output directory')
    
    args = parser.parse_args()
    
    generate_scripts(args.topology, args.config_dir, args.output_dir)
    print(f"Script generation complete for {args.topology}")

if __name__ == "__main__":
    main() 