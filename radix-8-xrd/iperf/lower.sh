#!/bin/bash

# host00
docker exec -it clab-radix8-isis-host00 ip addr add fc00:0:f800:0::2/64 dev eth1
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0::/32 via fc00:0:f800::1 dev eth1
docker exec -it clab-radix8-isis-host00 ip addr add fc00:0:f800:4::2/64 dev eth2
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:4::1 dev eth2
docker exec -it clab-radix8-isis-host00 ip addr add fc00:0:f800:8::2/64 dev eth3
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:8::1 dev eth3
docker exec -it clab-radix8-isis-host00 ip addr add fc00:0:f800:c::2/64 dev eth4
docker exec -it clab-radix8-isis-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:c::1 dev eth4


# host01
docker exec -it clab-radix8-isis-host01 ip addr add fc00:0:f800:1::2/64 dev eth1
docker exec -it clab-radix8-isis-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:1::1 dev eth1
docker exec -it clab-radix8-isis-host01 ip addr add fc00:0:f800:5::2/64 dev eth2
docker exec -it clab-radix8-isis-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:5::1 dev eth2
docker exec -it clab-radix8-isis-host01 ip addr add fc00:0:f800:9::2/64 dev eth3
docker exec -it clab-radix8-isis-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:9::1 dev eth3
docker exec -it clab-radix8-isis-host01 ip addr add fc00:0:f800:d::2/64 dev eth4
docker exec -it clab-radix8-isis-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:d::1 dev eth4

# host02
docker exec -it clab-radix8-isis-host02 ip addr add fc00:0:f800:2::2/64 dev eth1
docker exec -it clab-radix8-isis-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:2::1 dev eth1
docker exec -it clab-radix8-isis-host02 ip addr add fc00:0:f800:6::2/64 dev eth2
docker exec -it clab-radix8-isis-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:6::1 dev eth2
docker exec -it clab-radix8-isis-host02 ip addr add fc00:0:f800:a::2/64 dev eth3
docker exec -it clab-radix8-isis-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:a::1 dev eth3
docker exec -it clab-radix8-isis-host02 ip addr add fc00:0:f800:e::2/64 dev eth4
docker exec -it clab-radix8-isis-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:e::1 dev eth4

# host03
docker exec -it clab-radix8-isis-host03 ip addr add fc00:0:f800:3::2/64 dev eth1
docker exec -it clab-radix8-isis-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:3::1 dev eth1
docker exec -it clab-radix8-isis-host03 ip addr add fc00:0:f800:7::2/64 dev eth2
docker exec -it clab-radix8-isis-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:7::1 dev eth2
docker exec -it clab-radix8-isis-host03 ip addr add fc00:0:f800:b::2/64 dev eth3
docker exec -it clab-radix8-isis-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:b::1 dev eth3
docker exec -it clab-radix8-isis-host03 ip addr add fc00:0:f800:f::2/64 dev eth4
docker exec -it clab-radix8-isis-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:f::1 dev eth4

# host04
docker exec -it clab-radix8-isis-host04 ip addr add fc00:0:f800:1004::2/64 dev eth1
docker exec -it clab-radix8-isis-host04 ip -6 route add fc00:0::/32 via fc00:0:f800:1004::1 dev eth1

# host05
docker exec -it clab-radix8-isis-host05 ip addr add fc00:0:f800:1005::2/64 dev eth1
docker exec -it clab-radix8-isis-host05 ip -6 route add fc00:0::/32 via fc00:0:f800:1005::1 dev eth1

# host06
docker exec -it clab-radix8-isis-host06 ip addr add fc00:0:f800:1006::2/64 dev eth1
docker exec -it clab-radix8-isis-host06 ip -6 route add fc00:0::/32 via fc00:0:f800:1006::1 dev eth1

# host07
docker exec -it clab-radix8-isis-host07 ip addr add fc00:0:f800:1007::2/64 dev eth1
docker exec -it clab-radix8-isis-host07 ip -6 route add fc00:0::/32 via fc00:0:f800:1007::1 dev eth1

# host08
docker exec -it clab-radix8-isis-host08 ip addr add fc00:0:f800:1008::2/64 dev eth1
docker exec -it clab-radix8-isis-host08 ip -6 route add fc00:0::/32 via fc00:0:f800:1008::1 dev eth1












