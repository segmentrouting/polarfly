#! /bin/bash

ip -6 route add fc00:0:f801::/64 \
  nexthop encap seg6 mode encap segs fc00:0:1049:1035:: via fc00:0:f800::1 dev eth1 weight 20 \
  nexthop encap seg6 mode encap segs fc00:0:1050:1019:: via fc00:0:f800:4::1 dev eth2 weight 10

ip -6 route add fc00:0:f801::/64 \
  nexthop encap seg6 mode encap segs fc00:0:1049:1035:: via fc00:0:f800::1 dev eth1 weight 20 \
  nexthop encap seg6 mode encap segs fc00:0:1050:1019:: via fc00:0:f800:4::1 dev eth2 weight 10



ip -6 route add fc00:0:f801::/64 metric 1 \
  nexthop encap seg6 mode encap segs fc00:0:1049:1035:: via fc00:0:f800::1 dev eth1

ip -6 route add fc00:0:f801::/64 metric 1 \
  nexthop encap seg6 mode encap segs fc00:0:1049:1035:: via fc00:0:f800::1 dev eth1 onlink