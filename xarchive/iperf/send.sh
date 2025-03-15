#! /bin/bash

docker exec -it clab-radix8-isis-host04 iperf3 -c fc00:0:f801:1034::2 -p 5200 -t 10 -V &
docker exec -it clab-radix8-isis-host04 iperf3 -c fc00:0:f801:1034::2 -p 5201 -t 10 -V &
docker exec -it clab-radix8-isis-host04 iperf3 -c fc00:0:f801:1034::2 -p 5202 -t 10 -V &
docker exec -it clab-radix8-isis-host04 iperf3 -c fc00:0:f801:1034::2 -p 5203 -t 10 -V &
docker exec -it clab-radix8-isis-host04 iperf3 -c fc00:0:f801:1034::2 -p 5204 -t 10 -V &
docker exec -it clab-radix8-isis-host04 iperf3 -c fc00:0:f801:1034::2 -p 5205 -t 10 -V &
docker exec -it clab-radix8-isis-host04 iperf3 -c fc00:0:f801:1034::2 -p 5206 -t 10 -V &
docker exec -it clab-radix8-isis-host04 iperf3 -c fc00:0:f801:1034::2 -p 5207 -t 10 -V 
