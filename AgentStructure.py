import random

import numpy as np


class IDGenerator:
    def __init__(self, num_agents):
        self.available_ids = list(range(num_agents))

    def get_next_id(self):
        if not self.available_ids:
            raise Exception("No more IDs available.")
        chosen_id = random.choice(self.available_ids)
        self.available_ids.remove(chosen_id)
        return chosen_id


class AgentStructure:
    """
    Note do not directly index into agents. Must use the get agent by id function
    """
    def __init__(self, num_agents):
        self.num_agents = num_agents
        self.agents = []
        self.id_generator = IDGenerator(self.num_agents)
        self.agent_type_string = ""
        self.agent_types = []

    def add_agents(self, agent, number):
        self.agents += [agent(self.id_generator.get_next_id(), budget=random.randint(1000, 10000)) for _ in
                        range(number)]
        self.agent_type_string += f"{self.agents[-1].get_type()}: {number}, "
        self.agent_types += [self.agents[-1].get_type()]

    def get_agent(self, id):
        for agent in self.agents:
            if agent.id == id:
                return agent

    def budgets_based_on_popularity(self, market, min_budget=1000, max_budget=10_000, scaling_factor=10):
        """
        Initializes agents' budgets based on their degree in the network.
        Agents with higher degrees (influencers) receive larger initial budgets.
        """
        # Get the degree of each agent in the market network
        # Get the degree of each agent in the market network
        degrees = dict(market.network.degree())

        # Calculate the maximum degree
        max_degree = max(degrees.values())

        # Assign initial budget to agents based on their degree using exponential scaling
        for agent in self.agents:
            agent_degree = degrees[agent.id]
            degree_ratio = agent_degree / max_degree

            # Calculate the agent's initial budget using exponential scaling
            agent_budget = int(min_budget * (scaling_factor ** degree_ratio))

            # Ensure the budget is within the specified range
            agent_budget = max(min_budget, min(agent_budget, max_budget))

            # Set the agent's budget
            agent.budget = agent_budget

    def get_descriptor(self):
        return f"{self.num_agents} agents ({self.agent_type_string})"
