## Radix 8 XRd Polarfly Topology

### Table of Contents

- [Requirements](#requirements)
- [Instructions](#instructions)
- [Router ssh table](#router-ssh-table)


This project is setup to deploy a radix 8 XRd Polarfly topology, which results in a 57 node Polarfly single tier network. The setup uses Containerlab as topology orchestrator and leverages the Containerlab VXLAN tool to connect nodes across host servers or VMs.

### Requirements:

Two Linux servers or large VMs with 32 vCPU and 96GB RAM each. This project has been tested on Ubuntu 22.04.

Other requirements: Docker and Containerlab

### Instructions:

1. Clone this repository

2. Install Containerlab: https://containerlab.dev/install/

3. Acquire a Cisco XRd router image

4. Load docker image
```
docker load -i <image_name>
```

1. Modprobe
```
sudo modprobe br_netfilter
```

1. Add the following to /etc/sysctl.conf
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

9. On the lower half server/VM, cd into the xrd directory then:
    
Deploy lower nodes:
```
sudo clab deploy -t polarfly-lower.yml
```

10. On the upper half server/VM, cd into this directory then:

Deploy upper nodes:
```
sudo clab deploy -t polarfly-upper.yml
```

11. Give the routers 1-2 minutes to launch, then proceed to the next step

#### The current version of containerlab appears to have a bug where some nodes' netns connections are erroneously allocated. Perform the following steps on both upper and lower servers/VMs to fix the issue.

1. cd into the util directory and run the `*find-ints.sh*` script, which will give a list of error connections
```
cd util
sudo ./find-ints.sh
```

2.  Run the `*fix-ints.sh*` script, which will clean up the errors
```
sudo ./fix-ints.sh
```

3.  Run vxlan interconnect scripts:

Lower nodes:
```
sudo ./vxlan-lower.sh
```

Upper nodes:
```
sudo ./vxlan-upper.sh
```

The containerlab connections both within the servers/VMs and across the vxlan interconnects should now be up

### Verify nodes are up and BGP sessions are established
   
1.  ssh to routers. Example:
```
ssh cisco@clab-polarfly-radix8-node55
password: cisco123
```

2. BGP sessions should be established. Example:
```
show bgp ipv6 unicast summary
```

3. Shift OOB interface to mgt bridge:
```
sudo ip addr del 198.18.4.2/24 dev ens192
sudo ip addr add 198.18.4.2/24 dev br-501f4bbbf398
sudo brctl addif br-501f4bbbf398 ens192
```

### Router ssh table

user/pw for all nodes is cisco/cisco123

| Node name      | ip address                   |
|:---------------|:----------------------------|
| node00         | 198.18.4.100                |
| node01         | 198.18.4.101                |
| node02         | 198.18.4.102                |
| node03         | 198.18.4.103                |
| node04         | 198.18.4.104                |
| node05         | 198.18.4.105                |
| node06         | 198.18.4.106                |
| node07         | 198.18.4.107                |
| node08         | 198.18.4.108                |
| node09         | 198.18.4.109                |
| node10         | 198.18.4.110                |
| node11         | 198.18.4.111                |
| node12         | 198.18.4.112                |
| node13         | 198.18.4.113                |
| node14         | 198.18.4.114                |
| node15         | 198.18.4.115                |
| node16         | 198.18.4.116                |
| node17         | 198.18.4.117                |
| node18         | 198.18.4.118                |
| node19         | 198.18.4.119                |
| node20         | 198.18.4.120                |
| node21         | 198.18.4.121                |
| node22         | 198.18.4.122                |
| node23         | 198.18.4.123                |
| node24         | 198.18.4.124                |
| node25         | 198.18.4.125                |
| node26         | 198.18.4.126                |
| node27         | 198.18.4.127                |
| node28         | 198.18.4.128                |
| node29         | 198.18.4.129                |
| node30         | 198.18.4.130                |
| node31         | 198.18.4.131                |
| node32         | 198.18.4.132                |
| node33         | 198.18.4.133                |
| node34         | 198.18.4.134                |
| node35         | 198.18.4.135                |
| node36         | 198.18.4.136                |
| node37         | 198.18.4.137                |
| node38         | 198.18.4.138                |
| node39         | 198.18.4.139                |
| node40         | 198.18.4.140                |
| node41         | 198.18.4.141                |
| node42         | 198.18.4.142                |
| node43         | 198.18.4.143                |
| node44         | 198.18.4.144                |
| node45         | 198.18.4.145                |
| node46         | 198.18.4.146                |
| node47         | 198.18.4.147                |
| node48         | 198.18.4.148                |
| node49         | 198.18.4.149                |
| node50         | 198.18.4.150                |
| node51         | 198.18.4.151                |
| node52         | 198.18.4.152                |
| node53         | 198.18.4.153                |
| node54         | 198.18.4.154                |
| node55         | 198.18.4.155                |
| node56         | 198.18.4.156                |


You should now have a working topology that looks something like this:

![example](../graph-view/data/radix-8-polarfly.png)
