import random
import networkx as nx
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


class Agent:
    def __init__(self, id, budget):
        self.id = id
        self.budget = budget
        self.holdings = {}
        self.average_buy_prices = {}

    def buy(self, coin, amount):
        cost = amount * coin.price
        if self.budget >= cost:
            self.budget -= cost
            self.holdings[coin.coinname] = self.holdings.get(coin.coinname, 0) + amount
            return amount
        return 0

    def sell(self, coin, amount):
        if self.holdings.get(coin.coinname, 0) >= amount:
            self.holdings[coin.coinname] -= amount
            self.budget += amount * coin.price
            return amount
        return 0

    def act(self, market, coin):
        pass

    def get_type(self):
        pass


class RationalAgent(Agent):
    """
    A type of agent that seeks to trade rationally. When instantiated, it comes up with
    a rational determination for the fair market value of a coin. The agent will simply buy below this
    value and attempt to sell above it. It will only invest up to 20% of its networth in a coin. This agent will not engage in trading memecoins.
    """

    def __init__(self, id, budget):
        super().__init__(id, budget)
        self.fair_values = {}

    def determine_fair_value(self, coin):
        self.fair_values[coin.coinname] = np.random.normal(coin.initial_price, coin.initial_price * 0.1)

    def act(self, market, coin):
        if coin.coinname not in self.fair_values:
            self.determine_fair_value(coin)

        if coin.ismeme:
            return

        if coin.price < self.fair_values[coin.coinname]:
            max_affordable = self.budget // coin.price
            try:
                buy_amount = random.randint(1, int(max(max_affordable, 1) * 0.2))
            except ValueError:
                buy_amount = 0
            self.buy(coin, buy_amount)
        elif coin.price > self.fair_values[coin.coinname] and self.holdings.get(coin.coinname, 0) > 0:
            sell_amount = random.randint(1, self.holdings[coin.coinname])
            self.sell(coin, sell_amount)

    def get_type(self):
        return "RationalAgent"


class LinearHerdingAgent(Agent):
    def __init__(self, id, budget, threshold=None, profit_threshold=None, price_sensitivity=None,
                 negative_sentiment_threshold=None):
        super().__init__(id, budget)
        self.threshold = threshold if threshold is not None else random.uniform(0.3, 0.7)
        self.profit_threshold = profit_threshold if profit_threshold is not None else random.uniform(1.2, 2.0)
        self.price_sensitivity = price_sensitivity if price_sensitivity is not None else random.uniform(0.5, 1.5)
        self.negative_sentiment_threshold = negative_sentiment_threshold if negative_sentiment_threshold is not None else random.uniform(
            0.5, 0.8)
        self.initial_buy_proportion = random.uniform(0.05, 0.2)

    def act(self, market, coin):
        if isinstance(market.network, nx.DiGraph):
            neighbors = list(market.network.predecessors(self.id))
        else:
            neighbors = list(market.network[self.id])

        if not neighbors:
            return

        neighbor_holdings_proportion = sum(
            market.agents[neighbor].holdings.get(coin.coinname, 0) > 0 for neighbor in neighbors) / len(neighbors)

        if self.holdings.get(coin.coinname, 0) == 0 and neighbor_holdings_proportion >= self.threshold:
            max_affordable = self.budget // coin.price
            buy_amount = int(max_affordable * self.initial_buy_proportion)
            self.buy(coin, buy_amount)
            self.average_buy_prices[coin.coinname] = coin.price

        if self.holdings.get(coin.coinname, 0) > 0 and coin.coinname in self.average_buy_prices:
            current_profit = coin.price / self.average_buy_prices[coin.coinname]
            # TODO look into sell logic
            sell_probability = (1 - neighbor_holdings_proportion) * (
                    current_profit / (self.profit_threshold * self.price_sensitivity)) + \
                               (neighbor_holdings_proportion) * (current_profit - self.profit_threshold) / (
                                       current_profit + 1)
            if random.random() < sell_probability:
                self.sell(coin, self.holdings[coin.coinname])
                del self.average_buy_prices[coin.coinname]

        if self.holdings.get(coin.coinname, 0) > 0:
            negative_sentiment = sum(
                market.agents[neighbor].holdings.get(coin.coinname, 0) == 0 for neighbor in neighbors) / len(neighbors)
            if negative_sentiment > self.negative_sentiment_threshold:
                self.sell(coin, self.holdings[coin.coinname])
                if coin.coinname in self.average_buy_prices:
                    del self.average_buy_prices[coin.coinname]

    def get_type(self):
        return "LinearHerdingAgent"


class BudgetProportionHerdingAgent(Agent):
    def __init__(self, id, budget, buy_threshold=None, profit_threshold=None,
                 price_sensitivity=None,
                 negative_sentiment_threshold=None):
        super().__init__(id, budget)
        self.buy_threshold = buy_threshold if buy_threshold is not None else random.uniform(0.2, 0.5)
        self.profit_threshold = profit_threshold if profit_threshold is not None else random.uniform(1.2, 2.0)
        self.price_sensitivity = price_sensitivity if price_sensitivity is not None else random.uniform(0.5, 1.5)
        self.negative_sentiment_threshold = negative_sentiment_threshold if negative_sentiment_threshold is not None else random.uniform(
            0.5, 0.8)
        self.initial_buy_proportion = random.uniform(0.05, 0.5)

    def act(self, market, coin):
        if isinstance(market.network, nx.DiGraph):
            neighbors = list(market.network.predecessors(self.id))
        else:
            neighbors = list(market.network[self.id])

        if not neighbors:
            return

        # Calculate the total value of the coin held by all neighbors
        total_neighbor_coin_value = sum(
            market.agents[neighbor].holdings.get(coin.coinname, 0) * coin.price for neighbor in neighbors)

        # Calculate the total budget of all neighbors
        total_neighbor_budget = sum(market.agents[neighbor].budget for neighbor in neighbors)

        # Calculate the collective investment proportion of the neighborhood
        neighborhood_investment_proportion = total_neighbor_coin_value / total_neighbor_budget

        print(neighborhood_investment_proportion)

        if self.holdings.get(coin.coinname, 0) == 0 and neighborhood_investment_proportion >= self.buy_threshold:
            max_affordable = self.budget // coin.price
            buy_amount = int(max_affordable * self.initial_buy_proportion)
            self.buy(coin, buy_amount)
            self.average_buy_prices[coin.coinname] = coin.price

        if self.holdings.get(coin.coinname, 0) > 0 and coin.coinname in self.average_buy_prices:
            current_profit = coin.price / self.average_buy_prices[coin.coinname]
            sell_probability = (1 - neighborhood_investment_proportion) * (
                        current_profit / (self.profit_threshold * self.price_sensitivity)) + \
                               (neighborhood_investment_proportion) * (current_profit - self.profit_threshold) / (
                                           current_profit + 1)
            if random.random() < sell_probability:
                self.sell(coin, self.holdings[coin.coinname])
                del self.average_buy_prices[coin.coinname]

        if self.holdings.get(coin.coinname, 0) > 0:
            negative_sentiment = sum(
                market.agents[neighbor].holdings.get(coin.coinname, 0) == 0 for neighbor in neighbors) / len(neighbors)
            if negative_sentiment > self.negative_sentiment_threshold:
                self.sell(coin, self.holdings[coin.coinname])
                if coin.coinname in self.average_buy_prices:
                    del self.average_buy_prices[coin.coinname]

    def get_type(self):
        return "BudgetProportionHerdingAgent"
