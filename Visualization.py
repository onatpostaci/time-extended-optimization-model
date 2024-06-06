import matplotlib.pyplot as plt
import networkx as nx

def visualize_time_extended_network():
    # Create a directed graph
    G = nx.DiGraph()  # Using DiGraph to ensure the arrows are visible

    # Adding nodes and time-extended arcs with capacity and time labels
    nodes = ['0', '1', '2', '3', 'A', 'B']
    arcs = [
        ('B', '2', {'capacity': 10, 'time': '9:00', 'label': '10@9:00'}),
        ('2', '0', {'capacity': 10, 'time': '10:00', 'label': '10@10:00'}),
        ('0', '1', {'capacity': 5, 'time': '11:00', 'label': '5@11:00'}),
        ('2', '3', {'capacity': 10, 'time': '10:30', 'label': '10@10:30'}),
        ('3', '1', {'capacity': 10, 'time': '11:30', 'label': '10@11:30'}),
        ('1', 'A', {'capacity': 10, 'time': '12:00', 'label': '10@12:00'})
    ]

    # Node positions for clear visualization
    positions = {
        'B': (0, 1), '2': (1, 1), '0': (2, 1),
        '1': (3, 0), '3': (2, 0), 'A': (4, 0)
    }

    # Add nodes and edges to the graph
    G.add_nodes_from(nodes)
    for start, end, attr in arcs:
        G.add_edge(start, end, **attr)

    # Draw the network
    plt.figure(figsize=(12, 6))
    node_colors = ['green' if node == 'B' else 'red' if node == 'A' else 'skyblue' for node in nodes]
    nx.draw_networkx_nodes(G, pos=positions, node_color=node_colors, node_size=2000)
    nx.draw_networkx_labels(G, pos=positions, font_size=12, font_family='sans-serif')

    # Draw edges with enhanced arrow properties
    nx.draw_networkx_edges(G, pos=positions, arrowstyle='-|>', arrowsize=20, edge_color='black', node_size=2000,
                           connectionstyle='arc3,rad=0.1')

    # Draw edge labels with capacity and time
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels, font_color='red', font_size=10)

    plt.title('Time-Extended Network Visualization with Clear Directed Arrows')
    plt.axis('off')  # Turn off the axis for aesthetics
    plt.show()

# Call the function to visualize the time-extended network
visualize_time_extended_network()
