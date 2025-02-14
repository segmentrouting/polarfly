from arango import ArangoClient
import json
import argparse
import os

def connect_db(url='http://localhost:8529', dbname='_system', username='root', password=''):
    """Connect to ArangoDB and return database handle"""
    client = ArangoClient(hosts=url)
    db = client.db(dbname, username=username, password=password)
    return db

def create_collections(db, graph_name):
    """Create vertex and edge collections if they don't exist"""
    # Create vertices collection if it doesn't exist
    if not db.has_collection('vertices'):
        vertices = db.create_collection('vertices')
    else:
        vertices = db.collection('vertices')

    # Create edge collection with same name as graph
    if not db.has_collection(graph_name):
        edges = db.create_collection(graph_name, edge=True)
    else:
        edges = db.collection(graph_name)

    return vertices, edges

def create_graph(db, graph_name):
    """Create a named graph if it doesn't exist"""
    if not db.has_graph(graph_name):
        graph = db.create_graph(graph_name)
        # Define the edge definition using graph name as edge collection
        graph.create_edge_definition(
            edge_collection=graph_name,
            from_vertex_collections=['vertices'],
            to_vertex_collections=['vertices']
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
    parser.add_argument('-v', '--vertices', required=True,
                       help='Input vertices JSON file')
    parser.add_argument('-e', '--edges', required=True,
                       help='Input edges JSON file')
    parser.add_argument('-g', '--graph-name', required=True,
                       help='Name of the graph to create in ArangoDB')
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
    
    # Verify input files exist
    if not os.path.exists(args.vertices):
        raise FileNotFoundError(f"Vertices file not found: {args.vertices}")
    if not os.path.exists(args.edges):
        raise FileNotFoundError(f"Edges file not found: {args.edges}")
    
    # Connect to database
    try:
        db = connect_db(args.url, args.dbname, args.username, args.password)
        print(f"Connected to ArangoDB at {args.url}")
    except Exception as e:
        print(f"Failed to connect to ArangoDB: {e}")
        return
    
    try:
        # Create collections
        vertices, edges = create_collections(db, args.graph_name)
        print(f"Created/accessed collections: vertices, {args.graph_name}")
        
        # Create graph
        graph = create_graph(db, args.graph_name)
        print(f"Created/accessed graph: {args.graph_name}")
        
        # Import data
        import_vertices(vertices, args.vertices)
        import_edges(edges, args.edges)
        
        print("Graph import completed successfully")
        
    except Exception as e:
        print(f"Error during import: {e}")

if __name__ == "__main__":
    main() 