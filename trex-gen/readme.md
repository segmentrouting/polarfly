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

# on polarfly lower-tier
python3 manage_trex.py start --hosts 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 
python3 manage_trex.py stop --hosts 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28
python3 manage_trex.py status --hosts 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28

# on polarfly upper-tier
python3 manage_trex.py start --hosts 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56
python3 manage_trex.py stop --hosts 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56
python3 manage_trex.py status --hosts 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56
```

5. **TRex console**
```bash
# Connect to TRex server running on a specific host
docker exec -it clab-radix8-host00 /opt/trex/v3.04/trex-console -s localhost

# Or if connecting from outside the container to a specific IP
/path/to/trex/trex-console -s 198.18.4.200
```

6. **TRex CLI**
```bash
# Show port statistics
stats

# Show port status
portattr

# Start traffic on specific ports
start -f /path/to/profile.py -p 0

# Stop traffic
stop -a

# Show active traffic streams
streams

# Enable service mode on ports (for IPv6 ND)
service -p 0 1 --on

# Disable service mode
service -p 0 1 --off

# Exit the console
quit
```

