#!/bin/sh

# IP addresses and routes

## host00
docker exec -it clab-clos-host00 ip addr add 10.10.0.2/24 dev eth1
docker exec -it clab-clos-host00 ip route add 10.0.0.0/8 via 10.10.0.1 dev eth1
docker exec -it clab-clos-host00 ip addr add fc00:0:f800::2/64 dev eth1
docker exec -it clab-clos-host00 ip -6 route add fc00:0::/32 via fc00:0:f800::1 dev eth1
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:fe00::/48 via fc00:0:f800::1 dev eth1
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:f800:8000::/64 encap seg6 mode encap segs fc00:0:fe00:fe00:fe04:fe04:: dev eth1

docker exec -it clab-clos-host00 ip addr add 10.10.4.2/24 dev eth2
docker exec -it clab-clos-host00 ip route add 10.0.0.0/8 via 10.10.4.1 dev eth2
docker exec -it clab-clos-host00 ip addr add fc00:0:f800:4::2/64 dev eth2
docker exec -it clab-clos-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:4::1 dev eth2
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:fe01::/48 via fc00:0:f800:4::1 dev eth2
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:f800:8004::/64 encap seg6 mode encap segs fc00:0:fe01:fe01:fe05:fe05:: dev eth2

docker exec -it clab-clos-host00 ip addr add 10.10.8.2/24 dev eth3
docker exec -it clab-clos-host00 ip route add 10.0.0.0/8 via 10.10.8.1 dev eth3
docker exec -it clab-clos-host00 ip addr add fc00:0:f800:8::2/64 dev eth3
docker exec -it clab-clos-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:8::1 dev eth3
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:fe02::/48 via fc00:0:f800:8::1 dev eth3
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:f800:8008::/64 encap seg6 mode encap segs fc00:0:fe02:fe02:fe06:fe06:: dev eth3

docker exec -it clab-clos-host00 ip addr add 10.10.12.2/24 dev eth4
docker exec -it clab-clos-host00 ip route add 10.0.0.0/8 via 10.10.12.1 dev eth4
docker exec -it clab-clos-host00 ip addr add fc00:0:f800:c::2/64 dev eth4
docker exec -it clab-clos-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:c::1 dev eth4
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:fe03::/48 via fc00:0:f800:c::1 dev eth4
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:f800:800c::/64 encap seg6 mode encap segs fc00:0:fe03:fe03:fe07:fe07:: dev eth4

docker exec -it clab-clos-host00 ip addr add 10.10.16.2/24 dev eth5
docker exec -it clab-clos-host00 ip route add 10.0.0.0/8 via 10.10.16.1 dev eth5
docker exec -it clab-clos-host00 ip addr add fc00:0:f800:10::2/64 dev eth5
docker exec -it clab-clos-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:10::1 dev eth5
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:fe04::/48 via fc00:0:f800:10::1 dev eth5
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:f800:8010::/64 encap seg6 mode encap segs fc00:0:fe04:fe04:fe08:fe08:: dev eth5

docker exec -it clab-clos-host00 ip addr add 10.10.20.2/24 dev eth6
docker exec -it clab-clos-host00 ip route add 10.0.0.0/8 via 10.10.20.1 dev eth6
docker exec -it clab-clos-host00 ip addr add fc00:0:f800:14::2/64 dev eth6
docker exec -it clab-clos-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:14::1 dev eth6
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:fe05::/48 via fc00:0:f800:14::1 dev eth6
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:f800:8014::/64 encap seg6 mode encap segs fc00:0:fe05:fe05:fe09:fe09:: dev eth6

docker exec -it clab-clos-host00 ip addr add 10.10.24.2/24 dev eth7
docker exec -it clab-clos-host00 ip route add 10.0.0.0/8 via 10.10.24.1 dev eth7
docker exec -it clab-clos-host00 ip addr add fc00:0:f800:18::2/64 dev eth7
docker exec -it clab-clos-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:18::1 dev eth7
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:fe06::/48 via fc00:0:f800:18::1 dev eth7
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:f800:8018::/64 encap seg6 mode encap segs fc00:0:fe06:fe06:fe0a:fe0a:: dev eth7

docker exec -it clab-clos-host00 ip addr add 10.10.28.2/24 dev eth8
docker exec -it clab-clos-host00 ip route add 10.0.0.0/8 via 10.10.28.1 dev eth8
docker exec -it clab-clos-host00 ip addr add fc00:0:f800:1c::2/64 dev eth8
docker exec -it clab-clos-host00 ip -6 route add fc00:0::/32 via fc00:0:f800:1c::1 dev eth8
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:fe07::/48 via fc00:0:f800:1c::1 dev eth8
# docker exec -it clab-clos-host00 ip -6 route add fc00:0:f800:801c::/64 encap seg6 mode encap segs fc00:0:fe07:fe07:fe0b:fe0b:: dev eth8


## host01
docker exec -it clab-clos-host01 ip addr add 10.10.1.2/24 dev eth1
docker exec -it clab-clos-host01 ip route add 10.0.0.0/8 via 10.10.1.1 dev eth1
docker exec -it clab-clos-host01 ip addr add fc00:0:f800:1::2/64 dev eth1
docker exec -it clab-clos-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:1::1 dev eth1
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:fe01::/48 via fc00:0:f800:1::1 dev eth1
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:f800:8001::/64 encap seg6 mode encap segs fc00:0:fe01:fe00:fe05:fe04:: dev eth1

docker exec -it clab-clos-host01 ip addr add 10.10.5.2/24 dev eth2
docker exec -it clab-clos-host01 ip route add 10.0.0.0/8 via 10.10.5.1 dev eth2
docker exec -it clab-clos-host01 ip addr add fc00:0:f800:5::2/64 dev eth2
docker exec -it clab-clos-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:5::1 dev eth2
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:fe02::/48 via fc00:0:f800:5::1 dev eth2
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:f800:8005::/64 encap seg6 mode encap segs fc00:0:fe02:fe01:fe06:fe05:: dev eth2

docker exec -it clab-clos-host01 ip addr add 10.10.9.2/24 dev eth3
docker exec -it clab-clos-host01 ip route add 10.0.0.0/8 via 10.10.9.1 dev eth3
docker exec -it clab-clos-host01 ip addr add fc00:0:f800:9::2/64 dev eth3
docker exec -it clab-clos-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:9::1 dev eth3
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:f800:8009::/64 encap seg6 mode encap segs fc00:0:fe03:fe02:fe07:fe06:: dev eth3

docker exec -it clab-clos-host01 ip addr add 10.10.13.2/24 dev eth4
docker exec -it clab-clos-host01 ip route add 10.0.0.0/8 via 10.10.13.1 dev eth4
docker exec -it clab-clos-host01 ip addr add fc00:0:f800:d::2/64 dev eth4
docker exec -it clab-clos-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:d::1 dev eth4
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:f800:800d::/64 encap seg6 mode encap segs fc00:0:fe00:fe03:fe04:fe07:: dev eth4

docker exec -it clab-clos-host01 ip addr add 10.10.17.2/24 dev eth5
docker exec -it clab-clos-host01 ip route add 10.0.0.0/8 via 10.10.17.1 dev eth5
docker exec -it clab-clos-host01 ip addr add fc00:0:f800:11::2/64 dev eth5
docker exec -it clab-clos-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:11::1 dev eth5
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:fe04::/48 via fc00:0:f800:11::1 dev eth5
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:f800:8011::/64 encap seg6 mode encap segs fc00:0:fe04:fe04:fe08:fe08:: dev eth5

docker exec -it clab-clos-host01 ip addr add 10.10.21.2/24 dev eth6
docker exec -it clab-clos-host01 ip route add 10.0.0.0/8 via 10.10.21.1 dev eth6
docker exec -it clab-clos-host01 ip addr add fc00:0:f800:15::2/64 dev eth6
docker exec -it clab-clos-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:15::1 dev eth6
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:fe05::/48 via fc00:0:f800:15::1 dev eth6
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:f800:8015::/64 encap seg6 mode encap segs fc00:0:fe05:fe05:fe09:fe09:: dev eth6

docker exec -it clab-clos-host01 ip addr add 10.10.25.2/24 dev eth7
docker exec -it clab-clos-host01 ip route add 10.0.0.0/8 via 10.10.25.1 dev eth7
docker exec -it clab-clos-host01 ip addr add fc00:0:f800:19::2/64 dev eth7
docker exec -it clab-clos-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:19::1 dev eth7
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:fe06::/48 via fc00:0:f800:19::1 dev eth7
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:f800:8019::/64 encap seg6 mode encap segs fc00:0:fe06:fe06:fe0a:fe0a:: dev eth7

docker exec -it clab-clos-host01 ip addr add 10.10.29.2/24 dev eth8
docker exec -it clab-clos-host01 ip route add 10.0.0.0/8 via 10.10.29.1 dev eth8
docker exec -it clab-clos-host01 ip addr add fc00:0:f800:1d::2/64 dev eth8
docker exec -it clab-clos-host01 ip -6 route add fc00:0::/32 via fc00:0:f800:1d::1 dev eth8
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:fe07::/48 via fc00:0:f800:1d::1 dev eth8
# docker exec -it clab-clos-host01 ip -6 route add fc00:0:f800:801d::/64 encap seg6 mode encap segs fc00:0:fe07:fe07:fe0b:fe0b:: dev eth8


## host02
docker exec -it clab-clos-host02 ip addr add 10.10.2.2/24 dev eth1
docker exec -it clab-clos-host02 ip route add 10.0.0.0/8 via 10.10.2.1 dev eth1
docker exec -it clab-clos-host02 ip addr add fc00:0:f800:2::2/64 dev eth1
docker exec -it clab-clos-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:2::1 dev eth1
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:fe00::/48 via fc00:0:f800:20::1 dev eth1
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:f800::/64 encap seg6 mode encap segs fc00:0:fe00:fe00:fe00:fe00:: dev eth1

docker exec -it clab-clos-host02 ip addr add 10.10.6.2/24 dev eth2
docker exec -it clab-clos-host02 ip route add 10.0.0.0/8 via 10.10.6.1 dev eth2
docker exec -it clab-clos-host02 ip addr add fc00:0:f800:6::2/64 dev eth2
docker exec -it clab-clos-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:6::1 dev eth2
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:fe01::/48 via fc00:0:f800:6::1 dev eth2
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:f800:4::/64 encap seg6 mode encap segs fc00:0:fe01:fe01:fe01:fe01:: dev eth2

docker exec -it clab-clos-host02 ip addr add 10.10.10.2/24 dev eth3
docker exec -it clab-clos-host02 ip route add 10.0.0.0/8 via 10.10.10.1 dev eth3
docker exec -it clab-clos-host02 ip addr add fc00:0:f800:a::2/64 dev eth3
docker exec -it clab-clos-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:a::1 dev eth3
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:fe02::/48 via fc00:0:f800:a::1 dev eth3
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:f800:8::/64 encap seg6 mode encap segs fc00:0:fe02:fe02:fe02:fe02:: dev eth3

docker exec -it clab-clos-host02 ip addr add 10.10.14.2/24 dev eth4
docker exec -it clab-clos-host02 ip route add 10.0.0.0/8 via 10.10.14.1 dev eth4
docker exec -it clab-clos-host02 ip addr add fc00:0:f800:e::2/64 dev eth4
docker exec -it clab-clos-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:e::1 dev eth4
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:fe03::/48 via fc00:0:f800:e::1 dev eth4
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:f800:c::/64 encap seg6 mode encap segs fc00:0:fe03:fe03:fe03:fe03:: dev eth4

docker exec -it clab-clos-host02 ip addr add 10.10.18.2/24 dev eth5
docker exec -it clab-clos-host02 ip route add 10.0.0.0/8 via 10.10.18.1 dev eth5
docker exec -it clab-clos-host02 ip addr add fc00:0:f800:12::2/64 dev eth5
docker exec -it clab-clos-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:12::1 dev eth5
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:fe04::/48 via fc00:0:f800:12::1 dev eth5
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:f800:10::/64 encap seg6 mode encap segs fc00:0:fe04:fe04:fe04:fe04:: dev eth5

docker exec -it clab-clos-host02 ip addr add 10.10.22.2/24 dev eth6
docker exec -it clab-clos-host02 ip route add 10.0.0.0/8 via 10.10.22.1 dev eth6
docker exec -it clab-clos-host02 ip addr add fc00:0:f800:16::2/64 dev eth6
docker exec -it clab-clos-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:16::1 dev eth6
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:fe05::/48 via fc00:0:f800:16::1 dev eth6
# docker exec -it clab-clos-host02 ip -6 route add fc00:0:f800:14::/64 encap seg6 mode encap segs fc00:0:fe05:fe05:fe05:fe05:: dev eth6

docker exec -it clab-clos-host02 ip addr add 10.10.26.2/24 dev eth7
docker exec -it clab-clos-host02 ip route add 10.0.0.0/8 via 10.10.26.1 dev eth7
docker exec -it clab-clos-host02 ip addr add fc00:0:f800:1a::2/64 dev eth7
docker exec -it clab-clos-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:1a::1 dev eth7

docker exec -it clab-clos-host02 ip addr add 10.10.30.2/24 dev eth8
docker exec -it clab-clos-host02 ip route add 10.0.0.0/8 via 10.10.30.1 dev eth8
docker exec -it clab-clos-host02 ip addr add fc00:0:f800:1e::2/64 dev eth8
docker exec -it clab-clos-host02 ip -6 route add fc00:0::/32 via fc00:0:f800:1e::1 dev eth8


## host03
docker exec -it clab-clos-host03 ip addr add 10.10.3.2/24 dev eth1
docker exec -it clab-clos-host03 ip route add 10.0.0.0/8 via 10.10.3.1 dev eth1
docker exec -it clab-clos-host03 ip addr add fc00:0:f800:3::2/64 dev eth1
docker exec -it clab-clos-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:3::1 dev eth1

docker exec -it clab-clos-host03 ip addr add 10.10.7.2/24 dev eth2
docker exec -it clab-clos-host03 ip route add 10.0.0.0/8 via 10.10.7.1 dev eth2
docker exec -it clab-clos-host03 ip addr add fc00:0:f800:7::2/64 dev eth2
docker exec -it clab-clos-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:7::1 dev eth2

docker exec -it clab-clos-host03 ip addr add 10.10.11.2/24 dev eth3
docker exec -it clab-clos-host03 ip route add 10.0.0.0/8 via 10.10.11.1 dev eth3
docker exec -it clab-clos-host03 ip addr add fc00:0:f800:b::2/64 dev eth3
docker exec -it clab-clos-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:b::1 dev eth3
# docker exec -it clab-clos-host03 ip -6 route add fc00:0:fe03::/48 via fc00:0:f800:8009::1 dev eth3
# docker exec -it clab-clos-host03 ip -6 route add fc00:0:f800:9::/64 encap seg6 mode encap segs fc00:0:fe03:fe02:fe03:fe02:: dev eth3

docker exec -it clab-clos-host03 ip addr add 10.10.15.2/24 dev eth4
docker exec -it clab-clos-host03 ip route add 10.0.0.0/8 via 10.10.15.1 dev eth4
docker exec -it clab-clos-host03 ip addr add fc00:0:f800:f::2/64 dev eth4
docker exec -it clab-clos-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:f::1 dev eth4
# docker exec -it clab-clos-host03 ip -6 route add fc00:0:fe00::/48 via fc00:0:f800:800d::1 dev eth4
# docker exec -it clab-clos-host03 ip -6 route add fc00:0:f800:d::/64 encap seg6 mode encap segs fc00:0:fe00:fe03:fe00:fe03:: dev eth4

docker exec -it clab-clos-host03 ip addr add 10.10.19.2/24 dev eth5
docker exec -it clab-clos-host03 ip route add 10.0.0.0/8 via 10.10.19.1 dev eth5
docker exec -it clab-clos-host03 ip addr add fc00:0:f800:13::2/64 dev eth5
docker exec -it clab-clos-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:13::1 dev eth5

docker exec -it clab-clos-host03 ip addr add 10.10.23.2/24 dev eth6
docker exec -it clab-clos-host03 ip route add 10.0.0.0/8 via 10.10.23.1 dev eth6
docker exec -it clab-clos-host03 ip addr add fc00:0:f800:17::2/64 dev eth6
docker exec -it clab-clos-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:17::1 dev eth6

docker exec -it clab-clos-host03 ip addr add 10.10.27.2/24 dev eth7
docker exec -it clab-clos-host03 ip route add 10.0.0.0/8 via 10.10.27.1 dev eth7
docker exec -it clab-clos-host03 ip addr add fc00:0:f800:1b::2/64 dev eth7
docker exec -it clab-clos-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:1b::1 dev eth7

docker exec -it clab-clos-host03 ip addr add 10.10.31.2/24 dev eth8
docker exec -it clab-clos-host03 ip route add 10.0.0.0/8 via 10.10.31.1 dev eth8
docker exec -it clab-clos-host03 ip addr add fc00:0:f800:1f::2/64 dev eth8
docker exec -it clab-clos-host03 ip -6 route add fc00:0::/32 via fc00:0:f800:1f::1 dev eth8
