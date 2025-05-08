#! /bin/bash

sudo clab tools vxlan delete -p clab

# node29
clab tools vxlan create --remote 198.18.1.100 --id 1022 --link node29-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1026 --link node29-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1046 --link node29-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1090 --link node29-eth4

# node30
clab tools vxlan create --remote 198.18.1.100 --id 1037 --link node30-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1055 --link node30-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1063 --link node30-eth3
clab tools vxlan create --remote 198.18.1.100 --id 1101 --link node30-eth4
clab tools vxlan create --remote 198.18.1.100 --id 1206 --link node30-eth5

# node31
clab tools vxlan create --remote 198.18.1.100 --id 1029 --link node31-eth1
clab tools vxlan create --remote 198.18.1.100 --id 1032 --link node31-eth2
clab tools vxlan create --remote 198.18.1.100 --id 1091 --link node31-eth3

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


















