import random

import networkx as nx
import numpy as np

import random


class IDGenerator:
    def __init__(self, num_agents):
        # Initialize a list of available IDs from 0 to num_agents-1
        self.available_ids = list(range(num_agents))

    def get_next_id(self):
        if not self.available_ids:
            raise Exception("No more IDs available.")
        # Randomly select an ID from the list of available IDs
        chosen_id = random.choice(self.available_ids)
        # Remove the chosen ID from the list of available IDs
        self.available_ids.remove(chosen_id)
        return chosen_id


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
            # print(f"{self.get_type()} buying: {amount} @ {coin.price}")
            return amount
        return 0

    def sell(self, coin, amount):
        if self.holdings >= amount:
            self.holdings -= amount
            self.budget += amount * coin.price
            # print(f"{self.get_type()} selling: {amount} @ {coin.price}")
            return amount
        return 0

    def act(self, market):
        pass  # To be defined by subclasses

    def get_type(self):
        pass  # to be defined by subclasses


class RationalAgent(Agent):
    """
    A type of agent that seeks to trade rationally. When instantiated, it comes up with
    a rational determination for the fair market value of a coin. The agent will simply buy below this
    value and attempt to sell above it. This agent will not engage in trading memecoins.
    """

    def __init__(self, id, budget):
        super().__init__(id, budget)
        self.fair_value = None  # Will be set when the first coin is encountered

    def determine_fair_value(self, initial_price):
        # Calculate a fair value based on the initial price and some Gaussian noise
        # The std deviation here is arbitrary and can be adjusted for different market volatilities
        self.fair_value = np.random.normal(initial_price, initial_price * 0.1)
        self.fair_value = 1

    def act(self, market):
        coin = market.coin
        # Set fair value if not set already
        if self.fair_value is None:
            self.determine_fair_value(coin.initial_price)

        # Do not trade if it's a meme coin
        if coin.ismeme:
            return

        # Buy if the price is less than fair value, sell if more, with the amount based on budget/holdings
        if coin.price < self.fair_value:
            # Spend a random proportion of available budget to buy coins
            max_affordable = self.budget // coin.price
            buy_amount = random.randint(1, int(max(max_affordable, 1) * 0.2))  # Will only spend 20% of money at once
            # print(f"buying {buy_amount} @ {coin.price}")
            self.buy(coin, buy_amount)
        elif coin.price > self.fair_value and self.holdings > 0:
            # Sell a random proportion of holdings
            sell_amount = random.randint(1, self.holdings)
            self.sell(coin, sell_amount)
            # print(f"selling {sell_amount} @ {coin.price}")

    def get_type(self):
        return "RationalAgent"


class LinearHerdingAgent(Agent):
    """
    A type of agent that seeks to trade based on sentiment. When instantiated, it comes up with
    a neighbor proportion threshold above which it will buy the coin. The agent will put a random percent of its net worth between 0.05-.05
    into the coin.
    """

    def __init__(self, id, budget, threshold=None, profit_threshold=None, price_sensitivity=None,
                 negative_sentiment_threshold=None):
        super().__init__(id, budget)
        self.threshold = threshold if threshold is not None else random.uniform(0.3, 0.7)
        self.profit_threshold = profit_threshold if profit_threshold is not None else random.uniform(1.2, 2.0)
        self.price_sensitivity = price_sensitivity if price_sensitivity is not None else random.uniform(0.5, 1.5)
        self.negative_sentiment_threshold = negative_sentiment_threshold if negative_sentiment_threshold is not None else random.uniform(
            0.5, 0.8)
        self.initial_buy_proportion = random.uniform(0.05, 0.2)
        self.average_buy_price = None

    def act(self, market):
        coin = market.coin

        # Determine neighbors based on the network type
        if isinstance(market.network, nx.DiGraph):
            neighbors = list(market.network.predecessors(self.id))
        else:
            neighbors = list(market.network[self.id])

        # TODO right now we just do nothing if this guy has no neighbors. Is this moral?
        if not neighbors:
            return

        # Calculate the proportion of neighbors holding the coin
        neighbor_holdings_proportion = sum(market.agents[neighbor].holdings > 0 for neighbor in neighbors) / len(
            neighbors)

        # Buy based on the initial buy proportion if not holding the coin
        if self.holdings == 0 and neighbor_holdings_proportion >= self.threshold:
            max_affordable = self.budget // coin.price
            buy_amount = int(max_affordable * self.initial_buy_proportion)
            self.buy(coin, buy_amount)
            self.average_buy_price = coin.price

        # Buy additional coins if more neighbors start holding
        # elif self.holdings > 0 and neighbor_holdings_proportion > self.threshold:
        #     max_affordable = self.budget // coin.price
        #     buy_amount = int(max_affordable * 0.1)  # Buy an additional 10% of affordable coins
        #     self.buy(coin, buy_amount)
        #     self.average_buy_price = (self.average_buy_price * (self.holdings - buy_amount) + coin.price * buy_amount) / self.holdings

        # Consider profit-taking based on neighbor proportion and price changes
        if self.holdings > 0 and self.average_buy_price is not None:
            current_profit = coin.price / self.average_buy_price
            #TODO look into sell logic
            sell_probability = (1 - neighbor_holdings_proportion) * (current_profit / (self.profit_threshold * self.price_sensitivity)) + \
                               (neighbor_holdings_proportion) * (current_profit - self.profit_threshold) / (current_profit + 1)
            if random.random() < sell_probability:
                self.sell(coin, self.holdings)  # Sell all holdings
                self.average_buy_price = None

        # Sell based on negative sentiment among neighbors
        if self.holdings > 0:
            negative_sentiment = sum(market.agents[neighbor].holdings == 0 for neighbor in neighbors) / len(neighbors)
            if negative_sentiment > self.negative_sentiment_threshold:
                self.sell(coin, self.holdings)  # Sell all holdings
                self.average_buy_price = None

    def get_type(self):
        return "LinearHerdingAgent"
