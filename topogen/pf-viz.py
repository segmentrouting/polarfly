# PolarFly Topology Constructor and Visualizer
# Christian Martin
# Feb 2025

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
from sympy.ntheory import isprime
from itertools import combinations
import argparse
import json  # Added for JSON export

class PolarFly:
    """
    PolarFly network topology implementation based on the Erdős-Rényi polarity graph of PG(2,q).
    
    The construction relies on projective geometry over finite fields, where:
    - Points in the projective plane PG(2,q) correspond to 1-dimensional subspaces of GF(q)³
    - Each point is represented by a non-zero vector (x,y,z) with components in GF(q)
    - Orthogonal vectors (dot product = 0 in GF(q)) determine the network connections
    
    PolarFly has optimal scaling properties with diameter 2 and exhibits a unique 3-part structure:
    - Quadrics: Self-orthogonal vectors forming the W(q) set
    - V1: Vertices adjacent to exactly one quadric (V₁(q) set)
    - V2: Vertices adjacent to no quadrics (V₂(q) set)
    
    The network has N = q² + q + 1 nodes with uniform degree k = q + 1.
    
    Attributes:
        q (int): The prime or prime power parameter that determines network size
        N (int): Total number of vertices (q² + q + 1)
        k (int): Degree of each vertex, also called radix (q + 1)
        G (nx.Graph): NetworkX graph representation of the PolarFly topology
        quadrics (list): Vertices in the W(q) set (self-orthogonal vectors)
        v1 (list): Vertices in the V₁(q) set (adjacent to exactly one quadric)
        v2 (list): Vertices in the V₂(q) set (not adjacent to any quadric)
        layout (dict): Spatial coordinates for visualization
    """
    
    def __init__(self, q):
        """
        Initialize PolarFly with parameter q.
        
        Args:
            q (int): The prime or prime power parameter that determines network size.
                   Must be a prime number for this implementation. Prime powers require
                   additional finite field arithmetic that is not implemented here.
        
        Raises:
            ValueError: If q is not a prime number
        """
        # Check if q is prime
        if not isprime(q):
            # Note: For full implementation, we'd need to check for prime powers as well
            # but that's more complex and beyond the scope of this implementation
            raise ValueError("q must be a prime number (or prime power for full implementation)")
        
        self.q = q
        self.N = q**2 + q + 1  # Total number of vertices in the graph (Theorem 1)
        self.k = q + 1  # Degree of each vertex (radix) (Theorem 1)
        
        # Generate the graph
        self.G = self._generate_er_graph()
        
        # Partition vertices into W(q), V1(q), and V2(q)
        self.quadrics, self.v1, self.v2 = self._partition_vertices()
        
        # Create the layout for visualization
        self.layout = self._create_layout()
    
    def _generate_er_graph(self):
        """
        Generate the Erdős-Rényi polarity graph of PG(2,q).
        
        This method:
        1. Generates all non-zero vectors (x,y,z) with components in GF(q)
        2. Normalizes vectors to get unique representatives of projective points
        3. Creates a node for each projective point (1D subspace)
        4. Connects nodes whose corresponding vectors are orthogonal (dot product = 0 in GF(q))
        
        The resulting graph represents the Erdős-Rényi polarity graph, where:
        - Vertices correspond to points in PG(2,q)
        - Two vertices are connected if their corresponding vectors are orthogonal
        
        Returns:
            nx.Graph: The Erdős-Rényi polarity graph
        """
        G = nx.Graph()
        
        # Add vertices as left-normalized vectors in F^3_q
        vectors = []
        
        # Generate all non-zero left-normalized vectors in F^3_q
        # Left-normalization means the first non-zero element is 1,
        # which ensures we get exactly one vector per projective point
        for x in range(self.q):
            for y in range(self.q):
                for z in range(self.q):
                    if x == 0 and y == 0 and z == 0:
                        continue  # Skip zero vector
                    
                    # Left normalize: ensure first non-zero coordinate is 1
                    # This implements the equivalence relation for projective spaces
                    # where (x,y,z) ~ (λx,λy,λz) for any non-zero λ in GF(q)
                    if x != 0:
                        # Calculate x⁻¹ mod q using Fermat's Little Theorem
                        # For prime q, x⁻¹ ≡ x^(q-2) (mod q)
                        vectors.append((1, (y * pow(x, -1, self.q)) % self.q, (z * pow(x, -1, self.q)) % self.q))
                    elif y != 0:
                        vectors.append((0, 1, (z * pow(y, -1, self.q)) % self.q))
                    else:  # z != 0
                        vectors.append((0, 0, 1))
        
        # Remove duplicates
        vectors = list(set(vectors))
        
        # Add vertices to graph
        for i, v in enumerate(vectors):
            G.add_node(i, vector=v)
        
        # Add edges between orthogonal vectors
        for i, j in combinations(range(len(vectors)), 2):
            v1 = G.nodes[i]['vector']
            v2 = G.nodes[j]['vector']
            
            # Calculate dot product in F_q
            # Two vectors are orthogonal if v1·v2 = 0 in GF(q)
            dot_product = (v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]) % self.q
            
            if dot_product == 0:
                G.add_edge(i, j)
        
        return G
    
    def _partition_vertices(self):
        """
        Partition vertices into W(q) (quadrics), V1(q), and V2(q) as defined in the paper.
        
        This implements the fundamental PolarFly network structure:
        
        1. W(q) (quadrics): Vertices that are self-orthogonal
           - These are vectors v where v·v = 0 in GF(q)
           - In projective geometry, these correspond to points on the quadric
        
        2. V1(q): Vertices adjacent to exactly one quadric
           - These form connections between different clusters
        
        3. V2(q): Vertices not adjacent to any quadric
           - These are contained entirely within their local neighborhoods
        
        This partitioning is used for both analysis and visualization of the PolarFly network.
        
        Returns:
            tuple: Lists of quadrics, V1, and V2 vertices
        """
        quadrics = []
        v1 = []
        v2 = []
        
        # Find quadrics (self-orthogonal vectors)
        for i in self.G.nodes():
            v = self.G.nodes[i]['vector']
            
            # Check if self-orthogonal: v·v = 0 in GF(q)
            # This identifies all point on the fundamental quadric in PG(2,q)
            dot_product = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) % self.q
            
            if dot_product == 0:
                quadrics.append(i)
        
        # Find V1(q) (vertices adjacent to quadrics)
        v1_set = set()
        for q_vertex in quadrics:
            v1_set.update(self.G.neighbors(q_vertex))
        v1 = list(v1_set)
        
        # V2(q) are all remaining vertices
        v2 = [v for v in self.G.nodes() if v not in quadrics and v not in v1]
        
        return quadrics, v1, v2
    
    def _create_layout(self):
        """
        Create a layout for basic visualization in cylindrical form.
        
        The layout places:
        - Quadrics (W(q)) at the top level (z=2.0) in a circular arrangement
        - V1 vertices in the middle level (z=1.0) in a larger circle
        - V2 vertices at the bottom level (z=0.0) in a similar circle
        
        This basic layout provides a clear visual separation of the three vertex sets,
        but doesn't capture the cluster structure used in the more advanced visualizations.
        
        Returns:
            dict: Mapping of node indices to 3D coordinates (x,y,z)
        """
        layout = {}
        
        # Place quadrics on the top in a circle
        n_quadrics = len(self.quadrics)
        radius_top = 1.0
        
        for i, node in enumerate(self.quadrics):
            theta = 2 * np.pi * i / n_quadrics
            layout[node] = (radius_top * np.cos(theta), radius_top * np.sin(theta), 2.0)
        
        # Place V1 in the middle in a circle
        n_v1 = len(self.v1)
        radius_middle = 1.5
        
        for i, node in enumerate(self.v1):
            theta = 2 * np.pi * i / n_v1
            layout[node] = (radius_middle * np.cos(theta), radius_middle * np.sin(theta), 1.0)
        
        # Place V2 on the bottom in a circle
        n_v2 = len(self.v2)
        radius_bottom = 1.5
        
        for i, node in enumerate(self.v2):
            theta = 2 * np.pi * i / n_v2
            layout[node] = (radius_bottom * np.cos(theta), radius_bottom * np.sin(theta), 0.0)
        
        return layout
    
    def visualize(self):
        """
        Visualize the PolarFly network in 3D, using the basic layered layout.
        
        This visualization:
        - Places quadrics (red) at the top level
        - Places V1 nodes (green) in the middle level
        - Places V2 nodes (blue) at the bottom level
        - Shows connections between nodes with varying colors and transparencies
        - Displays node labels (00, 01, 02, etc.)
        
        The method produces both a 3D view and a 2D overhead projection.
        
        This simple visualization is useful for understanding the general structure
        but doesn't capture the clustering properties shown in the more advanced layouts.
        """
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Format width for node labels
        width = len(str(self.N - 1))
        
        # Plot nodes
        for node in self.G.nodes():
            x, y, z = self.layout[node]
            
            if node in self.quadrics:
                color = 'red'
                size = 100  # Increased size
            elif node in self.v1:
                color = 'green'
                size = 80   # Increased size
            else:  # node in self.v2
                color = 'blue'
                size = 80   # Increased size
                
            ax.scatter(x, y, z, c=color, s=size, edgecolors='black')
            
            # Add node label with proper formatting - position slightly above the node
            label = str(node).zfill(width)  # Simple zero-padding approach
            ax.text(x, y, z + 0.2, label, size=10, zorder=10, ha='center', va='center',  # Position above node
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='black', pad=2))  # Added border
        
        # Plot edges
        for u, v in self.G.edges():
            x1, y1, z1 = self.layout[u]
            x2, y2, z2 = self.layout[v]
            
            # Determine edge color based on node types
            if u in self.quadrics or v in self.quadrics:
                color = 'red'
                alpha = 0.6
                width = 1.5  # Slightly thicker
            else:
                color = 'black'
                alpha = 0.3  # Slightly more visible
                width = 0.8  # Slightly thicker
                
            ax.plot([x1, x2], [y1, y2], [z1, z2], c=color, alpha=alpha, linewidth=width)
        
        # Set plot properties
        ax.set_title(f'PolarFly (q={self.q}, N={self.N}, k={self.k})', fontsize=16)
        ax.set_axis_off()
        
        # Set viewpoint
        ax.view_init(elev=20, azim=30)
        
        plt.tight_layout()
        plt.show()
        
        # Also create an overhead view
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)
        
        # Plot nodes
        for node in self.G.nodes():
            x, y, z = self.layout[node]
            
            if node in self.quadrics:
                color = 'red'
                size = 100  # Increased size
            elif node in self.v1:
                color = 'green'
                size = 80   # Increased size
            else:  # node in self.v2
                color = 'blue'
                size = 80   # Increased size
                
            ax.scatter(x, y, c=color, s=size, edgecolors='black')
            
            # Add node label with proper formatting - position slightly below the node
            # label = str(node).zfill(width)  # Simple zero-padding approach
            # ax.text(x, y - 0.2, label, size=10, zorder=10, ha='center', va='center',  # Position below node
            #         bbox=dict(facecolor='white', alpha=0.7, edgecolor='black', pad=2))  # Added border
        
        # Plot edges
        for u, v in self.G.edges():
            x1, y1, z1 = self.layout[u]
            x2, y2, z2 = self.layout[v]
            
            # Determine edge color based on node types
            if u in self.quadrics or v in self.quadrics:
                color = 'red'
                alpha = 0.6
                width = 1.5  # Slightly thicker
            else:
                color = 'black'
                alpha = 0.3  # Slightly more visible
                width = 0.8  # Slightly thicker
                
            ax.plot([x1, x2], [y1, y2], c=color, alpha=alpha, linewidth=width)
        
        # Set plot properties
        ax.set_title(f'PolarFly Overhead View (q={self.q})', fontsize=16)
        ax.set_axis_off()
        
        plt.tight_layout()
        plt.show()

    def visualize_cluster_layout(self, highlight_cluster=None):
        """
        Visualize PolarFly with the cluster layout as described in Algorithm 1 of the paper.
        
        This visualization highlights the natural clustering of PolarFly:
        - Cluster C₀: All quadrics (W(q))
        - Clusters C₁...C_q: Each centered around a V1 node adjacent to the starter quadric
        
        Within each cluster:
        - A V1 node serves as the cluster center
        - V1 and V2 nodes in the cluster form triangular structures with the center
        - The V1 nodes fan out radially from the cluster center
        - V2 nodes are positioned directly below their connected V1 nodes
        
        Args:
            highlight_cluster (int, optional): 
                Index of cluster to highlight (0 for quadrics, 1-q for others).
                When a cluster is highlighted, other clusters are dimmed.
        """
        fig = plt.figure(figsize=(14, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw the cluster layout
        self._draw_cluster_layout(ax, highlight_cluster)
        
        plt.tight_layout()
        plt.show()

    def visualize_interactive_pyplot(self):
        """
        Create an interactive visualization of the PolarFly graph with cluster selection.
        
        This method provides:
        1. Radio buttons to select which cluster to highlight
        2. Rotation controls to manipulate the 3D view
        3. Real-time updates when cluster selection changes
        4. Toggle button to show/hide node labels
        
        The visualization preserves the 3D view angles when changing the highlighted cluster,
        allowing for consistent exploration of the graph structure from different perspectives.
        
        This is particularly useful for studying:
        - The relationship between different clusters
        - How quadrics connect to other clusters
        - The triangular structures within each cluster
        """
        import matplotlib.pyplot as plt
        from matplotlib.widgets import RadioButtons, Button, CheckButtons
        
        # First create a figure that will persist
        fig = plt.figure(figsize=(14, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Set up radio buttons for cluster selection
        cluster_labels = ['None'] + [f'Cluster {i}' for i in range(self.q + 1)]
        radio_ax = plt.axes([0.02, 0.8, 0.12, 0.15], facecolor='lightgoldenrodyellow')
        radio = RadioButtons(radio_ax, cluster_labels)
        
        # Dictionary to store plot elements for faster redrawing
        plots = {'nodes': None, 'edges': None, 'current_highlight': None, 'show_labels': True}
        
        # Add checkbox for toggling labels
        check_ax = plt.axes([0.02, 0.45, 0.12, 0.03], facecolor='lightgoldenrodyellow')
        check = CheckButtons(check_ax, ['Show Labels'], [True])
        
        def update_view(label=None, show_labels=None):
            # Clear previous plot
            ax.clear()
            
            # Convert label to highlight_cluster value if provided
            if label is not None:
                if label == 'None':
                    highlight_cluster = None
                else:
                    highlight_cluster = int(label.split()[1])
                plots['current_highlight'] = highlight_cluster
            else:
                highlight_cluster = plots['current_highlight']
            
            # Update show_labels if provided
            if show_labels is not None:
                plots['show_labels'] = show_labels
            
            # Store current view angles
            elev, azim = ax.elev, ax.azim
            
            # Draw the new visualization
            self._draw_cluster_layout(ax, highlight_cluster, show_labels=plots['show_labels'])
            
            # Restore view angles
            ax.view_init(elev=elev, azim=azim)
            
            plt.draw()
        
        def on_label_toggle(label):
            update_view(show_labels=check.get_status()[0])
        
        # Initial draw
        self._draw_cluster_layout(ax, None, show_labels=True)
        
        # Connect the radio buttons to the update function
        radio.on_clicked(update_view)
        
        # Connect the checkbox to the toggle function
        check.on_clicked(on_label_toggle)
        
        # Add rotation buttons for better 3D control
        rotation_ax = plt.axes([0.02, 0.65, 0.12, 0.1], facecolor='lightgoldenrodyellow')
        rotation_buttons = {}
        
        def rotate_view(direction):
            current_elev, current_azim = ax.elev, ax.azim
            
            if direction == 'Up':
                ax.view_init(elev=current_elev + 10, azim=current_azim)
            elif direction == 'Down':
                ax.view_init(elev=current_elev - 10, azim=current_azim)
            elif direction == 'Left':
                ax.view_init(elev=current_elev, azim=current_azim + 10)
            elif direction == 'Right':
                ax.view_init(elev=current_elev, azim=current_azim - 10)
            elif direction == 'Reset':
                ax.view_init(elev=20, azim=30)
            
            plt.draw()
        
        # Add buttons for controlling the view
        button_labels = ['Up', 'Down', 'Left', 'Right', 'Reset']
        button_positions = [(0.02, 0.61), (0.02, 0.57), (0.02, 0.53), (0.06, 0.53), (0.04, 0.49)]
        button_width, button_height = 0.04, 0.03
        
        for label, pos in zip(button_labels, button_positions):
            button_ax = plt.axes([pos[0], pos[1], button_width, button_height])
            btn = Button(button_ax, label)
            btn.on_clicked(lambda event, dir=label: rotate_view(dir))
            rotation_buttons[label] = btn
        
        plt.subplots_adjust(left=0.15)  # Make room for the controls
        plt.show()

    def _draw_cluster_layout(self, ax, highlight_cluster=None, show_labels=True):
        """
        Helper method to draw the PolarFly with optimized cylindrical cluster layout.
        
        This method implements the more sophisticated visualization approach:
        - Uses a cylindrical layout with fixed radii from the central axis
        - Places all V1 nodes at z=1.0 and all V2 nodes at z=0.0
        - Positions V1-V2 pairs in vertical alignment to highlight the V1-V2 connections
        - Scales the angular spread based on q to prevent crowding in larger graphs
        - Displays node labels (00, 01, 02, etc.) if show_labels is True
        
        Args:
            ax (matplotlib.axes.Axes): The 3D axis to draw on
            highlight_cluster (int, optional): Index of cluster to highlight
            show_labels (bool, optional): Whether to show node labels
        """
        # Choose an arbitrary quadric as the starter for Algorithm 1
        starter_quadric = self.quadrics[0]
        
        # Create clusters
        clusters = [[] for _ in range(self.q + 1)]
        
        # Add all quadrics to C0
        clusters[0] = self.quadrics.copy()
        
        # For each vertex adjacent to the starter quadric
        for i, neighbor in enumerate(self.G.neighbors(starter_quadric)):
            if i >= self.q:  # Cap at q clusters
                break
                
            # Add neighbor to cluster as the center
            clusters[i+1].append(neighbor)
            
            # Add all non-quadric neighbors of the neighbor to the same cluster
            for nn in self.G.neighbors(neighbor):
                if nn not in self.quadrics and nn != neighbor:
                    clusters[i+1].append(nn)
        
        # Create a new layout based on clusters
        cluster_layout = {}
        
        # Layout for quadrics cluster (C0) - place in a circle at the top
        n_quadrics = len(clusters[0])
        for i, node in enumerate(clusters[0]):
            theta = 2 * np.pi * i / n_quadrics
            r = 1.0
            cluster_layout[node] = (r * np.cos(theta), r * np.sin(theta), 2.0)
        
        # Fixed radius from central axis for all V1 and V2 nodes
        fixed_v1_radius = 3.5  # Distance from central axis for all V1 nodes
        
        # Layout for non-quadric clusters (C1 to Cq) in a cylindrical arrangement
        for cluster_idx in range(1, self.q + 1):
            if not clusters[cluster_idx]:  # Skip empty clusters
                continue
                
            # Find the center of the cluster (should be the first element)
            center = clusters[cluster_idx][0]
            
            # Place center at a fixed position around a circle
            angle = 2 * np.pi * (cluster_idx - 1) / self.q
            r_center = 3.0  # Radius for cluster centers
            cluster_layout[center] = (r_center * np.cos(angle), r_center * np.sin(angle), 1.0)
            
            # Sort remaining nodes by whether they're in V1 or V2
            v1_nodes = [n for n in clusters[cluster_idx][1:] if n in self.v1]
            v2_nodes = [n for n in clusters[cluster_idx][1:] if n in self.v2]
            
            # Find V1-V2 connections within this cluster that form triangles with the center
            v1_v2_pairs = []
            for v1_node in v1_nodes:
                connected_v2 = [v2 for v2 in v2_nodes if self.G.has_edge(v1_node, v2)]
                for v2_node in connected_v2:
                    if self.G.has_edge(v2_node, center):  # Forms a triangle
                        v1_v2_pairs.append((v1_node, v2_node))
            
            # Track which nodes are already placed in V1-V2 pairs
            used_v1 = {v1 for v1, _ in v1_v2_pairs}
            used_v2 = {v2 for _, v2 in v1_v2_pairs}
            remaining_v1 = [v for v in v1_nodes if v not in used_v1]
            remaining_v2 = [v for v in v2_nodes if v not in used_v2]
            
            # Calculate the angle spread for this cluster's nodes
            total_nodes = len(v1_v2_pairs) + len(remaining_v1)
            if total_nodes == 0:
                continue
                
            # Determine the angular spread for this cluster's nodes
            # Adjust spread based on q to prevent crowding in larger graphs
            spread_angle = 0.8 * (2 * np.pi / self.q)  # Use 80% of available angular space
            
            # Position the triangular arrangements first
            for i, (v1_node, v2_node) in enumerate(v1_v2_pairs):
                # Calculate angle offset from the cluster center angle
                if total_nodes > 1:
                    offset = spread_angle * (i / (total_nodes - 1) - 0.5)
                else:
                    offset = 0
                    
                # The actual angle for this node
                node_angle = angle + offset
                
                # Place V1 node at fixed radius from central axis
                x1 = fixed_v1_radius * np.cos(node_angle)
                y1 = fixed_v1_radius * np.sin(node_angle)
                cluster_layout[v1_node] = (x1, y1, 1.0)
                
                # Place V2 node directly below V1 (creates a vertical connection)
                cluster_layout[v2_node] = (x1, y1, 0.0)
            
            # Place any remaining V1 nodes in their own radial positions
            for i, v1_node in enumerate(remaining_v1):
                # Calculate angle offset
                offset_index = len(v1_v2_pairs) + i
                if total_nodes > 1:
                    offset = spread_angle * (offset_index / (total_nodes - 1) - 0.5)
                else:
                    offset = 0
                    
                # The actual angle for this node
                node_angle = angle + offset
                
                # Place V1 node at fixed radius from central axis
                x = fixed_v1_radius * np.cos(node_angle)
                y = fixed_v1_radius * np.sin(node_angle)
                cluster_layout[v1_node] = (x, y, 1.0)
            
            # Place any remaining V2 nodes in a similar pattern, slightly offset
            for i, v2_node in enumerate(remaining_v2):
                if len(remaining_v2) > 1:
                    offset = spread_angle * (i / (len(remaining_v2) - 1) - 0.5) * 0.7  # narrower spread
                else:
                    offset = 0
                    
                # The actual angle for this node, slightly offset from the cluster center
                node_angle = angle + offset
                
                # Place V2 node at fixed radius from central axis, but at Z=0
                x = fixed_v1_radius * np.cos(node_angle)
                y = fixed_v1_radius * np.sin(node_angle)
                cluster_layout[v2_node] = (x, y, 0.0)
        
        # Create a mapping from node to cluster for edge/node styling
        node_to_cluster = {}
        for cluster_idx, cluster_nodes in enumerate(clusters):
            for node in cluster_nodes:
                node_to_cluster[node] = cluster_idx
        
        # Format width for node labels - ensure it's an integer
        label_width = int(len(str(self.N - 1)))
        
        # Plot all edges first (so they're behind nodes)
        for u, v in self.G.edges():
            if u not in cluster_layout or v not in cluster_layout:
                continue
                
            x1, y1, z1 = cluster_layout[u]
            x2, y2, z2 = cluster_layout[v]
            
            # Find which clusters u and v belong to
            u_cluster = node_to_cluster.get(u, None)
            v_cluster = node_to_cluster.get(v, None)
            
            # Initialize default values
            color = 'black'
            alpha = 0.5
            line_width = 0.5
            
            # Determine edge styling based on highlighting and connection type
            if highlight_cluster is not None:
                if u_cluster == highlight_cluster and v_cluster == highlight_cluster:
                    # Intra-cluster edge within highlighted cluster
                    color = 'green'  # Visible green color for intra-cluster edges
                    alpha = 1.0
                    line_width = 2.0
                elif (u_cluster == highlight_cluster or v_cluster == highlight_cluster):
                    if u_cluster == 0 or v_cluster == 0:
                        # Edge to a quadric from highlighted cluster
                        color = 'red'
                        alpha = 0.7
                        line_width = 1.5
                    else:
                        # Inter-cluster edge connected to highlighted cluster
                        color = 'blue'  # Blue for inter-cluster connections
                        alpha = 0.5
                        line_width = 0.5
                else:
                    # Edge not connected to highlighted cluster - very subtle
                    color = '#aaaaaa'  # Very light gray
                    alpha = 0.3        # Very transparent
            else:
                # No highlighting - show all edges normally
                if u_cluster == 0 or v_cluster == 0:
                    # Edge to a quadric
                    color = 'red'
                    alpha = 0.4
                    line_width = 1
                elif u_cluster == v_cluster:
                    # Intra-cluster edge
                    color = 'black'
                    alpha = 0.7
                    line_width = 1.0
                else:
                    # Inter-cluster edge (non-quadric)
                    color = 'blue'
                    alpha = 0.5
                    line_width = 0.8
                    
            ax.plot([x1, x2], [y1, y2], [z1, z2], c=color, alpha=alpha, linewidth=line_width)
        
        # Plot all nodes
        for node in self.G.nodes():
            if node not in cluster_layout:
                continue
                
            x, y, z = cluster_layout[node]
            
            # Find which cluster this node belongs to
            node_cluster = node_to_cluster.get(node, None)
            
            # Determine node styling based on highlighting and node type
            if highlight_cluster is not None:
                if node_cluster == highlight_cluster:
                    # Node is in highlighted cluster
                    if node == clusters[node_cluster][0] and node_cluster > 0:
                        # Highlighted center
                        color = 'blue'  # Cluster center in blue
                        size = 100
                        edgecolor = 'black'
                        zorder = 10
                    elif node in self.quadrics:
                        # Highlighted quadric
                        color = 'orange'
                        size = 70
                        edgecolor = 'black'
                        zorder = 9
                    else:
                        # Other highlighted node
                        color = 'green'  # Regular nodes in green
                        size = 50
                        edgecolor = 'black'
                        zorder = 8
                else:
                    # Node is not in highlighted cluster - very subtle
                    if node in self.quadrics:
                        color = '#aaaaaa'  # Very light gray
                        size = 25
                        edgecolor = '#777777'  # Lighter edge color
                        zorder = 3
                    elif node in [clusters[c][0] for c in range(1, self.q + 1) if clusters[c]]:
                        # Cluster centers
                        color = '#aaaaaa'  # Very light gray
                        size = 35
                        edgecolor = '#777777'  # Lighter edge color
                        zorder = 3
                    else:
                        color = '#aaaaaa'  # Very light gray
                        size = 20
                        edgecolor = '#777777'  # Lighter edge color
                        zorder = 2
            else:
                # Regular node styling (no highlighting)
                if node in self.quadrics:
                    color = 'red'
                    size = 50
                    edgecolor = 'black'
                    zorder = 7
                elif node in [cluster[0] for cluster in clusters[1:] if cluster]:
                    # Cluster centers
                    color = 'lightyellow'
                    size = 60
                    edgecolor = 'black'
                    zorder = 6
                elif node in self.v1:
                    color = 'green'
                    size = 30
                    edgecolor = 'black'
                    zorder = 5
                else:  # node in self.v2
                    color = 'blue'
                    size = 30
                    edgecolor = 'black'
                    zorder = 4
                    
            ax.scatter(x, y, z, c=color, s=size, edgecolors=edgecolor, zorder=zorder)
            
            # Add node label if show_labels is True
            if show_labels:
                show_this_label = True
                if highlight_cluster is not None and node_cluster != highlight_cluster:
                    # For non-highlighted clusters, only show labels for important nodes
                    if not (node in self.quadrics or node in [clusters[c][0] for c in range(1, self.q + 1) if clusters[c]]):
                        show_this_label = False
                
                if show_this_label:
                    # Convert node to string and pad with zeros
                    label = str(node).zfill(label_width)
                    # Adjust text color for better contrast
                    text_color = 'black' if color in ['yellow', 'lightyellow', 'orange', 'green'] else 'white'
                    # Position label above the node
                    ax.text(x, y, z + 0.2, label, size=10, zorder=zorder+1, ha='center', va='center', color=text_color,
                            bbox=dict(facecolor='black' if text_color == 'white' else 'white', 
                                     alpha=0.7, edgecolor='gray', pad=2))
        
        # Set plot properties
        if highlight_cluster is not None:
            if highlight_cluster == 0:
                title = f'PolarFly Cluster Layout - Highlighting Quadrics Cluster (q={self.q})'
            else:
                title = f'PolarFly Cluster Layout - Highlighting Cluster {highlight_cluster} (q={self.q})'
        else:
            title = f'PolarFly Cluster Layout (q={self.q}, N={self.N}, k={self.k})'
        
        ax.set_title(title, fontsize=16)
        ax.set_axis_off()
        
        # Set default viewpoint if not already set
        if not ax.elev and not ax.azim:
            ax.view_init(elev=20, azim=30)

    def print_node_connections(self):
        """
        Print a detailed list of all nodes in the PolarFly topology, including:
        - Node ID
        - Node role (quadric, V1 center, V1 peripheral, or V2)
        - Cluster membership
        - Vector representation
        - List of connected nodes
        
        This provides a textual representation of the network that complements
        the visual representation, making it easier to analyze specific node
        relationships and connectivity patterns.
        """
        # Format node IDs with leading zeros for better readability
        width = len(str(self.N - 1))
        
        # First, identify clusters and node roles
        # Choose an arbitrary quadric as the starter for Algorithm 1
        starter_quadric = self.quadrics[0]
        
        # Create clusters
        clusters = [[] for _ in range(self.q + 1)]
        
        # Add all quadrics to C0
        clusters[0] = self.quadrics.copy()
        
        # For each vertex adjacent to the starter quadric
        for i, neighbor in enumerate(self.G.neighbors(starter_quadric)):
            if i >= self.q:  # Cap at q clusters
                break
                
            # Add neighbor to cluster as the center
            clusters[i+1].append(neighbor)
            
            # Add all non-quadric neighbors of the neighbor to the same cluster
            for nn in self.G.neighbors(neighbor):
                if nn not in self.quadrics and nn != neighbor:
                    clusters[i+1].append(nn)
        
        # Create a mapping from node to cluster and role
        node_to_cluster = {}
        node_to_role = {}
        
        # Assign quadrics to cluster 0
        for node in self.quadrics:
            node_to_cluster[node] = 0
            node_to_role[node] = "Quadric"
        
        # Assign V1 and V2 nodes to their clusters
        for cluster_idx in range(1, self.q + 1):
            if not clusters[cluster_idx]:  # Skip empty clusters
                continue
                
            # First node in cluster is the V1 center
            center = clusters[cluster_idx][0]
            node_to_cluster[center] = cluster_idx
            node_to_role[center] = "V1 center"
            
            # Rest of nodes in cluster
            for node in clusters[cluster_idx][1:]:
                node_to_cluster[node] = cluster_idx
                if node in self.v1:
                    node_to_role[node] = "V1 peripheral"
                else:  # node in self.v2
                    node_to_role[node] = "V2"
        
        # Print header
        print(f"\nPolarFly Topology (q={self.q}, N={self.N}, k={self.k})")
        print("=" * 100)
        print(f"{'Node ID':<{width+6}} {'Role':<14} {'Cluster':<8} {'Vector':<15} {'Connections'}")
        print("-" * 100)
        
        # Process nodes in order: quadrics first, then V1 centers, then V1 peripherals, then V2
        for category in ["Quadric", "V1 center", "V1 peripheral", "V2"]:
            nodes = [node for node in self.G.nodes() if node_to_role.get(node, "") == category]
            
            # Sort nodes by cluster, then by ID
            nodes.sort(key=lambda x: (node_to_cluster.get(x, 0), x))
            
            for node in nodes:
                # Get vector representation
                vector = self.G.nodes[node]['vector']
                vector_str = f"({vector[0]},{vector[1]},{vector[2]})"
                
                # Get cluster
                cluster = node_to_cluster.get(node, "N/A")
                cluster_str = f"C{cluster}" if cluster != "N/A" else "N/A"
                
                # Get connections
                connections = sorted(self.G.neighbors(node))
                connections_str = ", ".join([f"node{c:0{width}d}" for c in connections])
                
                # Print node info
                print(f"node{node:0{width}d}: {category:<14} {cluster_str:<8} {vector_str:<15} connects to: {connections_str}")
        
        print("=" * 100)
        
        # Print cluster summary
        print("\nCluster Summary:")
        print("-" * 50)
        print(f"Cluster C0: {len(clusters[0])} quadrics")
        for i in range(1, self.q + 1):
            if clusters[i]:
                v1_count = len([n for n in clusters[i] if n in self.v1])
                v2_count = len([n for n in clusters[i] if n in self.v2])
                print(f"Cluster C{i}: 1 V1 center, {v1_count-1} V1 peripheral nodes, {v2_count} V2 nodes")
        print("-" * 50)

    def export_to_json(self, filename=None):
        """
        Export the PolarFly topology as a JSON file containing all edges.
        Each edge is represented in both directions for bidirectional connections.
        
        Args:
            filename (str, optional): Name of the JSON file to create.
                If not provided, defaults to 'polarfly_q{q}_edges.json'
        
        Returns:
            str: Path to the created JSON file
        """
        if filename is None:
            filename = f'polarfly_q{self.q}_edges.json'
        
        # Format width for node IDs
        width = len(str(self.N - 1))
        
        # Create the edge list in the requested format
        edges_json = []
        for u, v in self.G.edges():
            # Format node IDs with leading zeros
            u_str = f"node{u:0{width}d}"
            v_str = f"node{v:0{width}d}"
            
            # Create the edge object for u->v
            edge_uv = {
                "_key": f"{u_str}_{v_str}",
                "_from": f"radix_{self.k}_node/{u_str}",
                "_to": f"radix_{self.k}_node/{v_str}"
            }
            edges_json.append(edge_uv)
            
            # Create the edge object for v->u (bidirectional)
            edge_vu = {
                "_key": f"{v_str}_{u_str}",
                "_from": f"radix_{self.k}_node/{v_str}",
                "_to": f"radix_{self.k}_node/{u_str}"
            }
            edges_json.append(edge_vu)
        
        # Write to JSON file
        with open(filename, 'w') as f:
            json.dump(edges_json, f, indent=4)
        
        print(f"Exported {len(edges_json)} edges (bidirectional) to {filename}")
        return filename

    def export_vertices_to_json(self, filename=None):
        """
        Export all vertices of the PolarFly topology as a JSON file.
        
        Args:
            filename (str, optional): Name of the JSON file to create.
                If not provided, defaults to 'polarfly_q{q}_vertices.json'
        
        Returns:
            str: Path to the created JSON file
        """
        if filename is None:
            filename = f'polarfly_q{self.q}_vertices.json'
        
        # Format width for node IDs
        width = len(str(self.N - 1))
        
        # Create the vertex list in the requested format
        vertices_json = []
        for node in sorted(self.G.nodes()):
            # Format node ID with leading zeros
            node_str = f"node{node:0{width}d}"
            
            # Create the vertex object
            vertex = {
                "_key": node_str,
                "name": node_str
            }
            vertices_json.append(vertex)
        
        # Write to JSON file
        with open(filename, 'w') as f:
            json.dump(vertices_json, f, indent=4)
        
        print(f"Exported {len(vertices_json)} vertices to {filename}")
        return filename

# Example usage: Generate and visualize PolarFly with q=7
if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Generate and visualize a PolarFly topology.')
    parser.add_argument('-q', '--prime', type=int, default=7, 
                        help='Prime number q to use for PolarFly construction (default: 7)')
    parser.add_argument('--no-labels', action='store_true',
                        help='Hide node labels in visualizations')
    parser.add_argument('--no-interactive', action='store_true',
                        help='Skip the interactive visualization')
    parser.add_argument('--json', action='store_true',
                        help='Export the topology as JSON files (edges and vertices)')
    parser.add_argument('--json-edges', type=str, default=None,
                        help='Filename for the edges JSON export (default: polarfly_q{q}_edges.json)')
    parser.add_argument('--json-vertices', type=str, default=None,
                        help='Filename for the vertices JSON export (default: polarfly_q{q}_vertices.json)')
    
    args = parser.parse_args()
    
    # Validate that q is prime
    def is_prime(n):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True
    
    q = args.prime
    if not is_prime(q):
        print(f"Warning: {q} is not a prime number. PolarFly requires a prime q.")
        print("Continuing anyway, but results may not be valid.")
    
    print(f"Generating PolarFly with q={q}...")
    pf = PolarFly(q)
    
    print(f"Number of vertices: {pf.N}")
    print(f"Degree (radix): {pf.k}")
    print(f"Number of quadrics: {len(pf.quadrics)}")
    print(f"Number of V1 vertices: {len(pf.v1)}")
    print(f"Number of V2 vertices: {len(pf.v2)}")
    
    # Export to JSON if requested
    if args.json:
        pf.export_to_json(args.json_edges)
        pf.export_vertices_to_json(args.json_vertices)
    
    # Print node connections
    pf.print_node_connections()
    
    # Show labels based on command-line argument
    show_labels = not args.no_labels
    
    print("Visualizing standard layout...")
    pf.visualize()
    
    print("Visualizing cluster layout...")
    pf.visualize_cluster_layout()

    # View with a specific cluster highlighted
    print("Visualizing cluster 1 layout...")
    pf.visualize_cluster_layout(highlight_cluster=1)  # Highlight cluster 1

    # Interactive version that works in standard Python windows
    if not args.no_interactive:
        print("Visualizing cluster layout interactively")
        pf.visualize_interactive_pyplot()
