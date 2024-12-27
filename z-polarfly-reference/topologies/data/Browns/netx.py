import networkx as nx

G = nx.read_edgelist('Brown.7.adj.txt', nodetype=int)

# Print the nodes and edges
print("Nodes:", G.nodes())
print("Edges:", G.edges())
