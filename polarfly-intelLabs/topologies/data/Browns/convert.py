def convert_adj_to_edge_list(adj_file_path):
    nodes = []
    edges = set()  # using set to avoid duplicate edges
    
    with open(adj_file_path, 'r') as f:
        # Skip first line (metadata)
        next(f)
        
        # Read each line as adjacency list
        for node_id, line in enumerate(f):
            # Add node to nodes list
            nodes.append(node_id)
            
            # Get adjacent nodes
            adj_nodes = [int(x) for x in line.strip().split()]
            
            # Create edge pairs
            # Sort the pairs to ensure (1,2) and (2,1) are treated as same edge
            for adj_node in adj_nodes:
                edge = tuple(sorted([node_id, adj_node]))
                edges.add(edge)
    
    # Convert edges set to sorted list
    edges_list = sorted(list(edges))
    
    return nodes, edges_list

# Example usage
adj_file = "Brown.31.adj.txt"
nodes, edges = convert_adj_to_edge_list(adj_file)

# Write to graph.txt format
with open("../graph/graph31.txt", 'w') as f:
    f.write(f"Nodes: {nodes}\n")
    f.write(f"Edges: {edges}\n")

# Print some validation info
print(f"Number of nodes: {len(nodes)}")
print(f"Number of edges: {len(edges)}")