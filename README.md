# polarfly

Note: topogen/edge-list.py and topogen/topos is borrowed from https://github.com/IntelLabs/PolarFly

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

2. The tool will generate a Brown-<n>-adj.txt file in the data/Browns directory.

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

Example:
```yaml
(venv)$ python3 graph-calc.py -i data/Browns/Brown.23.adj.txt -r 24 -q 23 -n node
Created directory: data/radix_24

Files generated in data/radix_24:
  - summary.json
  - vertices.json
  - edges.json

Graph statistics:
Number of nodes: 553
Number of edges: 6624
Node categories:
  W    (quadrics): 24
  V1c  (center nodes): 23
  V1n  (non-center V1): 253
  V2   (not adjacent to quadrics): 253
```

## ArangoDB import tool

The topogen/db/arangodb.py tool imports the vertex and edge data into an ArangoDB database and populates a graph using the radix number as the collection name.

```
cd topogen
python3 db/arangodb.py -p data/radix_4 --url http://198.18.133.102:30852 --dbname jalapeno --username root --password jalapeno

python3 db/arangodb.py -p data/radix_8 --url http://198.18.133.102:30852 --dbname jalapeno --username root --password jalapeno

python3 db/arangodb.py -p data/radix_16 --url http://198.18.133.102:30852 --dbname jalapeno --username root --password jalapeno
```

Example:
```yaml
(venv)$ python3 db/arangodb.py -p data/radix_8 --url http://198.18.133.102:30852 --dbname jalapeno --username root --password jalapeno
Creating collections with names:
  Vertex collection: radix_8_node
  Edge collection: radix_8_graph
Connected to ArangoDB at http://198.18.133.102:30852
Created/accessed collections: radix_8_node, radix_8_graph
Created/accessed graph: radix_8_graph
Imported 57 vertices
Imported 448 edges
Graph import completed successfully

(venv)$ python3 db/arangodb.py -p data/radix_16 --url http://198.18.133.102:30852 --dbname jalapeno --username root --password jalapeno
Creating collections with names:
  Vertex collection: radix_16_node
  Edge collection: radix_16_graph
Connected to ArangoDB at http://198.18.133.102:30852
Created/accessed collections: radix_16_node, radix_16_graph
Created/accessed graph: radix_16_graph
Imported 183 vertices
Imported 2548 edges
Graph import completed successfully
```

## Building a 57-node Radix 8 Polarfly Topology with Containerlab and XRd

The following instructions assume deployment of the 57 nodes across a pair of servers or large VMs. If you've got enough vCPU and memory you could deploy all 57 nodes on a single server or VM.

Requirements:

Two servers or large VMs with 32 vCPU and 96GB RAM each.
Docker andContainerlab

### Instructions:

Note: steps 1-8 should be performed on both servers or VMs.

1. Clone this repository

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

#### Lower half of the topology
1. ssh to the server/VM that will host the lower half of the topology and cd into the radix-8-xrd directory then:
    
Deploy lower nodes:
```
sudo clab deploy -t polarfly-lower.yml
```

2. Run vxlan interconnect script for lower nodes:
```
sudo util/vxlan-lower.sh
```

3. As of clab 1.60 there appears to be a bug where some netns interfaces get incorrectly wired. Run the 'fix-ints.sh' script to correct this.
```
sudo util/fix-ints.sh
```

#### Upper half of the topology
1. ssh to the server/VM that will host the upper half of the topology and cd into the radix-8-xrd directory then:

Deploy upper nodes:
```
sudo clab deploy -t polarfly-upper.yml
```

2. Run vxlan interconnect script for upper nodes:
```
sudo util/vxlan-upper.sh
```

3. Run the 'fix-ints.sh' script to correct any incorrectly wired netns interfaces.
```
sudo util/fix-ints.sh
```

#### Both lower and upper halves:
1. Give the routers 3-4 minutes to launch, then verify
2. ssh to routers. Example:
```
ssh cisco@clab-polarfly-radix8-node55
password: cisco123
```

### srctl command line tool

1. srctl reference command:
```
srctl get-paths -s ebgp_prefix_v6/fc00:0:701:805::_64 -d ebgp_prefix_v6/fc00:0:701:9::_64 --type best-paths --limit 9
```