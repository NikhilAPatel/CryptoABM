import random


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

    def get_type(self):
        pass # to be defined by subclasses


class RationalAgent(Agent):
    #TODO change this so it buys amount based on available cash (and sells appropriately too based on how many coins it has)
    #TODO more sophisticated method of determining fair market value
    def act(self, market):
        coin = market.coin
        # fair_value = coin.initial_price * (1 + 0.05 * np.random.randn())
        fair_value = 2
        if coin.price < fair_value:
            self.buy(coin, random.randint(1,5))
        else:
            self.sell(coin, random.randint(1,5))

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

        # Sell based on negative sentiment among neighbors
        if self.holdings > 0:
            negative_sentiment = sum(
                market.agents[neighbor].holdings <= 0
                for neighbor in neighbors
            ) / len(neighbors) > 0.5
            if negative_sentiment:
                self.sell(coin, self.holdings)  # Sell all

    def get_type(self):
        return "HerdingAgent"