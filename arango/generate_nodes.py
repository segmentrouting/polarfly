import json

def generate_nodes(count):
    nodes = []
    for i in range(count):
        # Calculate IPv4 address components
        last_octet = i % 256
        third_octet = (i // 256) % 256
        router_id = f"10.0.{third_octet}.{last_octet}"
        
        # Calculate IPv6 SID in hex (starting from 0x1000)
        hex_value = format(0x1000 + i, 'x')  # Convert to hex, remove '0x' prefix
        
        node = {
            "_key": f"{router_id}_{4200000000+i}",
            "router_id": router_id,
            "name": f"node{i:02d}",  # This will pad with zeros, e.g., node00, node01
            "tier": "dc-tier-0",
            "asn": 4200000000 + i,
            "sids": [
                {
                    "srv6_sid": f"fc00:0:{hex_value}::",  # Will increment in hex: 1000, 1001, ..., 100a, etc.
                    "srv6_endpoint_behavior": {
                        "endpoint_behavior": 48,
                        "flag": 0,
                        "algo": 0
                    }
                }
            ]
        }
        nodes.append(node)
    return nodes

# Generate 993 nodes
nodes = generate_nodes(993)

# Write to file with nice formatting
with open('bgp-node.json', 'w') as f:
    json.dump(nodes, f, indent=4)

print("JSON file has been generated successfully!")