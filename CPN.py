import random

import networkx as nx


def create_core_periphery_network(num_agents, core_percent = 0.2, core_connected_prob = 0.5, periphery_connected_prob = 0.1):
    G = nx.Graph()
    core_size = int(num_agents * core_percent)  # Let's say 20% of nodes are core nodes

    # Add all agents as nodes
    G.add_nodes_from(range(num_agents))

    # Connect each core node with other core nodes
    for i in range(core_size):
        for j in range(i + 1, core_size):
            G.add_edge(i, j)

    # Connect core nodes to periphery nodes
    for i in range(core_size):
        for j in range(core_size, num_agents):
            if random.random() < core_connected_prob:  # Randomly connect core to periphery
                G.add_edge(i, j)

    # Optionally, add some random connections among periphery nodes to increase complexity
    for i in range(core_size, num_agents):
        for j in range(i + 1, num_agents):
            if random.random() < periphery_connected_prob:  # Sparse connectivity among periphery
                G.add_edge(i, j)

    return G