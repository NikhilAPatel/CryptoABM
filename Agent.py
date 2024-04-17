import math
import random
import networkx as nx
import numpy as np
from scipy.stats import pareto


class Agent:
    def __init__(self, id, budget):
        self.id = id
        self.budget = budget
        self.holdings = {}
        self.average_buy_prices = {}
        self.bought = set()

    def buy(self, coin, amount):
        cost = amount * coin.price
        if self.budget >= cost:
            self.budget -= cost
            self.holdings[coin.name] = self.holdings.get(coin.name, 0) + amount
            self.bought.add(coin.name)
            return amount
        return 0

    def sell(self, coin, amount):
        if self.holdings.get(coin.name, 0) >= amount:
            self.holdings[coin.name] -= amount
            self.budget += amount * coin.price
            return amount
        return 0
    
    def sell_all(self, coin):
        self.sell(coin, self.holdings.get(coin.name, 0))
        if coin.name in self.bought:
            self.bought.remove(coin.name)

    def act(self, market, coin):
        pass

    def get_type(self):
        pass


class RationalAgent(Agent):
    """
    A type of agent that seeks to trade rationally. When instantiated, it comes up with
    a rational determination for the fair market value of a coin. The agent will simply buy below this
    value and attempt to sell above it. It will only invest up to 20% of its networth in a coin. This agent will not engage in trading memecoins.

    They sell meme coins immediately as they believe them to have no intrinsic value
    """

    def __init__(self, id, budget):
        super().__init__(id, budget)
        self.fair_values = {}

    def determine_fair_value(self, coin):
        self.fair_values[coin.name] = np.random.normal(coin.initial_price, coin.initial_price * 0.1)

    def act(self, market, coin):
        if coin.name not in self.fair_values:
            self.determine_fair_value(coin)

        #rational investors will just sell a meme coin asap
        if coin.is_meme:
            if self.holdings.get(coin.name, 0)>0:
                self.sell_all(coin)
            return

        if coin.price < self.fair_values[coin.name]:
            max_affordable = self.budget // coin.price
            try:
                buy_amount = random.randint(1, int(max(max_affordable, 1) * 0.2))
            except ValueError:
                buy_amount = 0
            self.buy(coin, buy_amount)
        elif coin.price > self.fair_values[coin.name] and self.holdings.get(coin.name, 0) > 0:
            sell_amount = random.randint(1, self.holdings[coin.name])
            self.sell(coin, sell_amount)

    def get_type(self):
        return "RationalAgent"


class LinearHerdingAgent(Agent):
    """
    Buys if the proportion of the neighborhood holding the coin is sufficient
    Will sell for profit
    Will sell for sentiment
    """
    def __init__(self, id, budget, threshold=None, price_sensitivity=None,
                 negative_sentiment_threshold=None):
        super().__init__(id, budget)
        self.threshold = threshold if threshold is not None else random.uniform(0.5, 0.7)
        self.price_sensitivity = price_sensitivity if price_sensitivity is not None else random.uniform(0.5, 1.5)
        self.negative_sentiment_threshold = negative_sentiment_threshold if negative_sentiment_threshold is not None else random.uniform(
            0.5, 0.8)
        self.initial_buy_proportion = random.uniform(0.05, 0.2)
        self.max_multiple = pareto.rvs(3, scale=10) #TODO look into a better distribution


    def act(self, market, coin):
        if isinstance(market.network, nx.DiGraph):
            neighbors = list(market.network.predecessors(self.id))
        else:
            neighbors = list(market.network[self.id])


        if not neighbors:
            return

        neighbor_holdings_proportion = sum(
            market.agent_structure.get_agent(neighbor).holdings.get(coin.name, 0) > 0 for neighbor in neighbors) / len(neighbors)

        #If this is your first time buying, use your initial buy proportion
        if coin.name not in self.bought and neighbor_holdings_proportion >= self.threshold:
            max_affordable = self.budget // coin.price
            buy_amount = int(max_affordable * self.initial_buy_proportion)
            self.buy(coin, buy_amount)
            self.average_buy_prices[coin.name] = coin.price
            if (coin.name == "DogWifHat"):
                print(f"initial buying cheese {self.average_buy_prices[coin.name], neighbor_holdings_proportion}")
        #Still buy some if you already own the coin and have some more money. But the amount you are willing to buy
        #decreases exponentially relative to the amount of money you have left
        # elif neighbor_holdings_proportion >= self.threshold:
        #     # if coin.name=="DogWifHat":
        #     #     print(neighbor_holdings_proportion)
        #     max_affordable = self.budget // coin.price
        #     current_holdings = self.holdings.get(coin.name, 0)
        # 
        #     # Calculate the exponential decay factor based on the proportion of remaining budget
        #     decay_factor = np.exp(-current_holdings * coin.price / self.budget)
        # 
        #     # Adjust the buy amount based on the decay factor
        #     buy_amount = int(max_affordable * self.initial_buy_proportion)# * decay_factor)
        # 
        #     if buy_amount > 0:
        #         self.buy(coin, buy_amount)
        #         self.average_buy_prices[coin.name] = (self.average_buy_prices.get(coin.name,0) * current_holdings + coin.price * buy_amount) / (
        #                                                          current_holdings + buy_amount)
        #     if (coin.name == "DogWifHat"):
        #         print(f"buying cheese {self.average_buy_prices[coin.name]}")


        if self.holdings.get(coin.name, 0) > 0 and coin.name in self.average_buy_prices:
            current_profit_ratio = coin.price / self.average_buy_prices[coin.name]
            if current_profit_ratio >= self.max_multiple:
                # Automatically sell all holdings if profit exceeds the max multiple
                self.sell_all(coin)
            else:
                # Calculate the probability to sell based on an exponential function
                # Adjust the base of the exponential function according to your price sensitivity
                sell_probability = 1 - math.exp(-self.price_sensitivity * (current_profit_ratio - 1))

                if random.random() < sell_probability:
                    self.sell_all(coin)

                    if (coin.name == "DogWifHat"):
                        print(f"Selling cheese for profit: {coin.price, self.average_buy_prices[coin.name], sell_probability}")


        if self.holdings.get(coin.name, 0) > 0:
            negative_sentiment = sum(
                market.agent_structure.get_agent(neighbor).holdings.get(coin.name, 0) == 0 for neighbor in neighbors) / len(neighbors)
            if negative_sentiment > self.negative_sentiment_threshold:
                if(coin.name=="DogWifHat"):
                    print(f"selliong cheese cause of sentiment {self.negative_sentiment_threshold, negative_sentiment, neighbor_holdings_proportion}")
                self.sell_all(coin)
                if coin.name in self.average_buy_prices:
                    del self.average_buy_prices[coin.name]

    def get_type(self):
        return "LinearHerdingAgent"


class BudgetProportionHerdingAgent(Agent):
    """"
    Buys if the collective proportion of neighborhood investment is above a certain threshold
    Will sell for profit
    Will sell for sentiment
    """
    def __init__(self, id, budget, buy_threshold=None,
                 price_sensitivity=None,
                 negative_sentiment_threshold=None):
        super().__init__(id, budget)
        self.buy_threshold = buy_threshold if buy_threshold is not None else random.uniform(0.02, 0.1)
        self.price_sensitivity = price_sensitivity if price_sensitivity is not None else random.uniform(0.5, 1.5)
        self.negative_sentiment_threshold = negative_sentiment_threshold if negative_sentiment_threshold is not None else random.uniform(
            0.5, 0.8)
        self.initial_buy_proportion = random.uniform(0.05, 0.5)
        self.max_multiple = pareto.rvs(3, scale=10)  # TODO look into a better distribution

    def act(self, market, coin):
        if isinstance(market.network, nx.DiGraph):
            neighbors = list(market.network.predecessors(self.id))
        else:
            neighbors = list(market.network[self.id])

        if not neighbors:
            return

        # Calculate the total value of the coin held by all neighbors
        total_neighbor_coin_value = sum(
            market.agent_structure.get_agent(neighbor).holdings.get(coin.name, 0) * coin.price for neighbor in neighbors)

        # Calculate the total budget of all neighbors
        total_neighbor_budget = sum(market.agent_structure.get_agent(neighbor).budget for neighbor in neighbors)

        # Calculate the collective investment proportion of the neighborhood
        neighborhood_investment_proportion = total_neighbor_coin_value / total_neighbor_budget

        if (coin.name == "DogWifHat"):
            print(f"cheese neighbors {neighborhood_investment_proportion, self.buy_threshold}")

        if coin.name not in self.bought and neighborhood_investment_proportion >= self.buy_threshold:
            max_affordable = self.budget // coin.price
            buy_amount = int(max_affordable * self.initial_buy_proportion)
            self.buy(coin, buy_amount)
            self.average_buy_prices[coin.name] = coin.price
            if (coin.name == "DogWifHat"):
                print(f"first buying cheese {self.average_buy_prices[coin.name]}")
            # Still buy some if you already own the coin and have some more money. But the amount you are willing to buy
            # decreases exponentially relative to the amount of money you have left
        # elif neighborhood_investment_proportion >= self.buy_threshold:
        #     max_affordable = self.budget // coin.price
        #     current_holdings = self.holdings.get(coin.name, 0)
        #
        #     # Calculate the exponential decay factor based on the proportion of remaining budget
        #     decay_factor = np.exp(-current_holdings * coin.price / self.budget)
        #
        #     # Adjust the buy amount based on the decay factor
        #     buy_amount = int(max_affordable * self.initial_buy_proportion * decay_factor)
        #
        #     if buy_amount > 0:
        #         self.buy(coin, buy_amount)
        #         self.average_buy_prices[coin.name] = (self.average_buy_prices.get(coin.name,
        #                                                                           0) * current_holdings + coin.price * buy_amount) / (
        #                                                      current_holdings + buy_amount)
        #         # if (coin.name == "DogWifHat"):
        #             # print(f"buying cheese {self.average_buy_prices[coin.name]}")

        if self.holdings.get(coin.name, 0) > 0 and coin.name in self.average_buy_prices:
            current_profit_ratio = coin.price / self.average_buy_prices[coin.name]
            if current_profit_ratio >= self.max_multiple:
                # Automatically sell all holdings if profit exceeds the max multiple
                self.sell_all(coin)
            else:
                # Calculate the probability to sell based on an exponential function
                # Adjust the base of the exponential function according to your price sensitivity
                sell_probability = 1 - math.exp(-self.price_sensitivity * (current_profit_ratio - 1))

                if random.random() < sell_probability:
                    self.sell_all(coin)

                    if (coin.name == "DogWifHat"):
                        print(f"Selling cheese for profit: {coin.price, self.average_buy_prices[coin.name], sell_probability}")

        elif self.holdings.get(coin.name, 0) > 0:
            negative_sentiment = sum(
                market.agent_structure.get_agent(neighbor).holdings.get(coin.name, 0) == 0 for neighbor in neighbors) / len(neighbors)
            if negative_sentiment > self.negative_sentiment_threshold:
                self.sell_all(coin)
                if coin.name in self.average_buy_prices:
                    del self.average_buy_prices[coin.name]
                if (coin.name == "DogWifHat"):
                    print(f"selliong cheese cause of sentiment {self.negative_sentiment_threshold, negative_sentiment}")

    def get_type(self):
        return "BudgetProportionHerdingAgent"


class NeighborhoodProbabilisticInvestor(Agent):
    """
    Agent that buys and sell probabilistically based on the proportion of funds allocated to that coin in its neighborhood
    Also sells with the same logic, but uses a scaling factor sell_scaling_factor to dampen the probability since usually
    its rare for a significant amount of a neighborhoods budget to be invested in one asset

    Will sell for profit
    Will sell for sentiment
    Will sell to cut losses
    """
    def __init__(self, id, budget, price_sensitivity=None):
        super().__init__(id, budget)
        self.price_sensitivity = price_sensitivity if price_sensitivity is not None else random.uniform(0.5, 1.5)
        self.initial_buy_proportion = random.uniform(0.05, 0.5)
        self.max_multiple = pareto.rvs(3, scale=10)  # TODO look into a better distribution
        self.sell_scaling_factor = 0.2 #TODO adjust this

    def act(self, market, coin):
        if isinstance(market.network, nx.DiGraph):
            neighbors = list(market.network.predecessors(self.id))
        else:
            neighbors = list(market.network[self.id])

        if not neighbors:
            return

        # Calculate the total value of the coin held by all neighbors
        total_neighbor_coin_value = sum(
            market.agent_structure.get_agent(neighbor).holdings.get(coin.name, 0) * coin.price for neighbor in neighbors)

        # Calculate the total budget of all neighbors
        total_neighbor_budget = sum(market.agent_structure.get_agent(neighbor).budget for neighbor in neighbors)

        # Calculate the collective investment proportion of the neighborhood
        neighborhood_investment_proportion = total_neighbor_coin_value / total_neighbor_budget

        if coin.name not in self.bought and random.random() < neighborhood_investment_proportion:
            max_affordable = self.budget // coin.price
            buy_amount = int(max_affordable * self.initial_buy_proportion)
            self.buy(coin, buy_amount)
            self.average_buy_prices[coin.name] = coin.price
            if (coin.name == "DogWifHat"):
                print(f"first buying cheese {self.average_buy_prices[coin.name]}")

        proportion_not_invested = 1 - neighborhood_investment_proportion

        # Probabilistically sell based on the scaled proportion of wealth not invested
        if self.holdings.get(coin.name, 0) > 0:
            sell_probability = proportion_not_invested * self.sell_scaling_factor
            if random.random() < sell_probability:
                self.sell_all(coin)
                if coin.name in self.average_buy_prices:
                    del self.average_buy_prices[coin.name]

                if (coin.name == "DogWifHat"):
                    print(
                        f"Selling cheese due to sentiment: {coin.price, sell_probability}")

        #sell for profit somethines
        if self.holdings.get(coin.name, 0) > 0 and coin.name in self.average_buy_prices:
            current_profit_ratio = coin.price / self.average_buy_prices[coin.name]
            if current_profit_ratio >= self.max_multiple:
                # Automatically sell all holdings if profit exceeds the max multiple
                self.sell_all(coin)
            else:
                # Calculate the probability to sell based on an exponential function
                # Adjust the base of the exponential function according to your price sensitivity
                sell_probability = 1 - math.exp(-self.price_sensitivity * (current_profit_ratio - 1))

                if random.random() < sell_probability:
                    self.sell_all(coin)
                    if coin.name in self.average_buy_prices:
                        del self.average_buy_prices[coin.name]

                    if (coin.name == "DogWifHat"):
                        print(f"Selling cheese for profit: {coin.price, sell_probability}")


    def get_type(self):
        return "NeighborhoodProbabilisticInvestor"
