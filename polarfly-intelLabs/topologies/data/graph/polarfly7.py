import networkx as nx
from pyvis.network import Network
import ast

# Read the file and convert the string to a list of tuples
with open('graph7.txt', 'r') as f:
    edges = ast.literal_eval(f.read())

# Create graph from edge list
G = nx.Graph()
G.add_edges_from(edges)

# Apply circular layout to the graph
pos = nx.circular_layout(G)
# Convert positions to the format PyVis expects
for i, (x, y) in enumerate(pos.values()):
    # Scale the positions to make the circle larger
    # Multiply by a larger number (e.g., 500) to make the circle bigger
    G.nodes[i]['x'] = x * 500
    G.nodes[i]['y'] = y * 500

print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())

net = Network(notebook=True, height="900px", width="100%", bgcolor="#222222", font_color="white", select_menu=True, filter_menu=True)
net.repulsion()
net.cdn_resources='remote'
net.from_nx(G)
net.toggle_physics=(False)
net.set_options("""
{
    "nodes": {
        "label": null,
        "font": {
            "size": 4,
            "color": "white"
        }
    },
    "edges": {
        "color": {
            "inherit": true
        },
        "physics": false,
        "smooth": false,
        "width": 0.2
    },
    "physics": {
        "enabled": false,
        "solver": "repulsion"
    }
}
""")

#net.show("clean.html")
net.show("polarfly7.html")