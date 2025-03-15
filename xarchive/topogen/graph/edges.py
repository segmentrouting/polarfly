def generate_edges(edge_list, vertices, radix):
    """
    Generate enriched edge data using vertex information
    edge_list: list of basic edges with from/to node names
    vertices: list of vertex data
    radix: switch radix value for collection naming
    Creates bidirectional edges for each connection
    """
    # Create lookup dictionary for vertices by name
    vertex_dict = {vertex["name"]: vertex for vertex in vertices}
    
    # Create collection name based on radix
    collection_name = f"radix_{radix}_node"
    
    enriched_edges = []
    for edge in edge_list:
        from_name = edge["_from"]
        to_name = edge["_to"]
        
        # Create forward edge
        forward_edge = {
            "from": from_name,
            "to": to_name,
            "_from": f"{collection_name}/{vertex_dict[from_name]['_key']}",
            "_to": f"{collection_name}/{vertex_dict[to_name]['_key']}"
        }
        enriched_edges.append(forward_edge)
        
        # Create reverse edge
        reverse_edge = {
            "from": to_name,
            "to": from_name,
            "_from": f"{collection_name}/{vertex_dict[to_name]['_key']}",
            "_to": f"{collection_name}/{vertex_dict[from_name]['_key']}"
        }
        enriched_edges.append(reverse_edge)
    
    return enriched_edges 