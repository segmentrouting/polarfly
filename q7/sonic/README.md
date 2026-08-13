### Polarfly q=7 topology

Post polarfly topology data
```bash
curl -s -X POST http://localhost:30080/topology   -H 'Content-Type: application/json'   -d @q7/sonic/q7-fabric.json | python3 -m json.tool
```

Linux iproute2 example: **h001 to h019** via **sw001 -> sw051 -> sw019**

sw001 Ethernet28 f007
sw051 Ethernet24 f006

h001
```bash
ip -6 route add 2001:db8:a013::/64 \
  encap seg6 mode encap.red \
  segs fc00:0:f007:f006:e000:: dev eth1
```

h019
```bash
ip -6 route add 2001:db8:a001::/64 \
  encap seg6 mode encap.red \
  segs fc00:0:f007:f000:e000:: dev eth1
```

### iperf3 test

Start an iperf3 server on the receiver (`h019`):

```bash
docker exec -d h019 iperf3 -s
```

Run the client on the sender (`green-host00`) for a 10-second TCP test:

```bash
docker exec green-host00 iperf3 -c 2001:db8:bbbb:04::2 -t 10
```