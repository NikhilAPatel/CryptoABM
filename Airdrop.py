import random
from abc import ABC, abstractmethod


class AirdropStrategy(ABC):
    """
    Defines an Airdrop Strategy
    :param market
    :param coin
    :param percentage
    :param amount
    :param time - Expressed as a number [0,1] representing the percentage of the way through the simulation when the airdrop should be performed
    """

    def __init__(self, coin, percentage, amount, time):
        self.coin = coin
        self.percentage = percentage
        self.amount = amount
        self.time = time

    @abstractmethod
    def select_recipients(self, market):
        pass

    @abstractmethod
    def get_type(self):
        pass

    def get_descriptor(self):
        return f"{self.get_type()}({self.coin.name} {self.percentage * 100}% {self.amount})"

    def do_airdrop(self, market):
        recipients = self.select_recipients(market)
        for id in recipients:
            agent = market.agent_structure.get_agent(id)
            agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + self.amount
            agent.average_buy_prices[self.coin] = self.coin.price


class RandomAirdropStrategy(AirdropStrategy):
    """
    Random Airdrop Strategy
    :param market
    :param coin
    :param percentage
    :param amount
    """

    def select_recipients(self, market):
        recipients = random.choices(market.agent_structure.agents, k=int(market.num_agents * self.percentage))
        return [agent.id for agent in recipients]

    def get_type(self):
        return "RandomAirdropStrategy"

class ProportionalLeaderAirdropStrategy(AirdropStrategy):
    def __init__(self, coin, percentage, amount, time, threshold):
        super().__init__(coin, percentage, amount, time)
        self.threshold = threshold  # This is the target threshold percentage of crypto to total assets
    def do_airdrop(self, market):
        # Determine the number of leaders to target
        num_leaders = int(len(market.agent_structure.agents) * self.percentage)

        # Get the nodes sorted by their degree (influence)
        agent_degrees = dict(market.network.degree())
        agent_degrees = sorted(agent_degrees.items(), key=lambda x: x[1], reverse=True)

        recipients = agent_degrees[:num_leaders]

        for agent, degree in recipients:
            print(agent, market.agent_structure.get_agent(agent).get_type())

        # sorted_agents = sorted(agent_degrees,
        #                        key=lambda agent: market.agent_structure.get_agent(agent_degrees[agent.id]),
        #                        reverse=True)
        # targeted_agents = sorted_agents[:num_leaders]
        #
        # print(sorted_agents)

        # Calculate and distribute the airdrop
        # for agent in targeted_agents:
        #     total_assets = agent.get_total_assets()  # Assuming there is a method to calculate total assets
        #     needed_airdrop = (self.threshold * total_assets) - agent.holdings.get(self.coin.name, 0)
        #
        #     # Only airdrop if the needed amount is less than or equal to the predefined amount
        #     if 0 < needed_airdrop <= self.amount:
        #         agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + needed_airdrop
        #         agent.average_buy_prices[self.coin] = self.coin.price  # Update average buy price if needed
        #
        #     # Optionally, adjust this condition based on additional strategy requirements
        #     elif needed_airdrop <= 0:
        #         continue  # No airdrop needed, already meets or exceeds the threshold

        return f"Airdropped strategically to ensure neighborhood asset thresholds are met"


    def select_recipients(self, market):
        pass

    def get_type(self):
        return "ProportionalLeaderAirdropStrategy"




class LeaderAirdropStrategy(AirdropStrategy):
    """
    Distributes coins to nodes with the highest degrees
    :param market
    :param coin
    :param percentage
    :param amount
    """

    def select_recipients(self, market):
        # Determine the number of leaders to target
        num_leaders = int(len(market.agent_structure.agents) * self.percentage)

        # Get the nodes sorted by their degree (influence)
        agent_degrees = dict(market.network.degree())
        agent_degrees = sorted(agent_degrees.items(), key=lambda x: x[1], reverse=True)

        recipients = agent_degrees[:num_leaders]
        recipients = [agent for agent, degree in recipients]
        return recipients

    def get_type(self):
        return "LeaderAirdropStrategy"


class BiggestHoldersAirdropStrategy(AirdropStrategy):
    """
    Distributes coins to those with highest amount of some other existing coin
    :param market
    :param coin
    :param percentage
    :param amount
    :param time - Expressed as a number [0,1] representing the percentage of the way through the simulation when the airdrop should be performed
    :param existing_coin
    """

    def __init__(self, coin, percentage, amount, time, existing_coin):
        super().__init__(coin, percentage, amount, time)
        self.existing_coin = existing_coin

    def select_recipients(self, market):
        sorted_agents = sorted(market.agent_structure.agents, key=lambda agent: agent.holdings.get(self.existing_coin.name, 0),
                               reverse=True)
        num_recipients = int(market.num_agents * self.percentage)
        sorted_agents = sorted_agents[:num_recipients]
        sorted_agents = [agent.id for agent in sorted_agents]
        return sorted_agents

    def get_type(self):
        return "BiggestHoldersAirdropStrategy"

    def get_descriptor(self):
        return f"{self.get_type()}({self.coin.name} {self.percentage * 100}% {self.amount} to {self.existing_coin.name})"
