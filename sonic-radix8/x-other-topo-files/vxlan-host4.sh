#! /bin/bash

sudo clab tools vxlan delete -p clab

# node43
clab tools vxlan create --remote 198.18.1.100 --id 1035 --link node43-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1049 --link node43-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1083 --link node43-eth3

# node44
clab tools vxlan create --remote 198.18.1.100 --id 1013 --link node44-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1088 --link node44-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1109 --link node44-eth3  

# node45
clab tools vxlan create --remote 198.18.1.100 --id 1043 --link node45-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1056 --link node45-eth2  
clab tools vxlan create --remote 198.18.1.100 --id 1060 --link node45-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1065 --link node45-eth4

# node46
clab tools vxlan create --remote 198.18.1.100 --id 1014 --link node46-eth1 # 2/4
clab tools vxlan create --remote 198.18.1.100 --id 1031 --link node46-eth2 # 6/7
clab tools vxlan create --remote 198.18.1.100 --id 1050 --link node46-eth3  # 10/7
clab tools vxlan create --remote 198.18.1.100 --id 1052 --link node46-eth4  # 11/4
clab tools vxlan create --remote 198.18.1.100 --id 1057 --link node46-eth5  # 12/6
clab tools vxlan create --remote 198.18.1.100 --id 1068 --link node46-eth6  # 16/5
clab tools vxlan create --remote 198.18.1.100 --id 1077 --link node46-eth7  # 19/3
clab tools vxlan create --remote 198.18.1.100 --id 1114 --link node46-eth8  # 27/7

# node47
clab tools vxlan create --remote 198.18.1.100 --id 1078 --link node47-eth1  # 19/4
clab tools vxlan create --remote 198.18.1.100 --id 1089 --link node47-eth2  # 21/6

# node48
clab tools vxlan create --remote 198.18.1.100 --id 1004 --link node48-eth1 # 0/5
clab tools vxlan create --remote 198.18.1.100 --id 1058 --link node48-eth2 # 12/7
clab tools vxlan create --remote 198.18.1.100 --id 1084 --link node48-eth3 # 20/6
clab tools vxlan create --remote 198.18.1.100 --id 1100 --link node48-eth4 # 24/7

# node49
clab tools vxlan create --remote 198.18.1.100 --id 1005 --link node49-eth1 # 0/6
clab tools vxlan create --remote 198.18.1.100 --id 1015 --link node49-eth2 # 2/5
clab tools vxlan create --remote 198.18.1.100 --id 1066 --link node49-eth3 # 15/6
clab tools vxlan create --remote 198.18.1.100 --id 1092 --link node49-eth4 # 22/5
clab tools vxlan create --remote 198.18.1.100 --id 1097 --link node49-eth5 # 23/7
clab tools vxlan create --remote 198.18.1.100 --id 1104 --link node49-eth6 # 25/4

# node50
clab tools vxlan create --remote 198.18.1.100 --id 1042 --link node50-eth1 # 8/7
clab tools vxlan create --remote 198.18.1.100 --id 1061 --link node50-eth2 # 13/6
clab tools vxlan create --remote 198.18.1.100 --id 1069 --link node50-eth3 # 16/7
clab tools vxlan create --remote 198.18.1.100 --id 1093 --link node50-eth4 # 22/6

# node51
clab tools vxlan create --remote 198.18.1.100 --id 1053 --link node51-eth1 # 11/5
clab tools vxlan create --remote 198.18.1.100 --id 1085 --link node51-eth2 # 20/7
clab tools vxlan create --remote 198.18.1.100 --id 1105 --link node51-eth3 # 25/5

# node52
clab tools vxlan create --remote 198.18.1.100 --id 1079 --link node52-eth1  # 19/5
clab tools vxlan create --remote 198.18.1.100 --id 1094 --link node52-eth2 # 22/7
clab tools vxlan create --remote 198.18.1.100 --id 1118 --link node52-eth3 # 28/4

# node53
clab tools vxlan create --remote 198.18.1.100 --id 1009 --link node53-eth1 # 1/6
clab tools vxlan create --remote 198.18.1.100 --id 1062 --link node53-eth2 # 13/7
clab tools vxlan create --remote 198.18.1.100 --id 1080 --link node53-eth3 # 19/6
clab tools vxlan create --remote 198.18.1.100 --id 1110 --link node53-eth4 # 26/7

# node54
clab tools vxlan create --remote 198.18.1.100 --id 1020 --link node54-eth1 # 3/6
clab tools vxlan create --remote 198.18.1.100 --id 1024 --link node54-eth2  # 4/7
clab tools vxlan create --remote 198.18.1.100 --id 1044 --link node54-eth3 # 9/6
clab tools vxlan create --remote 198.18.1.100 --id 1081 --link node54-eth4 # 19/7
clab tools vxlan create --remote 198.18.1.100 --id 1106 --link node54-eth5 # 25/6

# node55
clab tools vxlan create --remote 198.18.1.100 --id 1006 --link node55-eth1 # 0/7 
clab tools vxlan create --remote 198.18.1.100 --id 1010 --link node55-eth2 # 1/7
clab tools vxlan create --remote 198.18.1.100 --id 1036 --link node55-eth3 # 7/7
clab tools vxlan create --remote 198.18.1.100 --id 1045 --link node55-eth4 # 9/7
clab tools vxlan create --remote 198.18.1.100 --id 1054 --link node55-eth5 # 11/6
clab tools vxlan create --remote 198.18.1.100 --id 1119 --link node55-eth6 # 28/5

# node56
clab tools vxlan create --remote 198.18.1.100 --id 1016 --link node56-eth1 # 2/6
clab tools vxlan create --remote 198.18.1.100 --id 1021 --link node56-eth2 # 3/7
clab tools vxlan create --remote 198.18.1.100 --id 1075 --link node56-eth3 # 18/7
clab tools vxlan create --remote 198.18.1.100 --id 1120 --link node56-eth4 # 28/6


















