#!/bin/bash

# host29
docker exec -it clab-radix8-isis-host29 apk add iproute2
docker exec -it clab-radix8-isis-host29 ip addr add fc00:0:f801::2/64 dev eth1
docker exec -it clab-radix8-isis-host29 ip -6 route add fc00:0::/32 via fc00:0:f801::1 dev eth1

docker exec -it clab-radix8-isis-host29 ip -6 route add fc00:0:f800::/64 \
encap seg6 mode encap segs fc00:0:1019:1050:1000:: dev eth1

docker exec -it clab-radix8-isis-host29 iperf3 -s -D
docker exec -it clab-radix8-isis-host29 iperf3 -c fc00:0:f800::2 



# host33
docker exec -it clab-radix8-isis-host33 ip addr add fc00:0:f801:1033::2/64 dev eth1
docker exec -it clab-radix8-isis-host33 ip -6 route add fc00:0::/32 via fc00:0:f801:1033::1 dev eth1
docker exec -it clab-radix8-isis-host33 apk add iproute2
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host33 iperf3 -s -p 5215 -D

# host34    
docker exec -it clab-radix8-isis-host34 ip addr add fc00:0:f801:1034::2/64 dev eth1
docker exec -it clab-radix8-isis-host34 ip -6 route add fc00:0::/32 via fc00:0:f801:1034::1 dev eth1
docker exec -it clab-radix8-isis-host34 apk add iproute2
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host34 iperf3 -s -p 5215 -D

# host35
docker exec -it clab-radix8-isis-host35 ip addr add fc00:0:f801:1035::2/64 dev eth1
docker exec -it clab-radix8-isis-host35 ip -6 route add fc00:0::/32 via fc00:0:f801:1035::1 dev eth1
docker exec -it clab-radix8-isis-host35 apk add iproute2
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host35 iperf3 -s -p 5215 -D

# host36
docker exec -it clab-radix8-isis-host36 ip addr add fc00:0:f801:1036::2/64 dev eth1
docker exec -it clab-radix8-isis-host36 ip -6 route add fc00:0::/32 via fc00:0:f801:1036::1 dev eth1
docker exec -it clab-radix8-isis-host36 apk add iproute2
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host36 iperf3 -s -p 5215 -D

# host37
docker exec -it clab-radix8-isis-host37 ip addr add fc00:0:f801:1037::2/64 dev eth1
docker exec -it clab-radix8-isis-host37 ip -6 route add fc00:0::/32 via fc00:0:f801:1037::1 dev eth1
docker exec -it clab-radix8-isis-host37 apk add iproute2
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host37 iperf3 -s -p 5215 -D

# host38
docker exec -it clab-radix8-isis-host38 ip addr add fc00:0:f801:1038::2/64 dev eth1
docker exec -it clab-radix8-isis-host38 ip -6 route add fc00:0::/32 via fc00:0:f801:1038::1 dev eth1
docker exec -it clab-radix8-isis-host38 apk add iproute2
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host38 iperf3 -s -p 5215 -D

# host39
docker exec -it clab-radix8-isis-host39 ip addr add fc00:0:f801:1039::2/64 dev eth1
docker exec -it clab-radix8-isis-host39 ip -6 route add fc00:0::/32 via fc00:0:f801:1039::1 dev eth1
docker exec -it clab-radix8-isis-host39 apk add iproute2
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host39 iperf3 -s -p 5215 -D

# host40
docker exec -it clab-radix8-isis-host40 ip addr add fc00:0:f801:1040::2/64 dev eth1
docker exec -it clab-radix8-isis-host40 ip -6 route add fc00:0::/32 via fc00:0:f801:1040::1 dev eth1
docker exec -it clab-radix8-isis-host40 apk add iproute2
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host40 iperf3 -s -p 5215 -D

# host41
docker exec -it clab-radix8-isis-host41 ip addr add fc00:0:f801:1041::2/64 dev eth1
docker exec -it clab-radix8-isis-host41 ip -6 route add fc00:0::/32 via fc00:0:f801:1041::1 dev eth1
docker exec -it clab-radix8-isis-host41 apk add iproute2
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host41 iperf3 -s -p 5215 -D

# host42
docker exec -it clab-radix8-isis-host42 ip addr add fc00:0:f801:1042::2/64 dev eth1
docker exec -it clab-radix8-isis-host42 ip -6 route add fc00:0::/32 via fc00:0:f801:1042::1 dev eth1
docker exec -it clab-radix8-isis-host42 apk add iproute2
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host42 iperf3 -s -p 5215 -D

# host43
docker exec -it clab-radix8-isis-host43 ip addr add fc00:0:f801:1043::2/64 dev eth1
docker exec -it clab-radix8-isis-host43 ip -6 route add fc00:0::/32 via fc00:0:f801:1043::1 dev eth1
docker exec -it clab-radix8-isis-host43 apk add iproute2
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host43 iperf3 -s -p 5215 -D

# host44
docker exec -it clab-radix8-isis-host44 ip addr add fc00:0:f801:1044::2/64 dev eth1
docker exec -it clab-radix8-isis-host44 ip -6 route add fc00:0::/32 via fc00:0:f801:1044::1 dev eth1
docker exec -it clab-radix8-isis-host44 apk add iproute2
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host44 iperf3 -s -p 5215 -D

# host45
docker exec -it clab-radix8-isis-host45 ip addr add fc00:0:f801:1045::2/64 dev eth1
docker exec -it clab-radix8-isis-host45 ip -6 route add fc00:0::/32 via fc00:0:f801:1045::1 dev eth1
docker exec -it clab-radix8-isis-host45 apk add iproute2
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host45 iperf3 -s -p 5215 -D

# host46
docker exec -it clab-radix8-isis-host46 ip addr add fc00:0:f801:1046::2/64 dev eth1
docker exec -it clab-radix8-isis-host46 ip -6 route add fc00:0::/32 via fc00:0:f801:1046::1 dev eth1
docker exec -it clab-radix8-isis-host46 apk add iproute2
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host46 iperf3 -s -p 5215 -D

# host47
docker exec -it clab-radix8-isis-host47 ip addr add fc00:0:f801:1047::2/64 dev eth1
docker exec -it clab-radix8-isis-host47 ip -6 route add fc00:0::/32 via fc00:0:f801:1047::1 dev eth1
docker exec -it clab-radix8-isis-host47 apk add iproute2    
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host47 iperf3 -s -p 5215 -D

# host48
docker exec -it clab-radix8-isis-host48 ip addr add fc00:0:f801:1048::2/64 dev eth1
docker exec -it clab-radix8-isis-host48 ip -6 route add fc00:0::/32 via fc00:0:f801:1048::1 dev eth1
docker exec -it clab-radix8-isis-host48 apk add iproute2
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host48 iperf3 -s -p 5215 -D

# host49
docker exec -it clab-radix8-isis-host49 ip addr add fc00:0:f801:1049::2/64 dev eth1
docker exec -it clab-radix8-isis-host49 ip -6 route add fc00:0::/32 via fc00:0:f801:1049::1 dev eth1
docker exec -it clab-radix8-isis-host49 apk add iproute2
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host49 iperf3 -s -p 5215 -D

# host50
docker exec -it clab-radix8-isis-host50 ip addr add fc00:0:f801:1050::2/64 dev eth1
docker exec -it clab-radix8-isis-host50 ip -6 route add fc00:0::/32 via fc00:0:f801:1050::1 dev eth1
docker exec -it clab-radix8-isis-host50 apk add iproute2
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host50 iperf3 -s -p 5215 -D

# host51
docker exec -it clab-radix8-isis-host51 ip addr add fc00:0:f801:1051::2/64 dev eth1
docker exec -it clab-radix8-isis-host51 ip -6 route add fc00:0::/32 via fc00:0:f801:1051::1 dev eth1
docker exec -it clab-radix8-isis-host51 apk add iproute2
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host51 iperf3 -s -p 5215 -D

# host52
docker exec -it clab-radix8-isis-host52 ip addr add fc00:0:f801:1052::2/64 dev eth1
docker exec -it clab-radix8-isis-host52 ip -6 route add fc00:0::/32 via fc00:0:f801:1052::1 dev eth1
docker exec -it clab-radix8-isis-host52 apk add iproute2
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host52 iperf3 -s -p 5215 -D

# host53
docker exec -it clab-radix8-isis-host53 ip addr add fc00:0:f801:1053::2/64 dev eth1
docker exec -it clab-radix8-isis-host53 ip -6 route add fc00:0::/32 via fc00:0:f801:1053::1 dev eth1
docker exec -it clab-radix8-isis-host53 apk add iproute2
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host53 iperf3 -s -p 5215 -D

# host54
docker exec -it clab-radix8-isis-host54 ip addr add fc00:0:f801:1054::2/64 dev eth1
docker exec -it clab-radix8-isis-host54 ip -6 route add fc00:0::/32 via fc00:0:f801:1054::1 dev eth1
docker exec -it clab-radix8-isis-host54 apk add iproute2
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host54 iperf3 -s -p 5215 -D

# host55
docker exec -it clab-radix8-isis-host55 ip addr add fc00:0:f801:1055::2/64 dev eth1
docker exec -it clab-radix8-isis-host55 ip -6 route add fc00:0::/32 via fc00:0:f801:1055::1 dev eth1
docker exec -it clab-radix8-isis-host55 apk add iproute2    
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host55 iperf3 -s -p 5215 -D

# host56
docker exec -it clab-radix8-isis-host56 ip addr add fc00:0:f801:1056::2/64 dev eth1
docker exec -it clab-radix8-isis-host56 ip -6 route add fc00:0::/32 via fc00:0:f801:1056::1 dev eth1
docker exec -it clab-radix8-isis-host56 apk add iproute2
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5200 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5201 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5202 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5203 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5204 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5205 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5206 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5207 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5208 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5209 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5210 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5211 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5212 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5213 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5214 -D
docker exec -it clab-radix8-isis-host56 iperf3 -s -p 5215 -D

