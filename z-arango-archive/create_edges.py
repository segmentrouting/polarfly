from arango import ArangoClient
import json
import argparse
import ast  # For safely evaluating the string representation of tuples

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Create edges in ArangoDB IPv6 graph from adjacency list')
    parser.add_argument('-f', '--file', required=True,
                       help='Path to the adjacency list file (e.g., graph31.txt)')
    parser.add_argument('--create-graph', action='store_true',
                       help='Create the IPv6 graph if it does not exist')
    return parser.parse_args()

def setup_database():
    """Setup database connection and collections"""
    client = ArangoClient(hosts='http://198.18.133.102:30852')
    db = client.db('polarfly32', username='root', password='jalapeno')
    
    # Get bgp_node collection
    if not db.has_collection('bgp_node'):
        raise Exception("bgp_node collection does not exist!")
    bgp = db.collection('bgp_node')
    
    # Setup ipv6_graph edge collection
    if not db.has_collection('ipv6_graph'):
        ipv6graph = db.create_collection('ipv6_graph', edge=True)
        print("Created ipv6_graph edge collection")
    else:
        ipv6graph = db.collection('ipv6_graph')
        print("Using existing ipv6_graph edge collection")
    
    return db, bgp, ipv6graph

def create_graph_definition(db):
    """Create the graph definition if it doesn't exist"""
    if not db.has_graph('ipv6_graph'):
        graph = db.create_graph('ipv6_graph', edge_definitions=[
            {
                'collection': 'ipv6_graph',
                'from': ['bgp_node'],
                'to': ['bgp_node']
            }
        ])
        print("Created ipv6_graph graph definition")
    else:
        graph = db.graph('ipv6_graph')
        print("Using existing ipv6_graph graph definition")
    return graph

def get_node_key(bgp, node_num):
    """Get the _key for a node based on its node number"""
    aql = """
    FOR doc IN bgp_node
        FILTER doc.name == @node_name
        RETURN doc._key
    """
    node_name = f"node{node_num:02d}"
    result = db.aql.execute(aql, bind_vars={'node_name': node_name})
    return next(result, None)

def create_edges(db, bgp, ipv6graph, adjacency_file):
    """Create edges based on the adjacency list"""
    # Read adjacency list
    with open(adjacency_file, 'r') as f:
        adjacency_data = f.read().strip()
        # Safely evaluate the string representation of the list of tuples
        adjacencies = ast.literal_eval(adjacency_data)
    
    edges_created = 0
    for from_node, to_node in adjacencies:
        # Get the _key values for the nodes
        from_key = get_node_key(bgp, from_node)
        to_key = get_node_key(bgp, to_node)
        
        if not from_key or not to_key:
            print(f"Warning: Could not find keys for nodes {from_node} -> {to_node}")
            continue
        
        # Create unique edge key
        edge_key = f"{from_key}_{to_key}"
        
        # Create edge document
        edge = {
            '_key': edge_key,
            '_from': f'bgp_node/{from_key}',
            '_to': f'bgp_node/{to_key}',
            'link_type': 'ipv6'
        }
        
        try:
            # Use upsert to avoid duplicates
            aql = """
            UPSERT { _key: @edge_key }
            INSERT @edge
            UPDATE @edge
            IN ipv6_graph
            RETURN NEW
            """
            db.aql.execute(aql, bind_vars={'edge_key': edge_key, 'edge': edge})
            edges_created += 1
            
            if edges_created % 100 == 0:  # Progress update every 100 edges
                print(f"Created {edges_created} edges...")
                
        except Exception as e:
            print(f"Error creating edge {edge_key}: {str(e)}")
    
    print(f"\nFinished! Created {edges_created} edges in total")

if __name__ == "__main__":
    args = parse_args()
    
    # Setup database connections
    db, bgp, ipv6graph = setup_database()
    
    # Create graph definition if requested
    if args.create_graph:
        create_graph_definition(db)
    
    # Create edges from adjacency list
    create_edges(db, bgp, ipv6graph, args.file) 