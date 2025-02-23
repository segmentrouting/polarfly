#!/bin/sh

# IP addresses and routes

## host04
docker exec -it clab-clos-host04 ip addr add 10.11.0.2/24 dev eth1
docker exec -it clab-clos-host04 ip route add 10.0.0.0/8 via 10.11.0.1 dev eth1
docker exec -it clab-clos-host04 ip addr add fc00:0:f801::2/64 dev eth1

docker exec -it clab-clos-host04 ip addr add 10.11.4.2/24 dev eth2
docker exec -it clab-clos-host04 ip route add 10.0.0.0/8 via 10.11.4.1 dev eth2
docker exec -it clab-clos-host04 ip addr add fc00:0:f801:4::2/64 dev eth2

docker exec -it clab-clos-host04 ip addr add 10.11.8.2/24 dev eth3
docker exec -it clab-clos-host04 ip route add 10.0.0.0/8 via 10.11.8.1 dev eth3
docker exec -it clab-clos-host04 ip addr add fc00:0:f801:8::2/64 dev eth3

docker exec -it clab-clos-host04 ip addr add 10.11.12.2/24 dev eth4
docker exec -it clab-clos-host04 ip route add 10.0.0.0/8 via 10.11.12.1 dev eth4
docker exec -it clab-clos-host04 ip addr add fc00:0:f801:c::2/64 dev eth4

docker exec -it clab-clos-host04 ip addr add 10.11.16.2/24 dev eth5
docker exec -it clab-clos-host04 ip route add 10.0.0.0/8 via 10.11.16.1 dev eth5
docker exec -it clab-clos-host04 ip addr add fc00:0:f801:10::2/64 dev eth5

docker exec -it clab-clos-host04 ip addr add 10.11.20.2/24 dev eth6
docker exec -it clab-clos-host04 ip route add 10.0.0.0/8 via 10.11.20.1 dev eth6
docker exec -it clab-clos-host04 ip addr add fc00:0:f801:14::2/64 dev eth6

docker exec -it clab-clos-host04 ip addr add 10.11.24.2/24 dev eth7
docker exec -it clab-clos-host04 ip route add 10.0.0.0/8 via 10.11.24.1 dev eth7
docker exec -it clab-clos-host04 ip addr add fc00:0:f801:18::2/64 dev eth7

docker exec -it clab-clos-host04 ip addr add 10.11.28.2/24 dev eth8
docker exec -it clab-clos-host04 ip route add 10.0.0.0/8 via 10.11.28.1 dev eth8
docker exec -it clab-clos-host04 ip addr add fc00:0:f801:1c::2/64 dev eth8

docker exec -it clab-clos-host04 ip -6 route add fc00:0::/32 \
nexthop via fc00:0:f801::1 dev eth1 weight 1 \
nexthop via fc00:0:f801:4::1 dev eth2 weight 1 \
nexthop via fc00:0:f801:8::1 dev eth3 weight 1 \
nexthop via fc00:0:f801:c::1 dev eth4 weight 1 \
nexthop via fc00:0:f801:10::1 dev eth5 weight 1 \
nexthop via fc00:0:f801:14::1 dev eth6 weight 1 \
nexthop via fc00:0:f801:18::1 dev eth7 weight 1 \
nexthop via fc00:0:f801:1c::1 dev eth8 weight 1

## host05
docker exec -it clab-clos-host05 ip addr add 10.11.1.2/24 dev eth1
docker exec -it clab-clos-host05 ip route add 10.0.0.0/8 via 10.11.1.1 dev eth1
docker exec -it clab-clos-host05 ip addr add fc00:0:f801:1::2/64 dev eth1

docker exec -it clab-clos-host05 ip addr add 10.11.5.2/24 dev eth2
docker exec -it clab-clos-host05 ip route add 10.0.0.0/8 via 10.11.5.1 dev eth2
docker exec -it clab-clos-host05 ip addr add fc00:0:f801:5::2/64 dev eth2

docker exec -it clab-clos-host05 ip addr add 10.11.9.2/24 dev eth3
docker exec -it clab-clos-host05 ip route add 10.0.0.0/8 via 10.11.9.1 dev eth3
docker exec -it clab-clos-host05 ip addr add fc00:0:f801:9::2/64 dev eth3

docker exec -it clab-clos-host05 ip addr add 10.11.13.2/24 dev eth4
docker exec -it clab-clos-host05 ip route add 10.0.0.0/8 via 10.11.13.1 dev eth4
docker exec -it clab-clos-host05 ip addr add fc00:0:f801:d::2/64 dev eth4

docker exec -it clab-clos-host05 ip addr add 10.11.17.2/24 dev eth5
docker exec -it clab-clos-host05 ip route add 10.0.0.0/8 via 10.11.17.1 dev eth5
docker exec -it clab-clos-host05 ip addr add fc00:0:f801:11::2/64 dev eth5

docker exec -it clab-clos-host05 ip addr add 10.11.21.2/24 dev eth6
docker exec -it clab-clos-host05 ip route add 10.0.0.0/8 via 10.11.21.1 dev eth6
docker exec -it clab-clos-host05 ip addr add fc00:0:f801:15::2/64 dev eth6

docker exec -it clab-clos-host05 ip addr add 10.11.25.2/24 dev eth7
docker exec -it clab-clos-host05 ip route add 10.0.0.0/8 via 10.11.25.1 dev eth7
docker exec -it clab-clos-host05 ip addr add fc00:0:f801:19::2/64 dev eth7

docker exec -it clab-clos-host05 ip addr add 10.11.29.2/24 dev eth8
docker exec -it clab-clos-host05 ip route add 10.0.0.0/8 via 10.11.29.1 dev eth8
docker exec -it clab-clos-host05 ip addr add fc00:0:f801:1d::2/64 dev eth8

docker exec -it clab-clos-host05 ip -6 route add fc00:0::/32 \
nexthop via fc00:0:f801:1::1 dev eth1 weight 1 \
nexthop via fc00:0:f801:5::1 dev eth2 weight 1 \
nexthop via fc00:0:f801:9::1 dev eth3 weight 1 \
nexthop via fc00:0:f801:d::1 dev eth4 weight 1 \
nexthop via fc00:0:f801:11::1 dev eth5 weight 1 \
nexthop via fc00:0:f801:15::1 dev eth6 weight 1 \
nexthop via fc00:0:f801:19::1 dev eth7 weight 1 \
nexthop via fc00:0:f801:1d::1 dev eth8 weight 1

## host06   
docker exec -it clab-clos-host06 ip addr add 10.11.2.2/24 dev eth1
docker exec -it clab-clos-host06 ip route add 10.0.0.0/8 via 10.11.2.1 dev eth1
docker exec -it clab-clos-host06 ip addr add fc00:0:f801:2::2/64 dev eth1

docker exec -it clab-clos-host06 ip addr add 10.11.6.2/24 dev eth2
docker exec -it clab-clos-host06 ip route add 10.0.0.0/8 via 10.11.6.1 dev eth2
docker exec -it clab-clos-host06 ip addr add fc00:0:f801:6::2/64 dev eth2

docker exec -it clab-clos-host06 ip addr add 10.11.10.2/24 dev eth3
docker exec -it clab-clos-host06 ip route add 10.0.0.0/8 via 10.11.10.1 dev eth3
docker exec -it clab-clos-host06 ip addr add fc00:0:f801:a::2/64 dev eth3

docker exec -it clab-clos-host06 ip addr add 10.11.14.2/24 dev eth4
docker exec -it clab-clos-host06 ip route add 10.0.0.0/8 via 10.11.14.1 dev eth4
docker exec -it clab-clos-host06 ip addr add fc00:0:f801:e::2/64 dev eth4

docker exec -it clab-clos-host06 ip addr add 10.11.18.2/24 dev eth5
docker exec -it clab-clos-host06 ip route add 10.0.0.0/8 via 10.11.18.1 dev eth5
docker exec -it clab-clos-host06 ip addr add fc00:0:f801:12::2/64 dev eth5

docker exec -it clab-clos-host06 ip addr add 10.11.22.2/24 dev eth6
docker exec -it clab-clos-host06 ip route add 10.0.0.0/8 via 10.11.22.1 dev eth6
docker exec -it clab-clos-host06 ip addr add fc00:0:f801:16::2/64 dev eth6

docker exec -it clab-clos-host06 ip addr add 10.11.26.2/24 dev eth7
docker exec -it clab-clos-host06 ip route add 10.0.0.0/8 via 10.11.26.1 dev eth7
docker exec -it clab-clos-host06 ip addr add fc00:0:f801:1a::2/64 dev eth7

docker exec -it clab-clos-host06 ip addr add 10.11.30.2/24 dev eth8
docker exec -it clab-clos-host06 ip route add 10.0.0.0/8 via 10.11.30.1 dev eth8
docker exec -it clab-clos-host06 ip addr add fc00:0:f801:1e::2/64 dev eth8

docker exec -it clab-clos-host06 ip -6 route add fc00:0::/32 \
nexthop via fc00:0:f801:2::1 dev eth1 weight 1 \
nexthop via fc00:0:f801:6::1 dev eth2 weight 1 \
nexthop via fc00:0:f801:a::1 dev eth3 weight 1 \
nexthop via fc00:0:f801:e::1 dev eth4 weight 1 \
nexthop via fc00:0:f801:12::1 dev eth5 weight 1 \
nexthop via fc00:0:f801:16::1 dev eth6 weight 1 \
nexthop via fc00:0:f801:1a::1 dev eth7 weight 1 \
nexthop via fc00:0:f801:1e::1 dev eth8 weight 1

## host07
docker exec -it clab-clos-host07 ip addr add 10.11.3.2/24 dev eth1
docker exec -it clab-clos-host07 ip route add 10.0.0.0/8 via 10.11.3.1 dev eth1
docker exec -it clab-clos-host07 ip addr add fc00:0:f801:3::2/64 dev eth1

docker exec -it clab-clos-host07 ip addr add 10.11.7.2/24 dev eth2
docker exec -it clab-clos-host07 ip route add 10.0.0.0/8 via 10.11.7.1 dev eth2
docker exec -it clab-clos-host07 ip addr add fc00:0:f801:7::2/64 dev eth2

docker exec -it clab-clos-host07 ip addr add 10.11.11.2/24 dev eth3
docker exec -it clab-clos-host07 ip route add 10.0.0.0/8 via 10.11.11.1 dev eth3
docker exec -it clab-clos-host07 ip addr add fc00:0:f801:b::2/64 dev eth3

docker exec -it clab-clos-host07 ip addr add 10.11.15.2/24 dev eth4
docker exec -it clab-clos-host07 ip route add 10.0.0.0/8 via 10.11.15.1 dev eth4
docker exec -it clab-clos-host07 ip addr add fc00:0:f801:f::2/64 dev eth4

docker exec -it clab-clos-host07 ip addr add 10.11.19.2/24 dev eth5
docker exec -it clab-clos-host07 ip route add 10.0.0.0/8 via 10.11.19.1 dev eth5
docker exec -it clab-clos-host07 ip addr add fc00:0:f801:13::2/64 dev eth5

docker exec -it clab-clos-host07 ip addr add 10.11.23.2/24 dev eth6
docker exec -it clab-clos-host07 ip route add 10.0.0.0/8 via 10.11.23.1 dev eth6
docker exec -it clab-clos-host07 ip addr add fc00:0:f801:17::2/64 dev eth6

docker exec -it clab-clos-host07 ip addr add 10.11.27.2/24 dev eth7
docker exec -it clab-clos-host07 ip route add 10.0.0.0/8 via 10.11.27.1 dev eth7
docker exec -it clab-clos-host07 ip addr add fc00:0:f801:1b::2/64 dev eth7

docker exec -it clab-clos-host07 ip addr add 10.11.31.2/24 dev eth8
docker exec -it clab-clos-host07 ip route add 10.0.0.0/8 via 10.11.31.1 dev eth8
docker exec -it clab-clos-host07 ip addr add fc00:0:f801:1f::2/64 dev eth8

docker exec -it clab-clos-host07 ip -6 route add fc00:0::/32 \
nexthop via fc00:0:f801:3::1 dev eth1 weight 1 \
nexthop via fc00:0:f801:7::1 dev eth2 weight 1 \
nexthop via fc00:0:f801:b::1 dev eth3 weight 1 \
nexthop via fc00:0:f801:f::1 dev eth4 weight 1 \
nexthop via fc00:0:f801:13::1 dev eth5 weight 1 \
nexthop via fc00:0:f801:17::1 dev eth6 weight 1 \
nexthop via fc00:0:f801:1b::1 dev eth7 weight 1 \
nexthop via fc00:0:f801:1f::1 dev eth8 weight 1