#! /bin/bash

# node00
clab tools vxlan create --remote 198.18.1.105 --id 1000 --link node49-Gi0-0-0-0 
clab tools vxlan create --remote 198.18.1.105 --id 1001 --link node50-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1002 --link node51-Gi0-0-0-0 
clab tools vxlan create --remote 198.18.1.105 --id 1003 --link node52-Gi0-0-0-0 
clab tools vxlan create --remote 198.18.1.105 --id 1004 --link node53-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1005 --link node54-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1006 --link node55-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1007 --link node56-Gi0-0-0-0

# node01
clab tools vxlan create --remote 198.18.1.105 --id 1008 --link node34-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1009 --link node41-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1010 --link node48-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1011 --link node56-Gi0-0-0-1

# node02
clab tools vxlan create --remote 198.18.1.105 --id 1012 --link node31-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1013 --link node38-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1014 --link node45-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1015 --link node56-Gi0-0-0-2

# node03
clab tools vxlan create --remote 198.18.1.105 --id 1016 --link node30-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1017 --link node37-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1018 --link node44-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1019 --link node56-Gi0-0-0-3

# node04
clab tools vxlan create --remote 198.18.1.105 --id 1020 --link node33-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1021 --link node40-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1022 --link node47-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1023 --link node56-Gi0-0-0-4

# node05
clab tools vxlan create --remote 198.18.1.105 --id 1024 --link node32-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1025 --link node39-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1026 --link node46-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1027 --link node56-Gi0-0-0-5

# node06
clab tools vxlan create --remote 198.18.1.105 --id 1028 --link node29-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1029 --link node36-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1030 --link node43-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1031 --link node56-Gi0-0-0-6

# node07
clab tools vxlan create --remote 198.18.1.105 --id 1032 --link node42-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1033 --link node43-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1034 --link node44-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1035 --link node45-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1036 --link node46-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1037 --link node47-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1038 --link node48-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1039 --link node49-Gi0-0-0-1

# node08
clab tools vxlan create --remote 198.18.1.105 --id 1040 --link node30-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1041 --link node36-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1042 --link node42-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1043 --link node55-Gi0-0-0-1

# node09
clab tools vxlan create --remote 198.18.1.105 --id 1044 --link node29-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1045 --link node39-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1046 --link node42-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1047 --link node54-Gi0-0-0-2

# node10
clab tools vxlan create --remote 198.18.1.105 --id 1200 --link node31-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1201 --link node40-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1202 --link node42-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1203 --link node53-Gi0-0-0-1

# node11
clab tools vxlan create --remote 198.18.1.105 --id 1048 --link node32-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1049 --link node37-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1050 --link node42-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.105 --id 1051 --link node52-Gi0-0-0-1

# node12
clab tools vxlan create --remote 198.18.1.105 --id 1052 --link node34-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1053 --link node38-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1054 --link node42-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.105 --id 1055 --link node51-Gi0-0-0-1

# node13
clab tools vxlan create --remote 198.18.1.105 --id 1056 --link node33-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1057 --link node41-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.105 --id 1058 --link node42-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.105 --id 1059 --link node50-Gi0-0-0-1

# node14
clab tools vxlan create --remote 198.18.1.105 --id 1060 --link node49-Gi0-0-0-2

# node15
clab tools vxlan create --remote 198.18.1.105 --id 1061 --link node33-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1062 --link node38-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1063 --link node43-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1064 --link node52-Gi0-0-0-2

# node16
clab tools vxlan create --remote 198.18.1.105 --id 1065 --link node34-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1066 --link node40-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1067 --link node46-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1068 --link node55-Gi0-0-0-2

# node17
clab tools vxlan create --remote 198.18.1.105 --id 1069 --link node32-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1070 --link node36-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1071 --link node47-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1072 --link node51-Gi0-0-0-2

# node18
clab tools vxlan create --remote 198.18.1.105 --id 1073 --link node31-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1074 --link node41-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1075 --link node44-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1076 --link node54-Gi0-0-0-2

# node19
clab tools vxlan create --remote 198.18.1.105 --id 1077 --link node29-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1078 --link node37-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1079 --link node45-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1080 --link node50-Gi0-0-0-2

# node20
clab tools vxlan create --remote 198.18.1.105 --id 1081 --link node30-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1082 --link node39-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1083 --link node48-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.105 --id 1084 --link node53-Gi0-0-0-2

# node21
clab tools vxlan create --remote 198.18.1.105 --id 1085 --link node49-Gi0-0-0-3

# node22
clab tools vxlan create --remote 198.18.1.105 --id 1086 --link node29-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1087 --link node40-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1088 --link node44-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1089 --link node51-Gi0-0-0-3

# node23
clab tools vxlan create --remote 198.18.1.105 --id 1090 --link node32-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1091 --link node41-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1092 --link node43-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1093 --link node53-Gi0-0-0-3

# node24
clab tools vxlan create --remote 198.18.1.105 --id 1094 --link node33-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1095 --link node39-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1096 --link node45-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1097 --link node55-Gi0-0-0-3

# node25
clab tools vxlan create --remote 198.18.1.105 --id 1098 --link node30-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1099 --link node38-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1100 --link node46-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1101 --link node50-Gi0-0-0-3

# node26
clab tools vxlan create --remote 198.18.1.105 --id 1102 --link node31-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1103 --link node36-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1104 --link node48-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1105 --link node52-Gi0-0-0-3

# node27
clab tools vxlan create --remote 198.18.1.105 --id 1106 --link node34-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1107 --link node37-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1108 --link node47-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.105 --id 1109 --link node54-Gi0-0-0-3

# node28
clab tools vxlan create --remote 198.18.1.105 --id 1110 --link node35-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.105 --id 1111 --link node36-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.105 --id 1112 --link node37-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.105 --id 1113 --link node38-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.105 --id 1114 --link node39-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.105 --id 1115 --link node40-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.105 --id 1116 --link node41-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.105 --id 1117 --link node49-Gi0-0-0-4




























