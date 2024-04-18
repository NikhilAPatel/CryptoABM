import random
from abc import ABC, abstractmethod

import networkx as nx


class AirdropStrategy(ABC):
    """
    Defines an Airdrop Strategy
    :param market
    :param coin
    :param percentage
    :param amount
    :param time - Expressed as a number [0,1] representing the percentage of the way through the simulation when the airdrop should be performed
    """

    def __init__(self, coin, time, percentage):
        self.coin = coin
        self.time = time
        self.percentage = percentage

    @abstractmethod
    def select_recipients(self, market):
        pass

    @abstractmethod
    def get_type(self):
        pass

    def get_descriptor(self):
        pass

    def do_airdrop(self, market):
        pass


class RandomAirdropStrategy(AirdropStrategy):
    """
    Random Airdrop Strategy
    :param market
    :param coin
    :param percentage
    :param amount
    """
    def __init__(self, coin, time, percentage, amount):
        super().__init__(coin, time, percentage)
        self.amount = amount

    def select_recipients(self, market):
        recipients = random.choices(market.agent_structure.agents, k=int(market.num_agents * self.percentage))
        return [agent.id for agent in recipients]

    def do_airdrop(self, market):
        recipients = self.select_recipients(market)
        total_airdropped = 0
        total_value_airdropped = 0
        for id in recipients:
            agent = market.agent_structure.get_agent(id)
            agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + self.amount
            agent.average_buy_prices[self.coin] = self.coin.price
            total_airdropped += self.amount
            total_value_airdropped += self.amount * self.coin.price

        print(
            f"{self.get_type()} airdropped {total_airdropped} {self.coin.name} for a total of ${total_value_airdropped} at time {self.time} ")

    def get_type(self):
        return "RandomAirdropStrategy"

class MoreToLeaders(AirdropStrategy):
    def __init__(self, coin, time, percentage, total_coins):
        super().__init__(coin, time, percentage)
        self.total_coin = total_coins

    def do_airdrop(self, market):
        total_airdropped = 0
        total_value_airdropped = 0
        # Determine the number of leaders to target
        num_leaders = int(len(market.agent_structure.agents) * self.percentage)

        # Get the nodes sorted by their degree (influence)
        agent_degrees = dict(market.network.degree())
        agent_degrees = sorted(agent_degrees.items(), key=lambda x: x[1], reverse=True)
        recipients = agent_degrees[:num_leaders]

        total_degree = sum([degree for agent,degree in recipients])

        for id, degree in recipients:
            agent = market.agent_structure.get_agent(id)

            add = (int(degree)/total_degree) * self.total_coin

            agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + add
            agent.average_buy_prices[self.coin] = self.coin.price
            total_airdropped += add
            total_value_airdropped += add * self.coin.price

        print(
            f"{self.get_type()} airdropped {total_airdropped} {self.coin.name} for a total of ${total_value_airdropped} at time {self.time} ")

    def select_recipients(self, market):
        pass

    def get_type(self):
        return "MoreToLeaders"
class ProportionalLeaderAirdropStrategy(AirdropStrategy):
    """
    To the top x% of people by outdegree, we give them enough coin such that the total invested proportion of their neighborhood exceeds some threshold
    :param coin
    :param time
    :param percentage
    :param threshold
    """
    def __init__(self, coin, time, percentage, threshold):
        super().__init__(coin, time, percentage)
        self.threshold = threshold

    def do_airdrop(self, market):
        total_airdropped = 0
        total_value_airdropped = 0
        # Determine the number of leaders to target
        num_leaders = int(len(market.agent_structure.agents) * self.percentage)

        # Get the nodes sorted by their degree (influence)
        agent_degrees = dict(market.network.degree())
        agent_degrees = sorted(agent_degrees.items(), key=lambda x: x[1], reverse=True)

        recipients = agent_degrees[:num_leaders]

        for id, degree in recipients:
            agent = market.agent_structure.get_agent(id)

            if isinstance(market.network, nx.DiGraph):
                neighbors = list(market.network.predecessors(id))
            else:
                neighbors = list(market.network[id])

            total_neighbor_coin_value = sum(
                market.agent_structure.get_agent(neighbor).holdings.get(self.coin.name, 0) * self.coin.price for
                neighbor in
                neighbors)

            total_neighbor_portfolio_value = sum(
                market.agent_structure.get_agent(neighbor).get_total_portfolio_value(market) for neighbor in neighbors)

            add = (self.threshold * total_neighbor_portfolio_value - total_neighbor_coin_value) / self.coin.price
            add = max(0, add)

            # print(id, total_neighbor_coin_value, total_neighbor_portfolio_value, add)

            agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + add
            agent.average_buy_prices[self.coin] = self.coin.price
            total_airdropped += add
            total_value_airdropped += add * self.coin.price

        print(
            f"ProportionalLeaderAirdropStrategy airdropped {total_airdropped} {self.coin.name} for a total of ${total_value_airdropped} at time {self.time} ")

    def select_recipients(self, market):
        pass

    def get_type(self):
        return "ProportionalLeaderAirdropStrategy"


class RandomProportionalAirdropStrategy(AirdropStrategy):
    def __init__(self, coin, time, percentage, threshold):
        super().__init__(coin, time, percentage)
        self.threshold = threshold  # This is the target threshold percentage of crypto to total assets

    def do_airdrop(self, market):
        total_airdropped = 0
        total_value_airdropped = 0

        # Determine the number of leaders to target
        recipients = random.choices(market.agent_structure.agents, k=int(market.num_agents * self.percentage))
        recipients = [agent.id for agent in recipients]

        for id in recipients:
            agent = market.agent_structure.get_agent(id)

            if isinstance(market.network, nx.DiGraph):
                neighbors = list(market.network.predecessors(id))
            else:
                neighbors = list(market.network[id])

            total_neighbor_coin_value = sum(
                market.agent_structure.get_agent(neighbor).holdings.get(self.coin.name, 0) * self.coin.price for
                neighbor in
                neighbors)

            total_neighbor_portfolio_value = sum(
                market.agent_structure.get_agent(neighbor).get_total_portfolio_value(market) for neighbor in neighbors)

            add = (self.threshold * total_neighbor_portfolio_value - total_neighbor_coin_value) / self.coin.price
            add = max(0, add)

            # print(id, total_neighbor_coin_value, total_neighbor_portfolio_value, add)

            agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + add
            agent.average_buy_prices[self.coin] = self.coin.price
            total_airdropped += add
            total_value_airdropped += add * self.coin.price

        print(
            f"{self.get_type()} airdropped {total_airdropped} {self.coin.name} for a total of ${total_value_airdropped} at time {self.time} ")

    def select_recipients(self, market):
        pass

    def get_type(self):
        return "RandomProportionalAirdropStrategy"


class LeaderAirdropStrategy(AirdropStrategy):
    """
    Distributes coins to nodes with the highest degrees
    :param market
    :param coin
    :param percentage
    :param amount
    """

    def __init__(self, market, coin, percentage, amount):
        super().__init__(market, coin, percentage)
        self.amount = amount


    def select_recipients(self, market):
        # Determine the number of leaders to target
        num_leaders = int(len(market.agent_structure.agents) * self.percentage)

        # Get the nodes sorted by their degree (influence)
        agent_degrees = dict(market.network.degree())
        agent_degrees = sorted(agent_degrees.items(), key=lambda x: x[1], reverse=True)

        recipients = agent_degrees[:num_leaders]
        recipients = [agent for agent, degree in recipients]
        return recipients

    def do_airdrop(self, market):
        recipients = self.select_recipients(market)
        total_airdropped = 0
        total_value_airdropped = 0
        for id in recipients:
            agent = market.agent_structure.get_agent(id)
            agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + self.amount
            agent.average_buy_prices[self.coin] = self.coin.price
            total_airdropped += self.amount
            total_value_airdropped += self.amount * self.coin.price

        print(
            f"{self.get_type()} airdropped {total_airdropped} {self.coin.name} for a total of ${total_value_airdropped} at time {self.time} ")

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

    def __init__(self, coin, time, percentage, amount, existing_coin):
        super().__init__(coin, time, percentage)
        self.amount = amount
        self.time = time
        self.existing_coin = existing_coin

    def select_recipients(self, market):
        sorted_agents = sorted(market.agent_structure.agents,
                               key=lambda agent: agent.holdings.get(self.existing_coin.name, 0),
                               reverse=True)
        num_recipients = int(market.num_agents * self.percentage)
        sorted_agents = sorted_agents[:num_recipients]
        sorted_agents = [agent.id for agent in sorted_agents]
        return sorted_agents

    def do_airdrop(self, market):
        recipients = self.select_recipients(market)
        total_airdropped = 0
        total_value_airdropped = 0
        for id in recipients:
            agent = market.agent_structure.get_agent(id)
            agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + self.amount
            agent.average_buy_prices[self.coin] = self.coin.price
            total_airdropped += self.amount
            total_value_airdropped += self.amount * self.coin.price

        print(
            f"{self.get_type()} airdropped {total_airdropped} {self.coin.name} for a total of ${total_value_airdropped} at time {self.time} ")

    def get_type(self):
        return "BiggestHoldersAirdropStrategy"

    def get_descriptor(self):
        return f"{self.get_type()}({self.coin.name} {self.percentage * 100}% {self.amount} to {self.existing_coin.name})"

class ProportionalBiggestHoldersAirdropStrategy(AirdropStrategy):
    """
    To the top x% of people by amount of existing coin held, we give them enough coin such that the total invested proportion of their neighborhood exceeds some threshold
    :param market
    :param coin
    :param percentage
    :param amount
    :param time - Expressed as a number [0,1] representing the percentage of the way through the simulation when the airdrop should be performed
    :param existing_coin
    """

    def __init__(self, coin, time, percentage, threshold, existing_coin):
        super().__init__(coin, time, percentage)
        self.time = time
        self.existing_coin = existing_coin
        self.threshold = threshold

    def select_recipients(self, market):
        sorted_agents = sorted(market.agent_structure.agents,
                               key=lambda agent: agent.holdings.get(self.existing_coin.name, 0),
                               reverse=True)
        num_recipients = int(market.num_agents * self.percentage)
        sorted_agents = sorted_agents[:num_recipients]
        sorted_agents = [agent.id for agent in sorted_agents]
        return sorted_agents

    def do_airdrop(self, market):
        total_airdropped = 0
        total_value_airdropped = 0

        recipients = self.select_recipients(market)

        for id in recipients:
            agent = market.agent_structure.get_agent(id)

            if isinstance(market.network, nx.DiGraph):
                neighbors = list(market.network.predecessors(id))
            else:
                neighbors = list(market.network[id])

            total_neighbor_coin_value = sum(
                market.agent_structure.get_agent(neighbor).holdings.get(self.coin.name, 0) * self.coin.price for
                neighbor in
                neighbors)

            total_neighbor_portfolio_value = sum(
                market.agent_structure.get_agent(neighbor).get_total_portfolio_value(market) for neighbor in neighbors)

            add = (self.threshold * total_neighbor_portfolio_value - total_neighbor_coin_value) / self.coin.price
            add = max(0, add)

            print(id, total_neighbor_coin_value, total_neighbor_portfolio_value, add)

            agent.holdings[self.coin.name] = agent.holdings.get(self.coin.name, 0) + add
            agent.average_buy_prices[self.coin] = self.coin.price
            total_airdropped += add
            total_value_airdropped += add * self.coin.price

        print(
            f"{self.get_type()} airdropped {total_airdropped} {self.coin.name} for a total of ${total_value_airdropped} at time {self.time} ")

    def get_type(self):
        return "ProportionalBiggestHoldersAirdropStrategy"

    def get_descriptor(self):
        # return f"{self.get_type()}({self.coin.name} {self.percentage * 100}% {self.amount} to {self.existing_coin.name})"
        return "TODO"