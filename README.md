# polarfly

This project is setup to model Polarfly topologies of various size and in some cases has containerlab topology definitions and config files to them. For example the radix 8 Polarfly topology results in a 57 node single tier network. In the case of larger topologies, the Containerlab VXLAN tool may be used to connect nodes across host servers or VMs.

## Use the edgelist.py tool to generate a basic Polarfly edge list

1. Run the topogen edge-list tool:
```
cd topogen
python3 edge-list.py generate brown 3
python3 edge-list.py generate brown 7
python3 edge-list.py generate brown 13
etc.
```

2. The tool will generate a Brown-<n>-adj.txt file in the util/data/Browns directory.

Example: [Brown-3-adj.txt](util/data/Browns/Brown-3-adj.txt)


## Use the graph-calc.py tool to generate a directory with vertex and edge data 

The graph-calc.py tool takes the adj.txt file, a radix number, and a q value as input and calculates vertex and edge data, which it populates into a directory with the radix number. It also calculates the node categorization (Quadric nodes, V1c, V1n, V2, etc.) and will output a json file with the node categorization.

```
cd topogen
python3 graph-calc.py -i data/Browns/Brown.3.adj.txt -r 4 -q 3 -n node
python3 graph-calc.py -i data/Browns/Brown.7.adj.txt -r 8 -q 7 -n node
python3 graph-calc.py -i data/Browns/Brown.13.adj.txt -r 16 -q 13 -n node
etc.
```

## ArangoDB import tool

The arango.py tool imports the vertex and edge data into an ArangoDB database and populates a graph using the radix number as the collection name.

```
cd topogen
python3 db/arangodb.py -p data/radix_4 --url http://198.18.133.102:30852 --dbname jalapeno --username root --password jalapeno

python3 db/arangodb.py -p data/radix_8 --url http://198.18.133.102:30852 --dbname jalapeno --username root --password jalapeno

python3 db/arangodb.py -p data/radix_16 --url http://198.18.133.102:30852 --dbname jalapeno --username root --password jalapeno
```

## Example deployment of 57-node Radix 8 Polarfly

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

13. srctl reference command:
```
srctl get-paths -s ebgp_prefix_v6/fc00:0:701:805::_64 -d ebgp_prefix_v6/fc00:0:701:9::_64 --type best-paths --limit 9
```