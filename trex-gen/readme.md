### Directory Structure

trex-gen/
├── config/
│   ├── topologies/
│   │   ├── radix-8.yaml       # Configuration for radix-8 topology
│   │   └── other-topologies/  # Future topology configurations
│   ├── templates/
│   │   ├── imix.py.j2         # Jinja2 template for IMIX traffic
│   │   ├── srv6_imix.py.j2    # Jinja2 template for SRv6 IMIX traffic
│   │   ├── bulk.py.j2         # Jinja2 template for bulk traffic
│   │   ├── srv6_bulk.py.j2    # Jinja2 template for SRv6 bulk traffic
│   │   └── trex_cfg.yaml.j2   # Jinja2 template for TRex configuration
│   └── srv6_paths.yaml        # SRv6 path information
├── scripts/
│   ├── generate_scripts.py    # Script generator
│   ├── enable_ipv6_nd.py      # IPv6 ND enablement script
│   └── traffic_controller.py  # Main traffic control script
├── output/
│   └── radix-8/               # Generated scripts for radix-8 topology
│       ├── host00/
│       │   ├── imix.py
│       │   ├── srv6_imix.py
│       │   ├── bulk.py
│       │   ├── srv6_bulk.py
│       │   └── trex_cfg.yaml
│       ├── host01/
│       └── ...
└── README.md                  # Documentation

### Usage

1. **Generate Host Configurations**
```bash
cd trex-gen/scripts
python3 generate_topology_yaml.py
```

2. **Generate per host TRex files and scripts**
```bash
cd trex-gen/scripts
python3 generate_scripts.py radix-8
```

3. **Use containerlab to launch the topology**
```bash
cd ../radix-8/
sudo clab deploy -t isis-upper.yml
```

4. **Start TRex on hosts**
```bash
cd trex-gen/scripts
# Start TRex on all hosts
python3 manage_trex.py start --all

# Stop TRex on all hosts
python3 manage_trex.py stop --all

# Check status of all TRex instances
python3 manage_trex.py status --all

# Start/stop/check specific hosts
python3 manage_trex.py start --hosts 0 1 2 3
python3 manage_trex.py stop --hosts 0 1 2 3
python3 manage_trex.py status --hosts 0 1 2 3
```