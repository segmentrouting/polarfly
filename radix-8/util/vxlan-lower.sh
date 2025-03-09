#! /bin/bash

sudo clab tools vxlan delete -p clab

# node00
clab tools vxlan create --remote 198.18.1.101 --id 1000 --link node00-Gi0-0-0-0 
clab tools vxlan create --remote 198.18.1.101 --id 1001 --link node00-Gi0-0-0-1     
clab tools vxlan create --remote 198.18.1.101 --id 1002 --link node00-Gi0-0-0-2 
clab tools vxlan create --remote 198.18.1.101 --id 1003 --link node00-Gi0-0-0-3 
clab tools vxlan create --remote 198.18.1.101 --id 1004 --link node00-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1005 --link node00-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1006 --link node00-Gi0-0-0-6  
clab tools vxlan create --remote 198.18.1.101 --id 1007 --link node00-Gi0-0-0-7

# node01
clab tools vxlan create --remote 198.18.1.101 --id 1008 --link node01-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1009 --link node01-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1010 --link node01-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1011 --link node01-Gi0-0-0-7

# node02
clab tools vxlan create --remote 198.18.1.101 --id 1012 --link node02-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1013 --link node02-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1014 --link node02-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1015 --link node02-Gi0-0-0-7

# node03
clab tools vxlan create --remote 198.18.1.101 --id 1016 --link node03-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1017 --link node03-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1018 --link node03-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1019 --link node03-Gi0-0-0-7

# node04
clab tools vxlan create --remote 198.18.1.101 --id 1020 --link node04-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1021 --link node04-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1022 --link node04-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1023 --link node04-Gi0-0-0-7

# node05
clab tools vxlan create --remote 198.18.1.101 --id 1024 --link node05-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1025 --link node05-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1026 --link node05-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1027 --link node05-Gi0-0-0-7

# node06
clab tools vxlan create --remote 198.18.1.101 --id 1028 --link node06-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1029 --link node06-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1030 --link node06-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1031 --link node06-Gi0-0-0-7

# node07
clab tools vxlan create --remote 198.18.1.101 --id 1032 --link node07-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.101 --id 1033 --link node07-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.101 --id 1034 --link node07-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.101 --id 1035 --link node07-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.101 --id 1036 --link node07-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1037 --link node07-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1038 --link node07-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1039 --link node07-Gi0-0-0-7

# node08
clab tools vxlan create --remote 198.18.1.101 --id 1040 --link node08-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1041 --link node08-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1042 --link node08-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1043 --link node08-Gi0-0-0-7

# node09
clab tools vxlan create --remote 198.18.1.101 --id 1044 --link node09-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1045 --link node09-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1046 --link node09-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1047 --link node09-Gi0-0-0-7

# node10
clab tools vxlan create --remote 198.18.1.101 --id 1048 --link node10-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1049 --link node10-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1050 --link node10-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1051 --link node10-Gi0-0-0-7

# node11
clab tools vxlan create --remote 198.18.1.101 --id 1052 --link node11-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1053 --link node11-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1054 --link node11-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1055 --link node11-Gi0-0-0-7

# node12
clab tools vxlan create --remote 198.18.1.101 --id 1056 --link node12-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1057 --link node12-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1058 --link node12-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1059 --link node12-Gi0-0-0-7

# node13
clab tools vxlan create --remote 198.18.1.101 --id 1060 --link node13-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1061 --link node13-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1062 --link node13-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1063 --link node13-Gi0-0-0-7

# node14
clab tools vxlan create --remote 198.18.1.101 --id 1064 --link node14-Gi0-0-0-7

# node15
clab tools vxlan create --remote 198.18.1.101 --id 1065 --link node15-Gi0-0-0-4 
clab tools vxlan create --remote 198.18.1.101 --id 1066 --link node15-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1067 --link node15-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1068 --link node15-Gi0-0-0-7

# node16
clab tools vxlan create --remote 198.18.1.101 --id 1069 --link node16-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1070 --link node16-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1071 --link node16-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1072 --link node16-Gi0-0-0-7

# node17
clab tools vxlan create --remote 198.18.1.101 --id 1073 --link node17-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.101 --id 1074 --link node17-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1075 --link node17-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1076 --link node17-Gi0-0-0-6

# node18
clab tools vxlan create --remote 198.18.1.101 --id 1077 --link node18-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.101 --id 1078 --link node18-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1079 --link node18-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1080 --link node18-Gi0-0-0-6

# node19
clab tools vxlan create --remote 198.18.1.101 --id 1081 --link node19-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1082 --link node19-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1083 --link node19-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1084 --link node19-Gi0-0-0-7

# node20
clab tools vxlan create --remote 198.18.1.101 --id 1085 --link node20-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1086 --link node20-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1087 --link node20-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1088 --link node20-Gi0-0-0-7

# node21
clab tools vxlan create --remote 198.18.1.101 --id 1089 --link node21-Gi0-0-0-7

# node22
clab tools vxlan create --remote 198.18.1.101 --id 1090 --link node22-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1091 --link node22-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1092 --link node22-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1093 --link node22-Gi0-0-0-7

# node23
clab tools vxlan create --remote 198.18.1.101 --id 1094 --link node23-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.101 --id 1095 --link node23-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1096 --link node23-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1097 --link node23-Gi0-0-0-6

# node24
clab tools vxlan create --remote 198.18.1.101 --id 1098 --link node24-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1099 --link node24-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1100 --link node24-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1101 --link node24-Gi0-0-0-7

# node25
clab tools vxlan create --remote 198.18.1.101 --id 1102 --link node25-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1103 --link node25-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1104 --link node25-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1105 --link node25-Gi0-0-0-7

# node26
clab tools vxlan create --remote 198.18.1.101 --id 1106 --link node26-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.101 --id 1107 --link node26-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1108 --link node26-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1109 --link node26-Gi0-0-0-6

# node27
clab tools vxlan create --remote 198.18.1.101 --id 1110 --link node27-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1111 --link node27-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1112 --link node27-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1113 --link node27-Gi0-0-0-7

# node28
clab tools vxlan create --remote 198.18.1.101 --id 1114 --link node28-Gi0-0-0-0
clab tools vxlan create --remote 198.18.1.101 --id 1115 --link node28-Gi0-0-0-1
clab tools vxlan create --remote 198.18.1.101 --id 1116 --link node28-Gi0-0-0-2
clab tools vxlan create --remote 198.18.1.101 --id 1117 --link node28-Gi0-0-0-3
clab tools vxlan create --remote 198.18.1.101 --id 1118 --link node28-Gi0-0-0-4
clab tools vxlan create --remote 198.18.1.101 --id 1119 --link node28-Gi0-0-0-5
clab tools vxlan create --remote 198.18.1.101 --id 1120 --link node28-Gi0-0-0-6
clab tools vxlan create --remote 198.18.1.101 --id 1121 --link node28-Gi0-0-0-7




























