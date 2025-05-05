#! /bin/bash

sudo clab tools vxlan delete -p clab

# node00
clab tools vxlan create --remote 198.18.1.101 --id 1000 --link node00-eth1
clab tools vxlan create --remote 198.18.1.103 --id 1000 --link node00-eth2 
clab tools vxlan create --remote 198.18.1.103 --id 1001 --link node00-eth3     
clab tools vxlan create --remote 198.18.1.103 --id 1002 --link node00-eth4 
clab tools vxlan create --remote 198.18.1.103 --id 1003 --link node00-eth5 
clab tools vxlan create --remote 198.18.1.104 --id 1004 --link node00-eth6
clab tools vxlan create --remote 198.18.1.104 --id 1005 --link node00-eth7
clab tools vxlan create --remote 198.18.1.104 --id 1006 --link node00-eth8  

# node01
clab tools vxlan create --remote 198.18.1.101 --id 1007 --link node01-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1008 --link node01-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1009 --link node01-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1010 --link node01-eth8

# node02
clab tools vxlan create --remote 198.18.1.101 --id 1011 --link node02-eth2
clab tools vxlan create --remote 198.18.1.101 --id 1012 --link node02-eth3
clab tools vxlan create --remote 198.18.1.101 --id 1013 --link node02-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1014 --link node02-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1015 --link node02-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1016 --link node02-eth7

# node03
clab tools vxlan create --remote 198.18.1.101 --id 1017 --link node03-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1018 --link node03-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1019 --link node03-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1020 --link node03-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1021 --link node03-eth8

# node04
clab tools vxlan create --remote 198.18.1.101 --id 1022 --link node04-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1023 --link node04-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1024 --link node04-eth8

# node05
clab tools vxlan create --remote 198.18.1.101 --id 1026 --link node05-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1027 --link node05-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1028 --link node05-eth8

# node06
clab tools vxlan create --remote 198.18.1.101 --id 1029 --link node06-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1030 --link node06-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1031 --link node06-eth8

# node07
clab tools vxlan create --remote 198.18.1.101 --id 1032 --link node07-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1033 --link node07-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1034 --link node07-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1035 --link node07-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1036 --link node07-eth8

# node08
clab tools vxlan create --remote 198.18.1.101 --id 1037 --link node08-eth3
clab tools vxlan create --remote 198.18.1.101 --id 1038 --link node08-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1039 --link node08-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1040 --link node08-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1041 --link node08-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1042 --link node08-eth8

# node09
clab tools vxlan create --remote 198.18.1.101 --id 1043 --link node09-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1044 --link node09-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1045 --link node09-eth8

# node10
clab tools vxlan create --remote 198.18.1.101 --id 1046 --link node10-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1047 --link node10-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1048 --link node10-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1049 --link node10-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1050 --link node10-eth8

# node11
clab tools vxlan create --remote 198.18.1.101 --id 1051 --link node11-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1052 --link node11-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1053 --link node11-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1054 --link node11-eth7

# node12
clab tools vxlan create --remote 198.18.1.101 --id 1055 --link node12-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1056 --link node12-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1057 --link node12-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1058 --link node12-eth8

# node13
clab tools vxlan create --remote 198.18.1.101 --id 1059 --link node13-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1060 --link node13-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1061 --link node13-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1062 --link node13-eth8

# node14
clab tools vxlan create --remote 198.18.1.101 --id 1063 --link node14-eth7

# node15
clab tools vxlan create --remote 198.18.1.101 --id 1064 --link node15-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1065 --link node15-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1066 --link node15-eth8

# node16
clab tools vxlan create --remote 198.18.1.101 --id 1067 --link node16-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1068 --link node16-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1069 --link node16-eth8

# node17
clab tools vxlan create --remote 198.18.1.101 --id 1070 --link node17-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1071 --link node17-eth8

# node18
clab tools vxlan create --remote 198.18.1.101 --id 1072 --link node18-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1073 --link node18-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1074 --link node18-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1075 --link node18-eth8

# node19
clab tools vxlan create --remote 198.18.1.101 --id 1076 --link node19-eth3
clab tools vxlan create --remote 198.18.1.101 --id 1077 --link node19-eth4
clab tools vxlan create --remote 198.18.1.101 --id 1078 --link node19-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1079 --link node19-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1080 --link node19-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1081 --link node19-eth8

# node20
clab tools vxlan create --remote 198.18.1.101 --id 1082 --link node20-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1083 --link node20-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1084 --link node20-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1085 --link node20-eth8

# node21
clab tools vxlan create --remote 198.18.1.101 --id 1086 --link node21-eth5
clab tools vxlan create --remote 198.18.1.101 --id 1087 --link node21-eth6
clab tools vxlan create --remote 198.18.1.101 --id 1088 --link node21-eth7
clab tools vxlan create --remote 198.18.1.101 --id 1089 --link node21-eth8

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




























