#! /bin/bash

sudo clab tools vxlan delete -p clab

# node29
clab tools vxlan create --remote 198.18.1.100 --id 1330 --link node29-eth1 # "node04:eth6"]
clab tools vxlan create --remote 198.18.1.100 --id 1400 --link node29-eth2 # "node05:eth6"]
clab tools vxlan create --remote 198.18.1.100 --id 1650 --link node29-eth3 # "node10:eth4"]
clab tools vxlan create --remote 198.18.1.101 --id 2270 --link node29-eth4 # "node22:eth4"]
clab tools vxlan create --remote 198.18.1.104 --id 3000 --link node29-eth8 # "node47:eth3"]

# node30
clab tools vxlan create --remote 198.18.1.100 --id 1550 --link node30-eth1 # "node08:eth3"]
clab tools vxlan create --remote 198.18.1.100 --id 1790 --link node30-eth2 # "node12:eth5"]
clab tools vxlan create --remote 198.18.1.100 --id 1940 --link node30-eth3 # "node14:eth7"]
clab tools vxlan create --remote 198.18.1.101 --id 2380 --link node30-eth4 # "node25:eth3"]
clab tools vxlan create --remote 198.18.1.101 --id 2430 --link node30-eth5 # "node26:eth4"]
clab tools vxlan create --remote 198.18.1.104 --id 3010 --link node30-eth8 # "node53:eth5"]

# node31
clab tools vxlan create --remote 198.18.1.100 --id 1470 --link node31-eth1 # node06:eth6
clab tools vxlan create --remote 198.18.1.100 --id 1500 --link node31-eth2 # node07-eth4
clab tools vxlan create --remote 198.18.1.101 --id 2280 --link node31-eth3 # node22-eth5
clab tools vxlan create --remote 198.18.1.104 --id 3020 --link node31-eth6 # node48-eth5
clab tools vxlan create --remote 198.18.1.104 --id 3030 --link node31-eth7 # node53-eth6
clab tools vxlan create --remote 198.18.1.104 --id 3040 --link node31-eth8 # node56-eth5

# node32
clab tools vxlan create --remote 198.18.1.101 --id 2320 --link node32-eth1 # node23-eth6
clab tools vxlan create --remote 198.18.1.101 --id 2480 --link node32-eth2 # node27-eth5
clab tools vxlan create --remote 198.18.1.104 --id 3050 --link node32-eth7 # node45-eth5

# node33
clab tools vxlan create --remote 198.18.1.100 --id 1010 --link node33-eth1 # node00-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1480 --link node33-eth2 # node06-eth7
clab tools vxlan create --remote 198.18.1.101 --id 2090 --link node33-eth3 # node18-eth5
clab tools vxlan create --remote 198.18.1.101 --id 2440 --link node33-eth4 # node26-eth5
clab tools vxlan create --remote 198.18.1.104 --id 3060 --link node33-eth6 # node45-eth6
clab tools vxlan create --remote 198.18.1.104 --id 3070 --link node33-eth7 # node52-eth4

# node34
clab tools vxlan create --remote 198.18.1.100 --id 1120 --link node34-eth1 # node01-eth5
clab tools vxlan create --remote 198.18.1.100 --id 1160 --link node34-eth2 # node02-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1410 --link node34-eth3 # node05-eth7
clab tools vxlan create --remote 198.18.1.100 --id 1560 --link node34-eth4 # node08-eth4
clab tools vxlan create --remote 198.18.1.101 --id 2190 --link node34-eth5 # node20-eth5

# node35
clab tools vxlan create --remote 198.18.1.100 --id 1250 --link node35-eth1 # node03-eth4
clab tools vxlan create --remote 198.18.1.100 --id 1420 --link node35-eth2 # node05-eth8
clab tools vxlan create --remote 198.18.1.100 --id 1510 --link node35-eth3 # node07-eth5
clab tools vxlan create --remote 198.18.1.101 --id 2000 --link node35-eth4 # node15-eth6
clab tools vxlan create --remote 198.18.1.101 --id 2450 --link node35-eth5 # node26-eth6    
clab tools vxlan create --remote 198.18.1.101 --id 2490 --link node35-eth6 # node27-eth6

# node36
clab tools vxlan create --remote 198.18.1.100 --id 1020 --link node36-eth1 # node00-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1260 --link node36-eth2 # node03-eth5
clab tools vxlan create --remote 198.18.1.101 --id 2030 --link node36-eth3 # node16-eth6
clab tools vxlan create --remote 198.18.1.104 --id 3080 --link node36-eth7 # node47-eth4
clab tools vxlan create --remote 198.18.1.104 --id 3090 --link node36-eth8 # node55-eth7

# node37
clab tools vxlan create --remote 198.18.1.100 --id 1130 --link node37-eth1 # node01-eth6
clab tools vxlan create --remote 198.18.1.100 --id 1660 --link node37-eth2 # node10-eth5
clab tools vxlan create --remote 198.18.1.101 --id 2100 --link node37-eth3 # node18-eth6
clab tools vxlan create --remote 198.18.1.101 --id 2390 --link node37-eth4 # node25-eth4
clab tools vxlan create --remote 198.18.1.101 --id 3100 --link node37-eth6 # node44-eth5
clab tools vxlan create --remote 198.18.1.104 --id 3110 --link node37-eth7 # node50-eth5
clab tools vxlan create --remote 198.18.1.104 --id 3120 --link node37-eth8 # node55-eth8

# node38
clab tools vxlan create --remote 198.18.1.100 --id 1270 --link node38-eth1 # node03-eth6
clab tools vxlan create --remote 198.18.1.100 --id 1570 --link node38-eth2 # node08-eth5
clab tools vxlan create --remote 198.18.1.100 --id 1730 --link node38-eth3 # node11-eth4
clab tools vxlan create --remote 198.18.1.100 --id 2230 --link node38-eth4 # node21-eth5    
clab tools vxlan create --remote 198.18.1.104 --id 3130 --link node38-eth8 # node40-eth4

# node39
clab tools vxlan create --remote 198.18.1.100 --id 1030 --link node39-eth1 # node00-eth4
clab tools vxlan create --remote 198.18.1.100 --id 1340 --link node39-eth2 # node04-eth7
clab tools vxlan create --remote 198.18.1.100 --id 1580 --link node39-eth3 # node08-eth6
clab tools vxlan create --remote 198.18.1.101 --id 2070 --link node39-eth4 # node17-eth7
clab tools vxlan create --remote 198.18.1.101 --id 2500 --link node39-eth5 # node27-eth7
clab tools vxlan create --remote 198.18.1.104 --id 3140 --link node39-eth6 # node50-eth6
clab tools vxlan create --remote 198.18.1.104 --id 3150 --link node39-eth7 # node51-eth4
clab tools vxlan create --remote 198.18.1.104 --id 3160 --link node39-eth8 # node56-eth6

# node40
clab tools vxlan create --remote 198.18.1.100 --id 1040 --link node40-eth1 # node00-eth5
clab tools vxlan create --remote 198.18.1.100 --id 1670 --link node40-eth2 # node10-eth6
clab tools vxlan create --remote 198.18.1.100 --id 1850 --link node40-eth3 # node13-eth5
clab tools vxlan create --remote 198.18.1.101 --id 2240 --link node40-eth4 # node21-eth6
clab tools vxlan create --remote 198.18.1.104 --id 3170 --link node40-eth6 # node43-eth5
clab tools vxlan create --remote 198.18.1.104 --id 3180 --link node40-eth7 # node49-eth7
clab tools vxlan create --remote 198.18.1.104 --id 3190 --link node40-eth8 # node53-eth7

# node41
clab tools vxlan create --remote 198.18.1.100 --id 1170 --link node41-eth1 # node02-eth3
clab tools vxlan create --remote 198.18.1.101 --id 2080 --link node41-eth2 # node17-eth8
clab tools vxlan create --remote 198.18.1.101 --id 2350 --link node41-eth3 # node24-eth6
clab tools vxlan create --remote 198.18.1.104 --id 3200 --link node41-eth7 # node43-eth6
clab tools vxlan create --remote 198.18.1.104 --id 3210 --link node41-eth8 # node52-eth5

# node42
clab tools vxlan create --remote 198.18.1.100 --id 1520 --link node42-eth1 # node07-eth6
clab tools vxlan create --remote 198.18.1.100 --id 1590 --link node42-eth2 # node08-eth7
clab tools vxlan create --remote 198.18.1.101 --id 2110 --link node42-eth3 # node18-eth7
clab tools vxlan create --remote 198.18.1.101 --id 2130 --link node42-eth4 # node19-eth3
clab tools vxlan create --remote 198.18.1.101 --id 2330 --link node42-eth5 # node23-eth7    
clab tools vxlan create --remote 198.18.1.101 --id 2360 --link node42-eth6 # node24-eth7
clab tools vxlan create --remote 198.18.1.104 --id 3220 --link node42-eth7 # node47-eth5
clab tools vxlan create --remote 198.18.1.104 --id 3230 --link node42-eth8 # node49-eth8


