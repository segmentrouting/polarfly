# polarfly

Project is setup to deploy a radix 8 Polarfly topology, which results in a 57 node Polarfly single tier network. The setup uses Containerlab as topology orchestrator and leverages the Containerlab VXLAN tool to connect nodes across host servers or VMs.

Requirements:

Two servers or large VMs with 32 vCPU and 96GB RAM each.
Docker andContainerlab

Instructions:

1. Clone the repository

2. Install Containerlab: https://containerlab.dev/install/

3. Acquire a Cisco XRd or other dockerized router image

4. Load docker image
```
docker load -i <image_name>
```

5. Modprobe
```
sudo modprobe br_netfilter
```
6. Add the following to /etc/sysctl.conf
```
kernel.pid_max=1048575
net.vrf.strict_mode=1
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1

fs.inotify.max_user_watches = 131072
fs.inotify.max_user_instances = 131072
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
kernel.pid_max = 1048575
```

7. Apply sysctl changes
```
sudo sysctl -p
```

8. Determine which server/VM will host the lower half of the topology (nodes00 - nodes28) and which will host the upper half (nodes29 - nodes57). 

9. cd into the xrd directory then:
    
    Deploy lower nodes:
```
sudo clab deploy -t polarfly-lower.yml
```

    Deploy upper nodes:
```
sudo clab deploy -t polarfly-upper.yml
```

10. Run vxlan interconnect scripts:

Lower nodes:
```
sudo ./vxlan-lower.sh
```

Upper nodes:
```
sudo ./vxlan-upper.sh
```

11. Give the routers 3-4 minutes to launch, then verify
12. ssh to routers. Example:
```
ssh cisco@clab-polarfly-radix8-node55
password: cisco123
```

