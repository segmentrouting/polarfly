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

### Access Routers
   
1.  ssh to topology host VM:
    node00 - node28:
    ```
    ssh cisco@198.18.133.100
    ```
    node29 - node57:
    ```
    ssh cisco@198.18.133.129
    ```

user/pw for all nodes is cisco/cisco123

| topology-host1 | ssh to node00 - node28          |
|:---------------|:--------------------------------|
| node00         | cisco@clab-radix8-isis-node00   |
| node01         | cisco@clab-radix8-isis-node01   |
| node02         | cisco@clab-radix8-isis-node02   |
| node03         | cisco@clab-radix8-isis-node03   |
| node04         | cisco@clab-radix8-isis-node04   |
| node05         | cisco@clab-radix8-isis-node05   |
| node06         | cisco@clab-radix8-isis-node06   |
| node07         | cisco@clab-radix8-isis-node07   |
| node08         | cisco@clab-radix8-isis-node08   |
| node09         | cisco@clab-radix8-isis-node09   |
| node10         | cisco@clab-radix8-isis-node10   |
| node11         | cisco@clab-radix8-isis-node11   |
| node12         | cisco@clab-radix8-isis-node12   |
| node13         | cisco@clab-radix8-isis-node13   |
| node14         | cisco@clab-radix8-isis-node14   |
| node15         | cisco@clab-radix8-isis-node15   |
| node16         | cisco@clab-radix8-isis-node16   |
| node17         | cisco@clab-radix8-isis-node17   |
| node18         | cisco@clab-radix8-isis-node18   |
| node19         | cisco@clab-radix8-isis-node19   |
| node20         | cisco@clab-radix8-isis-node20   |
| node21         | cisco@clab-radix8-isis-node21   |
| node22         | cisco@clab-radix8-isis-node22   |
| node23         | cisco@clab-radix8-isis-node23   |
| node24         | cisco@clab-radix8-isis-node24   |
| node25         | cisco@clab-radix8-isis-node25   |
| node26         | cisco@clab-radix8-isis-node26   |
| node27         | cisco@clab-radix8-isis-node27   |
| node28         | cisco@clab-radix8-isis-node28   |

| topology-host2 | ssh to node29 - node57          |
|:---------------|:--------------------------------|
| node29         | cisco@clab-radix8-isis-node29   |
| node30         | cisco@clab-radix8-isis-node30   |
| node31         | cisco@clab-radix8-isis-node31   |
| node32         | cisco@clab-radix8-isis-node32   |
| node33         | cisco@clab-radix8-isis-node33   |
| node34         | cisco@clab-radix8-isis-node34   |
| node35         | cisco@clab-radix8-isis-node35   |
| node36         | cisco@clab-radix8-isis-node36   |
| node37         | cisco@clab-radix8-isis-node37   |
| node38         | cisco@clab-radix8-isis-node38   |
| node39         | cisco@clab-radix8-isis-node39   |
| node40         | cisco@clab-radix8-isis-node40   |
| node41         | cisco@clab-radix8-isis-node41   |
| node42         | cisco@clab-radix8-isis-node42   |
| node43         | cisco@clab-radix8-isis-node43   |
| node44         | cisco@clab-radix8-isis-node44   |
| node45         | cisco@clab-radix8-isis-node45   |
| node46         | cisco@clab-radix8-isis-node46   |
| node47         | cisco@clab-radix8-isis-node47   |
| node48         | cisco@clab-radix8-isis-node48   |
| node49         | cisco@clab-radix8-isis-node49   |
| node50         | cisco@clab-radix8-isis-node50   |
| node51         | cisco@clab-radix8-isis-node51   |
| node52         | cisco@clab-radix8-isis-node52   |
| node53         | cisco@clab-radix8-isis-node53   |
| node54         | cisco@clab-radix8-isis-node54   |
| node55         | cisco@clab-radix8-isis-node55   |
| node56         | cisco@clab-radix8-isis-node56   |


