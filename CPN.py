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



def create_multiple_core_periphery_networks(total_agents, networks_count, interlink_probability, directed=False):
    """
    Creates multiple core periphery networks joined together mostly through cores. Important hyperparameter is the number of networks
    :param total_agents:
    :param networks_count:
    :param interlink_probability:
    :param directed:
    :return:
    """
    # Assume an equal number of agents per network for simplicity
    agents_per_network = total_agents // networks_count

    # Function to create a single core-periphery network based on the directed flag
    def create_network(agents_count):
        if directed:
            return create_directed_core_periphery_network(agents_count)
        else:
            return create_core_periphery_network(agents_count)

    # Create individual core-periphery networks
    networks = [create_network(agents_per_network) for _ in range(networks_count)]

    # Initialize one large graph to contain all individual networks
    if directed:
        large_network = nx.DiGraph()
    else:
        large_network = nx.Graph()

    # Add individual networks to the large graph
    offset = 0
    for net in networks:
        # Relabel nodes to ensure unique identifiers across the entire large network
        mapping = {i: i + offset for i in net.nodes()}
        relabeled_net = nx.relabel_nodes(net, mapping)
        large_network = nx.compose(large_network, relabeled_net)

        # Increment offset for the next network
        offset += agents_per_network

    # Link the networks together
    # For each network, try to link its core nodes to core nodes of other networks
    for i in range(networks_count):
        core_nodes_i = range(i * agents_per_network, i * agents_per_network + int(agents_per_network * 0.2))

        for j in range(networks_count):
            if i != j:
                core_nodes_j = range(j * agents_per_network, j * agents_per_network + int(agents_per_network * 0.2))

                # Randomly establish inter-core links based on the specified probability
                for node_i in core_nodes_i:
                    for node_j in core_nodes_j:
                        if random.random() < interlink_probability:
                            if directed:
                                # For directed, the link direction can also be randomized or set to a specific direction
                                if random.random() < 0.5:
                                    large_network.add_edge(node_i, node_j)
                                else:
                                    large_network.add_edge(node_j, node_i)
                            else:
                                large_network.add_edge(node_i, node_j)

    return large_network

