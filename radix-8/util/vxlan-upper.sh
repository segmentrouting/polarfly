#! /bin/bash

sudo clab tools vxlan delete -p clab

# node29
clab tools vxlan create --remote 198.18.1.100 --id 1022 --link node29-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1026 --link node29-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1046 --link node29-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1090 --link node29-Gi0-0-0-3

# node30
clab tools vxlan create --remote 198.18.1.100 --id 1037 --link node30-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1055 --link node30-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1063 --link node30-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1101 --link node30-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.100 --id 1206 --link node30-Gi0-0-0-4

# node31
clab tools vxlan create --remote 198.18.1.100 --id 1029 --link node31-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1032 --link node31-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1091 --link node31-Gi0-0-0-2

# node32
clab tools vxlan create --remote 198.18.1.100 --id 1095 --link node32-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1111 --link node32-Gi0-0-0-1

# node33
clab tools vxlan create --remote 198.18.1.100 --id 1000 --link node33-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1030 --link node33-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1072 --link node33-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1107 --link node33-Gi0-0-0-3

# node34
clab tools vxlan create --remote 198.18.1.100 --id 1007 --link node34-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1011 --link node34-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1027 --link node34-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1038 --link node34-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.100 --id 1082 --link node34-Gi0-0-0-4

# node35
clab tools vxlan create --remote 198.18.1.100 --id 1017 --link node35-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1028 --link node35-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1033 --link node35-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1064 --link node35-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.100 --id 1108 --link node35-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.100 --id 1112 --link node35-Gi0-0-0-5

# node36
clab tools vxlan create --remote 198.18.1.100 --id 1001 --link node36-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1018 --link node36-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1067 --link node36-Gi0-0-0-2

# node37
clab tools vxlan create --remote 198.18.1.100 --id 1008 --link node37-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1047 --link node37-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1073 --link node37-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1102 --link node37-Gi0-0-0-3

# node38
clab tools vxlan create --remote 198.18.1.100 --id 1019 --link node38-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1039 --link node38-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1051 --link node38-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1086 --link node38-Gi0-0-0-3

# node39
clab tools vxlan create --remote 198.18.1.100 --id 1002 --link node39-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1023 --link node39-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1040 --link node39-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1070 --link node39-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.100 --id 1113 --link node39-Gi0-0-0-4

# node40
clab tools vxlan create --remote 198.18.1.100 --id 1003 --link node40-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1048 --link node40-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1059 --link node40-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1087 --link node40-Gi0-0-0-3

# node41
clab tools vxlan create --remote 198.18.1.100 --id 1012 --link node41-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1071 --link node41-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1098 --link node41-Gi0-0-0-2

# node42
clab tools vxlan create --remote 198.18.1.100 --id 1034 --link node42-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1041 --link node42-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1074 --link node42-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1076 --link node42-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.100 --id 1096 --link node42-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.100 --id 1099 --link node42-Gi0-0-0-5

# node43
clab tools vxlan create --remote 198.18.1.100 --id 1035 --link node43-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1049 --link node43-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1083 --link node43-Gi0-0-0-2

# node44
clab tools vxlan create --remote 198.18.1.100 --id 1013 --link node44-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1088 --link node44-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.100 --id 1109 --link node44-Gi0-0-0-2  

# node45
clab tools vxlan create --remote 198.18.1.100 --id 1043 --link node45-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.100 --id 1056 --link node45-Gi0-0-0-1  
clab tools vxlan create --remote 198.18.1.100 --id 1060 --link node45-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.100 --id 1065 --link node45-Gi0-0-0-3

# node46
clab tools vxlan create --remote 198.18.1.100 --id 1014 --link node46-Gi0-0-0-0 # 2/4
clab tools vxlan create --remote 198.18.1.100 --id 1031 --link node46-Gi0-0-0-1 # 6/7
clab tools vxlan create --remote 198.18.1.100 --id 1050 --link node46-Gi0-0-0-2  # 10/7
clab tools vxlan create --remote 198.18.1.100 --id 1052 --link node46-Gi0-0-0-3  # 11/4
clab tools vxlan create --remote 198.18.1.100 --id 1057 --link node46-Gi0-0-0-4  # 12/6
clab tools vxlan create --remote 198.18.1.100 --id 1068 --link node46-Gi0-0-0-5  # 16/5
clab tools vxlan create --remote 198.18.1.100 --id 1077 --link node46-Gi0-0-0-6  # 19/3
clab tools vxlan create --remote 198.18.1.100 --id 1114 --link node46-Gi0-0-0-7  # 27/7

# node47
clab tools vxlan create --remote 198.18.1.100 --id 1078 --link node47-Gi0-0-0-0  # 19/4
clab tools vxlan create --remote 198.18.1.100 --id 1089 --link node47-Gi0-0-0-1  # 21/6

# node48
clab tools vxlan create --remote 198.18.1.100 --id 1004 --link node48-Gi0-0-0-0 # 0/5
clab tools vxlan create --remote 198.18.1.100 --id 1058 --link node48-Gi0-0-0-1 # 12/7
clab tools vxlan create --remote 198.18.1.100 --id 1084 --link node48-Gi0-0-0-2 # 20/6
clab tools vxlan create --remote 198.18.1.100 --id 1100 --link node48-Gi0-0-0-3 # 24/7

# node49
clab tools vxlan create --remote 198.18.1.100 --id 1005 --link node49-Gi0-0-0-0 # 0/6
clab tools vxlan create --remote 198.18.1.100 --id 1015 --link node49-Gi0-0-0-1 # 2/5
clab tools vxlan create --remote 198.18.1.100 --id 1066 --link node49-Gi0-0-0-2 # 15/6
clab tools vxlan create --remote 198.18.1.100 --id 1092 --link node49-Gi0-0-0-3 # 22/5
clab tools vxlan create --remote 198.18.1.100 --id 1097 --link node49-Gi0-0-0-4 # 23/7
clab tools vxlan create --remote 198.18.1.100 --id 1104 --link node49-Gi0-0-0-5 # 25/4

# node50
clab tools vxlan create --remote 198.18.1.100 --id 1042 --link node50-Gi0-0-0-0 # 8/7
clab tools vxlan create --remote 198.18.1.100 --id 1061 --link node50-Gi0-0-0-1 # 13/6
clab tools vxlan create --remote 198.18.1.100 --id 1069 --link node50-Gi0-0-0-2 # 16/7
clab tools vxlan create --remote 198.18.1.100 --id 1093 --link node50-Gi0-0-0-3 # 22/6

# node51
clab tools vxlan create --remote 198.18.1.100 --id 1053 --link node51-Gi0-0-0-0 # 11/5
clab tools vxlan create --remote 198.18.1.100 --id 1085 --link node51-Gi0-0-0-1 # 20/7
clab tools vxlan create --remote 198.18.1.100 --id 1105 --link node51-Gi0-0-0-2 # 25/5

# node52
clab tools vxlan create --remote 198.18.1.100 --id 1079 --link node52-Gi0-0-0-0  # 19/5
clab tools vxlan create --remote 198.18.1.100 --id 1094 --link node52-Gi0-0-0-1 # 22/7
clab tools vxlan create --remote 198.18.1.100 --id 1118 --link node52-Gi0-0-0-2 # 28/4

# node53
clab tools vxlan create --remote 198.18.1.100 --id 1009 --link node53-Gi0-0-0-0 # 1/6
clab tools vxlan create --remote 198.18.1.100 --id 1062 --link node53-Gi0-0-0-1 # 13/7
clab tools vxlan create --remote 198.18.1.100 --id 1080 --link node53-Gi0-0-0-2 # 19/6
clab tools vxlan create --remote 198.18.1.100 --id 1110 --link node53-Gi0-0-0-3 # 26/7

# node54
clab tools vxlan create --remote 198.18.1.100 --id 1020 --link node54-Gi0-0-0-0 # 3/6
clab tools vxlan create --remote 198.18.1.100 --id 1024 --link node54-Gi0-0-0-1  # 4/7
clab tools vxlan create --remote 198.18.1.100 --id 1044 --link node54-Gi0-0-0-2 # 9/6
clab tools vxlan create --remote 198.18.1.100 --id 1081 --link node54-Gi0-0-0-3 # 19/7
clab tools vxlan create --remote 198.18.1.100 --id 1106 --link node54-Gi0-0-0-4 # 25/6

# node55
clab tools vxlan create --remote 198.18.1.100 --id 1006 --link node55-Gi0-0-0-0 # 0/7 
clab tools vxlan create --remote 198.18.1.100 --id 1010 --link node55-Gi0-0-0-1 # 1/7
clab tools vxlan create --remote 198.18.1.100 --id 1036 --link node55-Gi0-0-0-2 # 7/7
clab tools vxlan create --remote 198.18.1.100 --id 1045 --link node55-Gi0-0-0-3 # 9/7
clab tools vxlan create --remote 198.18.1.100 --id 1054 --link node55-Gi0-0-0-4 # 11/6
clab tools vxlan create --remote 198.18.1.100 --id 1119 --link node55-Gi0-0-0-5 # 28/5

# node56
clab tools vxlan create --remote 198.18.1.100 --id 1016 --link node56-Gi0-0-0-0 # 2/6
clab tools vxlan create --remote 198.18.1.100 --id 1021 --link node56-Gi0-0-0-1 # 3/7
clab tools vxlan create --remote 198.18.1.100 --id 1075 --link node56-Gi0-0-0-2 # 18/7
clab tools vxlan create --remote 198.18.1.100 --id 1120 --link node56-Gi0-0-0-3 # 28/6


















