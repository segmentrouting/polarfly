### Fabric graph entries


      "srv6_ua_sids": [
        {
          "sid": "fc00:0:1039:e000::",
          "behavior": "End.DT",
          "structure": {
            "locator_block_len": 32,
            "locator_node_len": 16,
            "function_len": 16,
            "argument_len": 0
          }
        }
      ]

### ip -6 host routes
```bash
ip -6 route add 2001:db8:a013::2 nexthop encap seg6 mode encap.red segs fc00:0:1033:1013:e000:: via 2001:db8:a001::1 dev eth1 weight 4 

```