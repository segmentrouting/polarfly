#!/bin/bash

docker exec -it clab-radix8-isis-host29 ip addr add fc00:0:f801:0::2/64 dev eth1
docker exec -it clab-radix8-isis-host29 ip -6 route add fc00:0::/32 via fc00:0:f801::1 dev eth1
