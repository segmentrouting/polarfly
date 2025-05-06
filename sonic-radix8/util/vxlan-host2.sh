#!/bin/bash

# node15
clab tools vxlan create --remote 198.18.1.100 --id 1080 --link node15-eth1 # "node01:eth1"]
clab tools vxlan create --remote 198.18.1.100 --id 1220 --link node15-eth2 # "node03:eth1"]
clab tools vxlan create --remote 198.18.1.100 --id 1770 --link node15-eth3 # "node12:eth3"]
clab tools vxlan create --remote 198.18.1.103 --id 2000 --link node15-eth6 # "node35:eth4"]
clab tools vxlan create --remote 198.18.1.104 --id 2010 --link node15-eth7 # "node45:eth4"]
clab tools vxlan create --remote 198.18.1.104 --id 2020 --link node15-eth8 # "node49:eth3"]

# node16
clab tools vxlan create --remote 198.18.1.100 --id 1230 --link node16-eth1 # "node03:eth2"]
clab tools vxlan create --remote 198.18.1.100 --id 1430 --link node16-eth2 # "node06:eth2"]
clab tools vxlan create --remote 198.18.1.100 --id 1830 --link node16-eth3 # "node13:eth3"]
clab tools vxlan create --remote 198.18.1.103 --id 2030 --link node16-eth6 # "node36:eth3"]
clab tools vxlan create --remote 198.18.1.104 --id 2040 --link node16-eth7 # "node46:eth6"]
clab tools vxlan create --remote 198.18.1.104 --id 2050 --link node16-eth8 # "node50:eth3"]

# node17
clab tools vxlan create --remote 198.18.1.100 --id 1090 --link node17-eth1 # "node01:eth2"]
clab tools vxlan create --remote 198.18.1.100 --id 1300 --link node17-eth2 # "node04:eth3"]
clab tools vxlan create --remote 198.18.1.100 --id 1440 --link node17-eth3 # "node06:eth3"]
clab tools vxlan create --remote 198.18.1.103 --id 2070 --link node17-eth7 # "node39:eth4"]
clab tools vxlan create --remote 198.18.1.103 --id 2080 --link node17-eth8 # "node41:eth2"]

# node18
clab tools vxlan create --remote 198.18.1.100 --id 1240 --link node18-eth1 # "node03:eth3"]
clab tools vxlan create --remote 198.18.1.100 --id 1640 --link node18-eth2 # "node10:eth3"]
clab tools vxlan create --remote 198.18.1.100 --id 1890 --link node18-eth3 # "node14:eth2"]
clab tools vxlan create --remote 198.18.1.103 --id 2090 --link node18-eth5 # "node33:eth3"]
clab tools vxlan create --remote 198.18.1.103 --id 2100 --link node18-eth6 # "node37:eth3"]
clab tools vxlan create --remote 198.18.1.103 --id 2110 --link node18-eth7 # "node42:eth3"]
clab tools vxlan create --remote 198.18.1.104 --id 2120 --link node18-eth8 # "node56:eth3"]

# node19
clab tools vxlan create --remote 198.18.1.100 --id 1100 --link node19-eth1 # "node01:eth3"]
clab tools vxlan create --remote 198.18.1.103 --id 2130 --link node19-eth3 # "node42:eth4"]
clab tools vxlan create --remote 198.18.1.104 --id 2140 --link node19-eth4 # "node46:eth7"]
clab tools vxlan create --remote 198.18.1.104 --id 2150 --link node19-eth5 # "node47:eth1"]
clab tools vxlan create --remote 198.18.1.104 --id 2160 --link node19-eth6 # "node52:eth1"]
clab tools vxlan create --remote 198.18.1.104 --id 2170 --link node19-eth7 # "node53:eth3"]
clab tools vxlan create --remote 198.18.1.104 --id 2180 --link node19-eth8 # "node54:eth4"]

# node20
clab tools vxlan create --remote 198.18.1.100 --id 1110 --link node20-eth1 # "node01:eth4"]
clab tools vxlan create --remote 198.18.1.100 --id 1890 --link node20-eth2 # "node14:eth2"]
clab tools vxlan create --remote 198.18.1.103 --id 2190 --link node20-eth5 # "node34:eth5"]
clab tools vxlan create --remote 198.18.1.104 --id 2200 --link node20-eth6 # "node43:eth3"]
clab tools vxlan create --remote 198.18.1.104 --id 2210 --link node20-eth7 # "node48:eth3"]
clab tools vxlan create --remote 198.18.1.104 --id 2220 --link node20-eth8 # "node51:eth2"]

# node21
clab tools vxlan create --remote 198.18.1.100 --id 1450 --link node21-eth1 # "node06:eth4"]
clab tools vxlan create --remote 198.18.1.100 --id 1910 --link node21-eth2 # "node14:eth4"]
clab tools vxlan create --remote 198.18.1.103 --id 2230 --link node21-eth5 # "node38:eth4"]
clab tools vxlan create --remote 198.18.1.103 --id 2240 --link node21-eth6 # "node40:eth4"]
clab tools vxlan create --remote 198.18.1.104 --id 2250 --link node21-eth7 # "node44:eth2"]
clab tools vxlan create --remote 198.18.1.105 --id 2260 --link node21-eth8 # "node47:eth2"]

# node22
clab tools vxlan create --remote 198.18.1.101 --id 1090 --link node22-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1091 --link node22-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1092 --link node22-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1093 --link node22-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1094 --link node22-eth8

# node23
clab tools vxlan create --remote 198.18.1.101 --id 1095 --link node23-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1096 --link node23-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1097 --link node23-eth8

# node24
clab tools vxlan create --remote 198.18.1.101 --id 1098 --link node24-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1099 --link node24-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1100 --link node24-eth8

# node25
clab tools vxlan create --remote 198.18.1.101 --id 1101 --link node25-eth3
clab tools vxlan create --remote 198.18.1.101 --id 1102 --link node25-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1104 --link node25-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1105 --link node25-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1106 --link node25-eth7

# node26
clab tools vxlan create --remote 198.18.1.101 --id 1206 --link node26-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1107 --link node26-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1108 --link node26-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1109 --link node26-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1110 --link node26-eth8

# node27
clab tools vxlan create --remote 198.18.1.101 --id 1111 --link node27-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1112 --link node27-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1113 --link node27-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1114 --link node27-eth8

# node28
clab tools vxlan create --remote 198.18.1.101 --id 1118 --link node28-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1119 --link node28-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1120 --link node28-eth7
