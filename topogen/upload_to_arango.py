#!/usr/bin/env python3
"""
Upload PolarFly topology to ArangoDB

This script takes the JSON files containing vertices and edges of a PolarFly topology
and uploads them to an ArangoDB database, creating the necessary collections and graph.
"""

import argparse
import json
import sys
from arango import ArangoClient
from arango.exceptions import CollectionCreateError, GraphCreateError


def load_json_file(filename):
    """Load data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' is not valid JSON.")
        sys.exit(1)


def create_arango_graph(url, username, password, db_name, vertices_file, edges_file, 
                        graph_name="PolarFly", vertex_collection="nodes", edge_collection="edges"):
    """
    Create a graph in ArangoDB from PolarFly topology JSON files.
    
    Args:
        url (str): ArangoDB server URL (e.g., 'http://localhost:8529')
        username (str): ArangoDB username
        password (str): ArangoDB password
        db_name (str): Database name
        vertices_file (str): Path to the vertices JSON file
        edges_file (str): Path to the edges JSON file
        graph_name (str, optional): Name for the graph. Defaults to "PolarFly".
        vertex_collection (str, optional): Name for the vertex collection. Defaults to "nodes".
        edge_collection (str, optional): Name for the edge collection. Defaults to "edges".
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Load data from JSON files
    print(f"Loading vertices from {vertices_file}...")
    vertices = load_json_file(vertices_file)
    
    print(f"Loading edges from {edges_file}...")
    edges = load_json_file(edges_file)
    
    # Extract radix from edge data (assuming all edges have the same radix)
    if edges:
        # Extract radix from the first edge's _from field
        # Format: radix_{k}_node/node00
        radix_str = edges[0]["_from"].split("/")[0]
        radix = int(radix_str.split("_")[1])
        print(f"Detected radix (node degree): {radix}")
    else:
        print("Warning: No edges found in the edge file.")
        radix = 0
    
    # Connect to ArangoDB
    print(f"Connecting to ArangoDB at {url}...")
    client = ArangoClient(hosts=url)
    
    try:
        # Connect to the system database
        sys_db = client.db("_system", username=username, password=password)
        
        # Create the target database if it doesn't exist
        if not sys_db.has_database(db_name):
            print(f"Creating database '{db_name}'...")
            sys_db.create_database(db_name)
        
        # Connect to the target database
        db = client.db(db_name, username=username, password=password)
        
        # Create vertex collection if it doesn't exist
        if not db.has_collection(vertex_collection):
            print(f"Creating vertex collection '{vertex_collection}'...")
            db.create_collection(vertex_collection)
        
        # Create edge collection if it doesn't exist
        if not db.has_collection(edge_collection):
            print(f"Creating edge collection '{edge_collection}'...")
            db.create_collection(edge_collection, edge=True)
        
        # Get references to the collections
        nodes_collection = db.collection(vertex_collection)
        edges_collection = db.collection(edge_collection)
        
        # Create the graph if it doesn't exist
        graph_name_with_radix = f"{graph_name}_q{radix-1}"  # q = radix-1
        if not db.has_graph(graph_name_with_radix):
            print(f"Creating graph '{graph_name_with_radix}'...")
            graph = db.create_graph(
                graph_name_with_radix,
                edge_definitions=[
                    {
                        "edge_collection": edge_collection,
                        "from_vertex_collections": [vertex_collection],
                        "to_vertex_collections": [vertex_collection]
                    }
                ]
            )
        else:
            print(f"Graph '{graph_name_with_radix}' already exists.")
            graph = db.graph(graph_name_with_radix)
        
        # Import vertices
        print(f"Importing {len(vertices)} vertices...")
        # Truncate collection first to avoid duplicates
        nodes_collection.truncate()
        # Insert vertices in batches
        batch_size = 1000
        for i in range(0, len(vertices), batch_size):
            batch = vertices[i:i+batch_size]
            nodes_collection.import_bulk(batch, on_duplicate="replace")
        
        # Import edges
        print(f"Importing {len(edges)} edges...")
        # Truncate collection first to avoid duplicates
        edges_collection.truncate()
        # Insert edges in batches
        for i in range(0, len(edges), batch_size):
            batch = edges[i:i+batch_size]
            edges_collection.import_bulk(batch, on_duplicate="replace")
        
        print(f"Successfully created PolarFly graph with {len(vertices)} vertices and {len(edges)} edges.")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Upload PolarFly topology to ArangoDB')
    
    # Required arguments
    parser.add_argument('--url', required=True, help='ArangoDB server URL (e.g., http://localhost:8529)')
    parser.add_argument('--username', required=True, help='ArangoDB username')
    parser.add_argument('--password', required=True, help='ArangoDB password')
    parser.add_argument('--db', required=True, help='Database name')
    parser.add_argument('--vertices', required=True, help='Path to vertices JSON file')
    parser.add_argument('--edges', required=True, help='Path to edges JSON file')
    
    # Optional arguments
    parser.add_argument('--graph-name', default='PolarFly', help='Name for the graph (default: PolarFly)')
    parser.add_argument('--vertex-collection', default='nodes', help='Name for the vertex collection (default: nodes)')
    parser.add_argument('--edge-collection', default='edges', help='Name for the edge collection (default: edges)')
    
    args = parser.parse_args()
    
    success = create_arango_graph(
        args.url,
        args.username,
        args.password,
        args.db,
        args.vertices,
        args.edges,
        args.graph_name,
        args.vertex_collection,
        args.edge_collection
    )
    
    if success:
        print("Upload completed successfully.")
    else:
        print("Upload failed.")
        sys.exit(1)


if __name__ == "__main__":
    main() 