#! /bin/bash

sudo clab tools vxlan delete -p clab

# node00
clab tools vxlan create --remote 198.18.1.101 --id 1000 --link node00-eth1 # node27:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1010 --link node00-eth2 # node33:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1020 --link node00-eth3 # node36:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1030 --link node00-eth4 # node39:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1040 --link node00-eth5 # node40:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1050 --link node00-eth6 # node48:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1060 --link node00-eth7 # node49:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1070 --link node00-eth8 # node55:eth1

# node01
clab tools vxlan create --remote 198.18.1.101 --id 1080 --link node01-eth1 # node15:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1090 --link node01-eth2 # node17:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1100 --link node01-eth3 # node19:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1110 --link node01-eth4 # node20:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1120 --link node01-eth5 # node34:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1130 --link node01-eth6 # node37:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1140 --link node01-eth7 # node53:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1150 --link node01-eth8 # node55:eth2

# node02
clab tools vxlan create --remote 198.18.1.103 --id 1160 --link node02-eth2 # node34:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1170 --link node02-eth3 # node41:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1180 --link node02-eth4 # node44:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1190 --link node02-eth5 # node46:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1200 --link node02-eth6 # node49:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1210 --link node02-eth7 # node56:eth1

# node03
clab tools vxlan create --remote 198.18.1.101 --id 1220 --link node03-eth1 # node15:eth2
clab tools vxlan create --remote 198.18.1.101 --id 1230 --link node03-eth2 # node16:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1240 --link node03-eth3 # node18:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1250 --link node03-eth4 # node35:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1260 --link node03-eth5 # node36:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1270 --link node03-eth6 # node38:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1280 --link node03-eth7 # node54:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1290 --link node03-eth8 # node56:eth2

# node04
clab tools vxlan create --remote 198.18.1.101 --id 1300 --link node04-eth3 # node17:eth2
clab tools vxlan create --remote 198.18.1.101 --id 1310 --link node04-eth4 # node23:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1320 --link node04-eth5 # node26:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1330 --link node04-eth6 # node29:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1340 --link node04-eth7 # node39:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1350 --link node04-eth8 # node54:eth2

# node05
clab tools vxlan create --remote 198.18.1.101 --id 1360 --link node05-eth2 # node24:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1370 --link node05-eth3 # node25:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1380 --link node05-eth4 # node27:eth2
clab tools vxlan create --remote 198.18.1.101 --id 1390 --link node05-eth5 # node28:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1400 --link node05-eth6 # node29:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1410 --link node05-eth7 # node34:eth3
clab tools vxlan create --remote 198.18.1.103 --id 1420 --link node05-eth8 # node35:eth2

# node06
clab tools vxlan create --remote 198.18.1.101 --id 1430 --link node06-eth2 # node16:eth2
clab tools vxlan create --remote 198.18.1.101 --id 1440 --link node06-eth3 # node17:eth3
clab tools vxlan create --remote 198.18.1.101 --id 1450 --link node06-eth4 # node21:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1460 --link node06-eth5 # node25:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1470 --link node06-eth6 # node31:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1480 --link node06-eth7 # node33:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1490 --link node06-eth8 # node46:eth2


# node07
clab tools vxlan create --remote 198.18.1.103 --id 1500 --link node07-eth4 # node31:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1510 --link node07-eth5 # node35:eth3
clab tools vxlan create --remote 198.18.1.103 --id 1520 --link node07-eth6 # node42:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1530 --link node07-eth7 # node43:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1540 --link node07-eth8 # node55:eth3

# node08
clab tools vxlan create --remote 198.18.1.103 --id 1550 --link node08-eth3 # node30:eth1
clab tools vxlan create --remote 198.18.1.103 --id 1560 --link node08-eth4 # node34:eth4
clab tools vxlan create --remote 198.18.1.103 --id 1570 --link node08-eth5 # node38:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1580 --link node08-eth6 # node39:eth3
clab tools vxlan create --remote 198.18.1.103 --id 1590 --link node08-eth7 # node42:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1600 --link node08-eth8 # node50:eth1

# node09
clab tools vxlan create --remote 198.18.1.104 --id 1610 --link node09-eth6 # node45:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1620 --link node09-eth7 # node54:eth3
clab tools vxlan create --remote 198.18.1.104 --id 1630 --link node09-eth8 # node55:eth4

# node10
clab tools vxlan create --remote 198.18.1.101 --id 1640 --link node10-eth3 # node18:eth3
clab tools vxlan create --remote 198.18.1.103 --id 1650 --link node10-eth4 # node29:eth3
clab tools vxlan create --remote 198.18.1.103 --id 1660 --link node10-eth5 # node37:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1670 --link node10-eth6 # node40:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1680 --link node10-eth7 # node43:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1690 --link node10-eth8 # node46:eth3

# node11
clab tools vxlan create --remote 198.18.1.101 --id 1700 --link node11-eth1 # node22:eth1
clab tools vxlan create --remote 198.18.1.101 --id 1710 --link node11-eth2 # node24:eth2
clab tools vxlan create --remote 198.18.1.101 --id 1720 --link node11-eth3 # node26:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1730 --link node11-eth4 # node38:eth3
clab tools vxlan create --remote 198.18.1.104 --id 1740 --link node11-eth5 # node46:eth4
clab tools vxlan create --remote 198.18.1.104 --id 1750 --link node11-eth6 # node51:eth1
clab tools vxlan create --remote 198.18.1.104 --id 1760 --link node11-eth7 # node55:eth5

# node12
clab tools vxlan create --remote 198.18.1.101 --id 1770 --link node12-eth3 # node15:eth3
clab tools vxlan create --remote 198.18.1.101 --id 1780 --link node12-eth4 # node28:eth2
clab tools vxlan create --remote 198.18.1.103 --id 1790 --link node12-eth5 # node30:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1800 --link node12-eth6 # node45:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1810 --link node12-eth7 # node46:eth5
clab tools vxlan create --remote 198.18.1.104 --id 1820 --link node12-eth8 # node48:eth2

# node13
clab tools vxlan create --remote 198.18.1.101 --id 1830 --link node13-eth3 # node16:eth3
clab tools vxlan create --remote 198.18.1.101 --id 1840 --link node13-eth4 # node24:eth3
clab tools vxlan create --remote 198.18.1.103 --id 1850 --link node13-eth5 # node40:eth3
clab tools vxlan create --remote 198.18.1.104 --id 1860 --link node13-eth6 # node45:eth3
clab tools vxlan create --remote 198.18.1.104 --id 1870 --link node13-eth7 # node50:eth2
clab tools vxlan create --remote 198.18.1.104 --id 1880 --link node13-eth8 # node53:eth2

# node14
clab tools vxlan create --remote 198.18.1.101 --id 1890 --link node14-eth2 # node18:eth3
clab tools vxlan create --remote 198.18.1.101 --id 1900 --link node14-eth3 # node20:eth2
clab tools vxlan create --remote 198.18.1.101 --id 1910 --link node14-eth4 # node21:eth2
clab tools vxlan create --remote 198.18.1.101 --id 1920 --link node14-eth5 # node22:eth2
clab tools vxlan create --remote 198.18.1.101 --id 1930 --link node14-eth6 # node27:eth3
clab tools vxlan create --remote 198.18.1.103 --id 1940 --link node14-eth7 # node30:eth3





























