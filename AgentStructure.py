import random


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

    def get_descriptor(self):
        return f"{self.num_agents} agents ({self.agent_type_string})"
