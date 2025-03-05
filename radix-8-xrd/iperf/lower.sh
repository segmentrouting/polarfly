#!/bin/bash

# host00
docker exec -it clab-radix8-isis-host00 apk add iproute2
docker exec -it clab-radix8-isis-host00 ip addr add fc00:0:f800:0::2/64 dev eth1
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0::/32 via fc00:0:f800::1 dev eth1
docker exec -it clab-radix8-isis-host00 ip addr add fc00:0:f800:4::2/64 dev eth2
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:4::1 dev eth2
docker exec -it clab-radix8-isis-host00 ip addr add fc00:0:f800:8::2/64 dev eth3
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:8::1 dev eth3
docker exec -it clab-radix8-isis-host00 ip addr add fc00:0:f800:c::2/64 dev eth4
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:c::1 dev eth4

docker exec -it clab-radix8-isis-host00 iperf3 -s -D
docker exec -it clab-radix8-isis-host00 iperf3 -c fc00:0:f801::2 
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0:f801::/64 \
encap seg6 mode encap segs fc00:0:1000:1053:1054:1029:: dev eth1


# host01
docker exec -it clab-radix8-isis-host01 apk add iproute2
docker exec -it clab-radix8-isis-host01 ip addr add fc00:0:f800:1::2/64 dev eth1
docker exec -it clab-radix8-isis-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:1::1 dev eth1
docker exec -it clab-radix8-isis-host01 ip addr add fc00:0:f800:5::2/64 dev eth2
docker exec -it clab-radix8-isis-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:5::1 dev eth2
docker exec -it clab-radix8-isis-host01 ip addr add fc00:0:f800:9::2/64 dev eth3
docker exec -it clab-radix8-isis-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:9::1 dev eth3
docker exec -it clab-radix8-isis-host01 ip addr add fc00:0:f800:d::2/64 dev eth4
docker exec -it clab-radix8-isis-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:d::1 dev eth4

# host02
docker exec -it clab-radix8-isis-host02 apk add iproute2
docker exec -it clab-radix8-isis-host02 ip addr add fc00:0:f800:2::2/64 dev eth1
docker exec -it clab-radix8-isis-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:2::1 dev eth1
docker exec -it clab-radix8-isis-host02 ip addr add fc00:0:f800:6::2/64 dev eth2
docker exec -it clab-radix8-isis-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:6::1 dev eth2
docker exec -it clab-radix8-isis-host02 ip addr add fc00:0:f800:a::2/64 dev eth3
docker exec -it clab-radix8-isis-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:a::1 dev eth3
docker exec -it clab-radix8-isis-host02 ip addr add fc00:0:f800:e::2/64 dev eth4
docker exec -it clab-radix8-isis-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:e::1 dev eth4

# host03
docker exec -it clab-radix8-isis-host03 apk add iproute2
docker exec -it clab-radix8-isis-host03 ip addr add fc00:0:f800:3::2/64 dev eth1
docker exec -it clab-radix8-isis-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:3::1 dev eth1
docker exec -it clab-radix8-isis-host03 ip addr add fc00:0:f800:7::2/64 dev eth2
docker exec -it clab-radix8-isis-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:7::1 dev eth2
docker exec -it clab-radix8-isis-host03 ip addr add fc00:0:f800:b::2/64 dev eth3
docker exec -it clab-radix8-isis-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:b::1 dev eth3
docker exec -it clab-radix8-isis-host03 ip addr add fc00:0:f800:f::2/64 dev eth4
docker exec -it clab-radix8-isis-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:f::1 dev eth4

# host04
docker exec -it clab-radix8-isis-host04 apk add iproute2
docker exec -it clab-radix8-isis-host04 ip addr add fc00:0:f800:1004::2/64 dev eth1
docker exec -it clab-radix8-isis-host04 ip -6 route add fc00:0::/32 via fc00:0:f800:1004::1 dev eth1
docker exec -it clab-radix8-isis-host04 apk add iproute2
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host04 iperf3 -s -p 5215 -D

# host05
docker exec -it clab-radix8-isis-host05 apk add iproute2
docker exec -it clab-radix8-isis-host05 ip addr add fc00:0:f800:1005::2/64 dev eth1
docker exec -it clab-radix8-isis-host05 ip -6 route add fc00:0::/32 via fc00:0:f800:1005::1 dev eth1
docker exec -it clab-radix8-isis-host05 apk add iproute2
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host05 iperf3 -s -p 5215 -D

# host06
docker exec -it clab-radix8-isis-host06 apk add iproute2
docker exec -it clab-radix8-isis-host06 ip addr add fc00:0:f800:1006::2/64 dev eth1
docker exec -it clab-radix8-isis-host06 ip -6 route add fc00:0::/32 via fc00:0:f800:1006::1 dev eth1
docker exec -it clab-radix8-isis-host06 apk add iproute2
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host06 iperf3 -s -p 5215 -D

# host07
docker exec -it clab-radix8-isis-host07 apk add iproute2
docker exec -it clab-radix8-isis-host07 ip addr add fc00:0:f800:1007::2/64 dev eth1
docker exec -it clab-radix8-isis-host07 ip -6 route add fc00:0::/32 via fc00:0:f800:1007::1 dev eth1
docker exec -it clab-radix8-isis-host12 iperf3 -s -D

# host08
docker exec -it clab-radix8-isis-host08 apk add iproute2
docker exec -it clab-radix8-isis-host08 ip addr add fc00:0:f800:1008::2/64 dev eth1
docker exec -it clab-radix8-isis-host08 ip -6 route add fc00:0::/32 via fc00:0:f800:1008::1 dev eth1
docker exec -it clab-radix8-isis-host08 iperf3 -s -D

# host09
docker exec -it clab-radix8-isis-host09 apk add iproute2
docker exec -it clab-radix8-isis-host09 ip addr add fc00:0:f800:1009::2/64 dev eth1
docker exec -it clab-radix8-isis-host09 ip -6 route add fc00:0::/32 via fc00:0:f800:1009::1 dev eth1
docker exec -it clab-radix8-isis-host09 iperf3 -s -D

# host10
docker exec -it clab-radix8-isis-host10 apk add iproute2
docker exec -it clab-radix8-isis-host10 ip addr add fc00:0:f800:1010::2/64 dev eth1
docker exec -it clab-radix8-isis-host10 ip -6 route add fc00:0::/32 via fc00:0:f800:1010::1 dev eth1
docker exec -it clab-radix8-isis-host10 iperf3 -s -D

# host11    
docker exec -it clab-radix8-isis-host11 apk add iproute2
docker exec -it clab-radix8-isis-host11 ip addr add fc00:0:f800:1011::2/64 dev eth1
docker exec -it clab-radix8-isis-host11 ip -6 route add fc00:0::/32 via fc00:0:f800:1011::1 dev eth1
docker exec -it clab-radix8-isis-host11 iperf3 -s -D

# host12
docker exec -it clab-radix8-isis-host12 apk add iproute2
docker exec -it clab-radix8-isis-host12 ip addr add fc00:0:f800:1012::2/64 dev eth1
docker exec -it clab-radix8-isis-host12 ip -6 route add fc00:0::/32 via fc00:0:f800:1012::1 dev eth1
docker exec -it clab-radix8-isis-host12 iperf3 -s -D

# host13
docker exec -it clab-radix8-isis-host13 apk add iproute2
docker exec -it clab-radix8-isis-host13 ip addr add fc00:0:f800:1013::2/64 dev eth1
docker exec -it clab-radix8-isis-host13 ip -6 route add fc00:0::/32 via fc00:0:f800:1013::1 dev eth1
docker exec -it clab-radix8-isis-host12 iperf3 -s -D










