import json

def generate_nodes(count):
    nodes = []
    for i in range(count):
        node = {
            "_key": f"10.0.0.{i}_{4200000000+i}",
            "router_id": f"10.0.0.{i}",
            "name": f"node{i:02d}",  # This will pad with zeros, e.g., node00, node01
            "tier": "dc-tier-0",
            "asn": 4200000000 + i,
            "sids": [
                {
                    "srv6_sid": f"fc00:0:1{i:03d}::",  # This will pad with zeros, e.g., 1000, 1001
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

# Generate 57 nodes
nodes = generate_nodes(57)

# Write to file with nice formatting
with open('bgp-node.json', 'w') as f:
    json.dump(nodes, f, indent=4)

print("JSON file has been generated successfully!")