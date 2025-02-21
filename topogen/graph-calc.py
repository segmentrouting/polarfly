import argparse
import os
import json
from graph.vertices import generate_vertices
from graph.edges import generate_edges

def is_quadric(node_id, q):
    """
    Determine if a node is quadric by checking if its vector representation 
    is self-orthogonal in F³q
    """
    # Convert node_id to vector representation in F³q
    x = 1  # First non-zero component is always 1 in left-normalized form
    y = (node_id // q) % q
    z = node_id % q
    
    # Calculate dot product with self in Fq
    dot_product = (x * x + y * y + z * z) % q
    
    return dot_product == 0

def get_dot_product(node1, node2, q):
    """Calculate dot product of two nodes in F³q"""
    x1, y1, z1 = 1, (node1 // q) % q, node1 % q
    x2, y2, z2 = 1, (node2 // q) % q, node2 % q
    return (x1 * x2 + y1 * y2 + z1 * z2) % q

def find_center_nodes(node_id, quadrics, adj_nodes, q):
    """
    Determine if a V1 node is a center node by checking if it's
    connected to our chosen quadric
    """
    if node_id not in quadrics:
        # Find a quadric that has exactly q connections to non-quadric nodes
        chosen_quadric = None
        for quadric in quadrics:
            non_quadric_connections = sum(1 for n in range(q*q + q + 1)
                                        if n not in quadrics and 
                                        get_dot_product(n, quadric, q) == 0)
            if non_quadric_connections == q:
                chosen_quadric = quadric
                break
        
        if chosen_quadric is None:
            chosen_quadric = min(quadrics)  # fallback to first quadric
            
        # Count how many center nodes we've identified so far
        center_count = sum(1 for n in range(node_id) 
                          if n not in quadrics and 
                          get_dot_product(n, chosen_quadric, q) == 0)
        
        # Accept this node as a center if it's connected to our chosen quadric
        # and we haven't reached q centers yet
        if get_dot_product(node_id, chosen_quadric, q) == 0 and center_count < q:
            return True
    return False

def get_node_category(node_id, quadrics, adj_nodes, q):
    """
    Categorize node as:
    W   - quadric vertices
    V1c - V1 vertices that are cluster centers (connected to arbitrary quadric)
    V1n - V1 vertices that are not cluster centers
    V2  - vertices not adjacent to W
    """
    if node_id in quadrics:
        return "W"
    
    # Check if node is adjacent to any quadric
    quadric_adjacent = False
    for quadric in quadrics:
        if get_dot_product(node_id, quadric, q) == 0:
            quadric_adjacent = True
            break
    
    if quadric_adjacent:
        # It's a V1 node, check if it's a center
        if find_center_nodes(node_id, quadrics, adj_nodes, q):
            return "V1c"
        return "V1n"
    
    return "V2"

def get_cluster_assignment(node_id, quadrics, adj_lists, q):
    """
    Determine which cluster (C0 through Cq) a node belongs to:
    C0 - quadric vertices (W)
    C1-Cq - non-quadric clusters, each with a center V1c vertex and its neighbors
    Following Algorithm 1 from the paper:
    1. All quadrics go to C0
    2. Select arbitrary quadric v
    3. For each vertex u adjacent to v:
       - u becomes a center of new cluster Ci
       - All non-quadric neighbors of u go into Ci
    """
    # Quadrics always go to C0
    if node_id in quadrics:
        return 0

    # Find our chosen quadric
    chosen_quadric = None
    for quadric in quadrics:
        non_quadric_connections = sum(1 for n in range(q*q + q + 1)
                                    if n not in quadrics and 
                                    get_dot_product(n, quadric, q) == 0)
        if non_quadric_connections == q:
            chosen_quadric = quadric
            break
    
    if chosen_quadric is None:
        chosen_quadric = min(quadrics)

    # Get all center nodes (vertices adjacent to chosen quadric)
    centers = []
    for n in range(q*q + q + 1):
        if n not in quadrics and get_dot_product(n, chosen_quadric, q) == 0:
            centers.append(n)
            if len(centers) == q:  # We've found all q centers
                break

    # If this node is a center, assign it to corresponding cluster
    if node_id in centers:
        return centers.index(node_id) + 1

    # For non-center nodes, find which center they're connected to
    # by checking adjacency lists
    for i, center in enumerate(centers, 1):
        if node_id in adj_lists[center]:
            return i

    # Debug output if we can't assign a cluster
    print(f"Debug - Node {node_id}:")
    print(f"Chosen quadric: {chosen_quadric}")
    print(f"Centers: {centers}")
    print(f"Node adjacencies: {adj_lists[node_id]}")
    
    raise ValueError(f"Could not assign cluster for node {node_id}")

def convert_adj_to_edge_list(adj_file_path, node_prefix=None, q=None):
    nodes = []
    edges = set()  # using set to avoid duplicate edges
    quadrics = set()  # set to store quadric nodes
    node_categories = {}  # dictionary to store node categories
    adj_lists = {}  # store adjacency lists for each node
    
    with open(adj_file_path, 'r') as f:
        # Skip first line (metadata)
        next(f)
        
        # First pass: identify quadric nodes
        if q is not None:
            for node_id in range(q*q + q + 1):  # Total nodes in ERq
                if is_quadric(node_id, q):
                    quadrics.add(node_id)
        
        # Reset file pointer
        f.seek(0)
        next(f)
        
        # Second pass: store adjacency lists
        for node_id, line in enumerate(f):
            adj_nodes = [int(x) for x in line.strip().split()]
            adj_lists[node_id] = adj_nodes
            
            # Add node to nodes list with optional prefix
            node_name = f"{node_prefix}{node_id:02d}" if node_prefix else node_id
            nodes.append(node_name)
            
            # Create edge pairs
            for adj_node in adj_nodes:
                edge = tuple(sorted([node_id, adj_node]))
                edges.add(edge)
        
        # Third pass: categorize nodes
        if q is not None:
            for node_id in range(len(nodes)):
                node_name = f"{node_prefix}{node_id:02d}" if node_prefix else node_id
                category = get_node_category(node_id, quadrics, adj_lists[node_id], q)
                node_categories[node_name] = category
    
    # Convert edges set to sorted list and format with _from and _to
    edges_list = []
    for src, dst in sorted(list(edges)):
        edge = {
            "_from": f"{node_prefix}{src:02d}" if node_prefix else src,
            "_to": f"{node_prefix}{dst:02d}" if node_prefix else dst
        }
        edges_list.append(edge)
    
    # Add cluster assignments to metadata
    node_clusters = {}
    if q is not None:
        for node_id in range(len(nodes)):
            node_name = f"{node_prefix}{node_id:02d}" if node_prefix else node_id
            cluster = get_cluster_assignment(node_id, quadrics, adj_lists, q)
            node_clusters[node_name] = f"C{cluster}"
    
    # Create dictionary structure
    graph_dict = {
        "graph": {
            "nodes": nodes,
            "edges": edges_list,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges_list),
                "q_value": q,
                "node_categories": node_categories,
                "node_clusters": node_clusters,
                "category_counts": {
                    "W": sum(1 for cat in node_categories.values() if cat == "W"),
                    "V1c": sum(1 for cat in node_categories.values() if cat == "V1c"),
                    "V1n": sum(1 for cat in node_categories.values() if cat == "V1n"),
                    "V2": sum(1 for cat in node_categories.values() if cat == "V2")
                } if q is not None else None,
                "cluster_counts": {
                    f"C{i}": sum(1 for c in node_clusters.values() if c == f"C{i}")
                    for i in range(q+1)
                } if q is not None else None
            }
        }
    }
    
    return graph_dict

def parse_args():
    parser = argparse.ArgumentParser(description='Generate PolarFly topology and node data')
    parser.add_argument('-i', '--input', required=True,
                       help='Input adjacency file path (e.g., Brown.31.adj.txt)')
    parser.add_argument('-r', '--radix', type=int, required=True,
                       help='Switch radix (e.g., 8 for radix-8 directory)')
    parser.add_argument('-q', '--q-value', type=int, required=True,
                       help='Q value for identifying quadric nodes and node categories')
    parser.add_argument('-n', '--node-prefix', 
                       help='Optional prefix for node names (e.g., "router" for router00, router01, etc.)')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Verify input file exists
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file not found: {args.input}")
    
    # Create radix directory if it doesn't exist
    radix_dir = os.path.join("data", f"radix_{args.radix}")  # Changed from radix-{args.radix}
    if not os.path.exists(radix_dir):
        os.makedirs(radix_dir)
        print(f"Created directory: {radix_dir}")
    
    # Define output file paths
    summary_path = os.path.join(radix_dir, "summary.json")
    vertices_path = os.path.join(radix_dir, "vertices.json")
    edges_path = os.path.join(radix_dir, "edges.json")
    
    # Convert adjacency list to graph dictionary
    graph_dict = convert_adj_to_edge_list(args.input, args.node_prefix, args.q_value)
    
    # Generate vertex data
    node_count = graph_dict['graph']['metadata']['node_count']
    node_categories = graph_dict['graph']['metadata'].get('node_categories')
    vertices = generate_vertices(node_count, node_categories)
    
    # Generate edge data
    edges = generate_edges(graph_dict['graph']['edges'], vertices, args.radix)
    
    # Write all files
    with open(summary_path, 'w') as f:
        json.dump(graph_dict, f, indent=4)
    
    with open(vertices_path, 'w') as f:
        json.dump(vertices, f, indent=4)
    
    with open(edges_path, 'w') as f:
        json.dump(edges, f, indent=4)
    
    # Print validation info
    print(f"\nFiles generated in {radix_dir}:")
    print(f"  - summary.json")
    print(f"  - vertices.json")
    print(f"  - edges.json")
    print(f"\nGraph statistics:")
    print(f"Number of nodes: {graph_dict['graph']['metadata']['node_count']}")
    print(f"Number of edges: {graph_dict['graph']['metadata']['edge_count']}")
    if args.q_value:
        cats = graph_dict['graph']['metadata']['category_counts']
        print(f"Node categories:")
        print(f"  W    (quadrics): {cats['W']}")
        print(f"  V1c  (center nodes): {cats['V1c']}")
        print(f"  V1n  (non-center V1): {cats['V1n']}")
        print(f"  V2   (not adjacent to quadrics): {cats['V2']}")

if __name__ == "__main__":
    main()