import random

import numpy as np


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
            print(f"{self.get_type()} buying: {amount} @ {coin.price}")
            return amount
        return 0

    def sell(self, coin, amount):
        if self.holdings >= amount:
            self.holdings -= amount
            self.budget += amount * coin.price
            print(f"{self.get_type()} selling: {amount} @ {coin.price}")
            return amount
        return 0

    def act(self, market):
        pass  # To be defined by subclasses

    def get_type(self):
        pass # to be defined by subclasses


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
        self.fair_value =2

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
            buy_amount = random.randint(1, int(max(max_affordable, 1)*0.2)) #Will only spend 20% of money at once
            # print(f"buying {buy_amount} @ {coin.price}")
            self.buy(coin, buy_amount)
        elif coin.price > self.fair_value and self.holdings > 0:
            # Sell a random proportion of holdings
            sell_amount = random.randint(1, self.holdings)
            self.sell(coin, sell_amount)
            # print(f"selling {sell_amount} @ {coin.price}")

    def get_type(self):
        return "RationalAgent"


class HerdingAgent(Agent):
    #TODO even herding agents want to take profits sometimes
    def act(self, market):
        coin = market.coin

        # Buying based on herding behavior...
        neighbors = list(market.network[self.id])
        # Herd behavior: buy if the majority of neighbors have this coin
        if sum(market.agents[neighbor].holdings > 0 for neighbor in neighbors) / len(
                neighbors) > 0.5:
            self.buy(coin, 1)
            # print(f"buying {1} @ {coin.price}")

        # Sell based on negative sentiment among neighbors
        if self.holdings > 0:
            negative_sentiment = sum(
                market.agents[neighbor].holdings <= 0
                for neighbor in neighbors
            ) / len(neighbors) > 0.5
            if negative_sentiment:
                self.sell(coin, self.holdings)  # Sell all
                # print(f"selling {self.holdings} @ {coin.price}")

    def get_type(self):
        return "HerdingAgent"