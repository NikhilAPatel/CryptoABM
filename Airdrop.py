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
        for agent in recipients:
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
        return random.choices(market.agents, k=int(len(market.agents) * self.percentage))

    def get_type(self):
        return "RandomAirdropStrategy"


class LeaderAirdropStrategy(AirdropStrategy):
    """
    Distributes coins to nodes with the highest degrees
    :param market
    :param coin
    :param percentage
    :param amount
    """

    def select_recipients(self, market):
        agent_degrees = dict(market.network.degree())
        sorted_agents = sorted(market.agents, key=lambda agent: agent_degrees[agent.id], reverse=True)
        num_recipients = int(len(market.agents) * self.percentage)
        return sorted_agents[:num_recipients]

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
        sorted_agents = sorted(market.agents, key=lambda agent: agent.holdings.get(self.existing_coin.name, 0),
                               reverse=True)
        num_recipients = int(len(market.agents) * self.percentage)
        return sorted_agents[:num_recipients]

    def get_type(self):
        return "BiggestHoldersAirdropStrategy"

    def get_descriptor(self):
        return f"{self.get_type()}({self.coin.name} {self.percentage * 100}% {self.amount} to {self.existing_coin.name})"
