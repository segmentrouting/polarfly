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
clab tools vxlan create --remote 198.18.1.100 --id 1029 --link node31-eth1 #
clab tools vxlan create --remote 198.18.1.100 --id 1032 --link node31-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1091 --link node31-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1091 --link node31-eth6
clab tools vxlan create --remote 198.18.1.100 --id 1091 --link node31-eth7
clab tools vxlan create --remote 198.18.1.100 --id 1091 --link node31-eth8

# node32
clab tools vxlan create --remote 198.18.1.100 --id 1095 --link node32-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1111 --link node32-eth2

# node33
clab tools vxlan create --remote 198.18.1.100 --id 1000 --link node33-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1030 --link node33-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1072 --link node33-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1107 --link node33-eth4

# node34
clab tools vxlan create --remote 198.18.1.100 --id 1007 --link node34-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1011 --link node34-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1027 --link node34-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1038 --link node34-eth4
clab tools vxlan create --remote 198.18.1.100 --id 1082 --link node34-eth5

# node35
clab tools vxlan create --remote 198.18.1.100 --id 1017 --link node35-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1028 --link node35-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1033 --link node35-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1064 --link node35-eth4
clab tools vxlan create --remote 198.18.1.100 --id 1108 --link node35-eth5
clab tools vxlan create --remote 198.18.1.100 --id 1112 --link node35-eth6

# node36
clab tools vxlan create --remote 198.18.1.100 --id 1001 --link node36-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1018 --link node36-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1067 --link node36-eth3

# node37
clab tools vxlan create --remote 198.18.1.100 --id 1008 --link node37-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1047 --link node37-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1073 --link node37-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1102 --link node37-eth4

# node38
clab tools vxlan create --remote 198.18.1.100 --id 1019 --link node38-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1039 --link node38-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1051 --link node38-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1086 --link node38-eth4

# node39
clab tools vxlan create --remote 198.18.1.100 --id 1002 --link node39-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1023 --link node39-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1040 --link node39-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1070 --link node39-eth4
clab tools vxlan create --remote 198.18.1.100 --id 1113 --link node39-eth5

# node40
clab tools vxlan create --remote 198.18.1.100 --id 1003 --link node40-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1048 --link node40-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1059 --link node40-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1087 --link node40-eth4

# node41
clab tools vxlan create --remote 198.18.1.100 --id 1012 --link node41-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1071 --link node41-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1098 --link node41-eth3

# node42
clab tools vxlan create --remote 198.18.1.100 --id 1034 --link node42-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1041 --link node42-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1074 --link node42-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1076 --link node42-eth4
clab tools vxlan create --remote 198.18.1.100 --id 1096 --link node42-eth5
clab tools vxlan create --remote 198.18.1.100 --id 1099 --link node42-eth6

