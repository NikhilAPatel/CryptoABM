import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


class Cryptocurrency:
    def __init__(self, name, initial_price):
        self.coinname = name
        self.price = initial_price
        self.initial_price = initial_price


class Agent:
    def __init__(self, id, budget):
        self.id = id
        self.budget = budget
        self.holdings = 0

    def buy(self, coin, amount):
        cost = amount * coin.price
        if self.budget >= cost:
            self.budget -= cost
            self.holdings += amount
            return amount
        return 0

    def sell(self, coin, amount):
        if self.holdings >= amount:
            self.holdings -= amount
            self.budget += amount * coin.price
            return amount
        return 0

    def act(self, market):
        pass  # To be defined by subclasses


class RationalAgent(Agent):
    #TODO change this so it buys amount based on availabnle cash (and sells appropriately too)
    #Also more sophisticated method of determining fair market value
    def act(self, market):
        coin = market.coin
        # fair_value = coin.initial_price * (1 + 0.05 * np.random.randn())
        fair_value = 2
        if coin.price < fair_value:
            self.buy(coin, random.randint(1,5))
        else:
            self.sell(coin, random.randint(1,5))


class HerdingAgent(Agent):
    #TODO even herding agents want to take profits sometimes
    def act(self, market):
        coin = market.coin

        # Buying based on herding behavior...
        neighbors = list(market.network[self.id])
        # Herd behavior: buy if majority of neighbors have this coin
        if sum(market.agents[neighbor].holdings > 0 for neighbor in neighbors) / len(
                neighbors) > 0.5:
            self.buy(coin, 1)

        # Sell based on negative sentiment among neighbors
        if self.holdings > 0:
            negative_sentiment = sum(
                market.agents[neighbor].holdings <= 0
                for neighbor in neighbors
            ) / len(neighbors) > 0.5
            if negative_sentiment:
                self.sell(coin, self.holdings)  # Sell all


# You can similarly define MemeCoinAgent and SniperAgent with their own act() methods.

class CryptoMarket:
    def __init__(self, num_agents, initial_coin):
        self.agents = [HerdingAgent(i, random.randint(1000, 10000)) for i in
                       range(num_agents)]  # Add different agents here
        self.coin = initial_coin
        self.network = self.create_network(num_agents)

    def create_network(self, num_agents):
        return nx.barabasi_albert_graph(num_agents, 2)

    def get_coin_price(self, coin_name):
        return self.coin.price

    def set_coin_price(self, coin_name, new_price):
        self.coin.price = new_price

    def airdrop(self, agents, amount):
        for agent in agents:
            agent.holdings += amount

    def simulate(self, num_iterations):
        price_history = [self.coin.price]

        #airdrop crypto to percentage of users
        self.airdrop(random.choices(self.agents, k = int(len(self.agents)*0.5)), 100)

        for _ in range(num_iterations):
            total_bought = 0
            total_sold = 0

            # Each agent acts based on its type
            for agent in self.agents:
                initial_holdings = agent.holdings  # Record initial holdings to determine buy/sell volume
                agent.act(self)
                change_in_holdings = agent.holdings - initial_holdings

                # Increment bought or sold counters
                if change_in_holdings > 0:
                    total_bought += change_in_holdings
                elif change_in_holdings < 0:
                    total_sold += -change_in_holdings  # Subtract because change_in_holdings is negative

            # Adjust prices based on the actions taken by agents
            net_demand = total_bought - total_sold
            price_change_factor = 1 + (
                        net_demand / (len(self.agents) + 1)) * 0.05  # Price changes by 5% per net agent demand
            self.coin.price *= price_change_factor  # Modify the price based on net demand
            self.coin.price = max(self.coin.initial_price,
                                  self.coin.price)  # Prevent the price from dropping below initial
            price_history.append(self.coin.price)

        return {self.coin.coinname: price_history}

    def plot_price_history(self, price_history):
        plt.figure(figsize=(12, 6))
        for coin_name, prices in price_history.items():
            plt.plot(prices, label=coin_name)
        plt.xlabel('Iteration')
        plt.ylabel('Price')
        plt.title('Cryptocurrency Price Simulation')
        plt.legend()
        plt.show()


# Example usage
btc = Cryptocurrency('CryptoCoin', 1.00)

# Note: You would need to add the other agents to the market as well for a mixed-agent simulation.
market = CryptoMarket(num_agents=100, initial_coin=btc)
price_history = market.simulate(500)
market.plot_price_history(price_history)
