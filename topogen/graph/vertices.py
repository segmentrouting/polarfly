def generate_vertices(count, node_categories=None):
    """
    Generate enriched vertex data with IPv4, IPv6, and BGP information
    node_categories: optional dict mapping node names to their categories (W, V1c, etc.)
    """
    vertices = []
    for i in range(count):
        # Calculate IPv4 address components
        last_octet = i % 256
        third_octet = (i // 256) % 256
        router_id = f"10.0.{third_octet}.{last_octet}"
        
        # Calculate IPv6 SID in hex (starting from 0x1000)
        hex_value = format(0x1000 + i, 'x')
        
        vertex = {
            "_key": f"{router_id}_{4200000000+i}",
            "router_id": router_id,
            "name": f"node{i:02d}",
            "tier": "dc-tier-0",
            "asn": 4200000000 + i,
            "sids": [
                {
                    "srv6_sid": f"fc00:0:{hex_value}::",
                    "srv6_endpoint_behavior": {
                        "endpoint_behavior": 48,
                        "flag": 0,
                        "algo": 0
                    }
                }
            ]
        }
        
        # Add category if available
        if node_categories and f"node{i:02d}" in node_categories:
            vertex["category"] = node_categories[f"node{i:02d}"]
            
        vertices.append(vertex)
    return vertices 