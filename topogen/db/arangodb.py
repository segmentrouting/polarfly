from arango import ArangoClient
import json
import argparse
import os

def connect_db(url='http://localhost:8529', dbname='_system', username='root', password=''):
    """Connect to ArangoDB and return database handle"""
    client = ArangoClient(hosts=url)
    db = client.db(dbname, username=username, password=password)
    return db

def create_collections(db, collection_name):
    """Create vertex and edge collections if they don't exist"""
    # Create vertex collection if it doesn't exist
    if not db.has_collection(collection_name):
        vertices = db.create_collection(collection_name)
    else:
        vertices = db.collection(collection_name)

    # Create edge collection with radix_X_graph name
    graph_name = collection_name.replace('_node', '_graph')
    if not db.has_collection(graph_name):
        edges = db.create_collection(graph_name, edge=True)
    else:
        edges = db.collection(graph_name)

    return vertices, edges

def create_graph(db, collection_name):
    """Create a named graph if it doesn't exist"""
    graph_name = collection_name.replace('_node', '_graph')
    if not db.has_graph(graph_name):
        graph = db.create_graph(graph_name)
        # Define the edge definition
        graph.create_edge_definition(
            edge_collection=graph_name,
            from_vertex_collections=[collection_name],
            to_vertex_collections=[collection_name]
        )
    else:
        graph = db.graph(graph_name)
    return graph

def import_vertices(vertices_collection, vertices_file):
    """Import vertices from JSON file"""
    with open(vertices_file, 'r') as f:
        vertices = json.load(f)
    
    # Import vertices in batches
    batch_size = 1000
    for i in range(0, len(vertices), batch_size):
        batch = vertices[i:i + batch_size]
        vertices_collection.import_bulk(batch)
    
    print(f"Imported {len(vertices)} vertices")

def import_edges(edges_collection, edges_file):
    """Import edges from JSON file"""
    with open(edges_file, 'r') as f:
        edges = json.load(f)
    
    # Import edges in batches
    batch_size = 1000
    for i in range(0, len(edges), batch_size):
        batch = edges[i:i + batch_size]
        edges_collection.import_bulk(batch)
    
    print(f"Imported {len(edges)} edges")

def parse_args():
    parser = argparse.ArgumentParser(description='Import graph data into ArangoDB')
    parser.add_argument('-p', '--path', required=True,
                       help='Path to directory containing vertices.json and edges.json')
    parser.add_argument('--url', default='http://localhost:8529',
                       help='ArangoDB URL (default: http://localhost:8529)')
    parser.add_argument('--dbname', default='_system',
                       help='Database name (default: _system)')
    parser.add_argument('--username', default='root',
                       help='Database username (default: root)')
    parser.add_argument('--password', default='',
                       help='Database password (default: empty)')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Verify directory exists and contains required files
    if not os.path.exists(args.path):
        raise FileNotFoundError(f"Directory not found: {args.path}")
        
    vertices_file = os.path.join(args.path, 'vertices.json')
    edges_file = os.path.join(args.path, 'edges.json')
    
    if not os.path.exists(vertices_file):
        raise FileNotFoundError(f"Vertices file not found: {vertices_file}")
    if not os.path.exists(edges_file):
        raise FileNotFoundError(f"Edges file not found: {edges_file}")
    
    # Extract radix number and create valid collection names
    dir_name = os.path.basename(args.path).strip('/')  # Remove any trailing slash
    try:
        # Handle both "radix_8" and just "8" formats
        if '_' in dir_name:
            radix_num = dir_name.split('_')[-1]  # Get last part after underscore
        else:
            radix_num = dir_name  # Assume the directory name is just the number
            
        collection_name = f"radix_{radix_num}_node"
    except Exception as e:
        print(f"Error parsing directory name '{dir_name}': {e}")
        return
    
    # Print collection names for debugging
    print(f"Creating collections with names:")
    print(f"  Vertex collection: {collection_name}")
    print(f"  Edge collection: {collection_name.replace('_node', '_graph')}")
    
    # Connect to database
    try:
        db = connect_db(args.url, args.dbname, args.username, args.password)
        print(f"Connected to ArangoDB at {args.url}")
    except Exception as e:
        print(f"Failed to connect to ArangoDB: {e}")
        return
    
    try:
        # Create collections
        vertices, edges = create_collections(db, collection_name)
        print(f"Created/accessed collections: {collection_name}, {collection_name.replace('_node', '_graph')}")
        
        # Create graph
        graph = create_graph(db, collection_name)
        print(f"Created/accessed graph: {collection_name.replace('_node', '_graph')}")
        
        # Import data
        import_vertices(vertices, vertices_file)
        import_edges(edges, edges_file)
        
        print("Graph import completed successfully")
        
    except Exception as e:
        print(f"Error during import: {e}")
        if hasattr(e, 'http_code') and hasattr(e, 'error_code'):
            print(f"HTTP Code: {e.http_code}")
            print(f"Error Code: {e.error_code}")
            print(f"Error Message: {e.error_message}")

if __name__ == "__main__":
    main() 