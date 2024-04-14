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


import networkx as nx
import random


def create_directed_core_periphery_network(num_agents, core_percent=0.2, core_to_core_prob=0.5,
                                           core_to_periphery_prob=0.5, periphery_to_periphery_prob=0.1,
                                           periphery_to_core_prob=0.01):
    G = nx.DiGraph()
    core_size = int(num_agents * core_percent)  # Determine the number of core nodes

    # Add all agents as nodes
    G.add_nodes_from(range(num_agents))

    # Connect each core node with other core nodes with a higher probability
    for i in range(core_size):
        for j in range(core_size):
            if i != j and random.random() < core_to_core_prob:
                G.add_edge(i, j)

    # Connect core nodes to periphery nodes with a higher probability
    for i in range(core_size):
        for j in range(core_size, num_agents):
            if random.random() < core_to_periphery_prob:
                G.add_edge(i, j)

    # Allow periphery nodes to connect to other periphery nodes with a lower probability
    for i in range(core_size, num_agents):
        for j in range(core_size, num_agents):
            if i != j and random.random() < periphery_to_periphery_prob:
                G.add_edge(i, j)

    # Rarely allow periphery nodes to influence core nodes
    for i in range(core_size, num_agents):
        for j in range(core_size):
            if random.random() < periphery_to_core_prob:
                G.add_edge(i, j)

    return G
