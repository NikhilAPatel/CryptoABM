import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from Agent import *


class Cryptocurrency:
    def __init__(self, name, initial_price, ismeme):
        self.coinname = name
        self.price = initial_price
        self.initial_price = initial_price
        self.ismeme=ismeme


class CryptoMarket:
    def __init__(self, num_agents, initial_coin):
        num_rational_agents = 20
        num_herding_agents = num_agents - num_rational_agents
        self.agents = ([RationalAgent(i, random.randint(1000, 10000)) for i in range(num_rational_agents)] +
                       [HerdingAgent(i, random.randint(1000, 10000)) for i in range(num_herding_agents)])
        self.coin = initial_coin
        self.network = self.create_network(num_agents)
        self.agent_types = {'RationalAgent': num_rational_agents, 'HerdingAgent': num_herding_agents}


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
        # Initialize a dictionary to count the number of agents holding the cryptocurrency for each type
        holdings_history = {agent_type: [0] * (num_iterations) for agent_type in self.agent_types}

        self.airdrop(self.agents, 100)

        for t in range(num_iterations):
            agent_holding_metrics = {agent_type: 0 for agent_type in self.agent_types}

            # Shuffle the agents to randomize the order of their actions
            random.shuffle(self.agents)

            # Each agent acts based on its type
            for agent in self.agents:
                # Record the state before the agent acts
                initial_holdings = agent.holdings
                initial_budget = agent.budget
                agent.act(self)

                # Update the holding metrics
                if agent.holdings>0:
                    agent_holding_metrics[agent.get_type()] += 1

                # Calculate the net demand and adjust the price accordingly
                change_in_holdings = agent.holdings - initial_holdings
                change_in_budget = agent.budget - initial_budget

                if change_in_holdings > 0:  # Agent bought coins
                    bought = change_in_holdings
                    spent = -change_in_budget
                    price_change_factor = 1 + (bought / (spent / self.coin.price)) * 0.05
                    self.coin.price *= price_change_factor
                elif change_in_holdings < 0:  # Agent sold coins
                    sold = -change_in_holdings
                    earned = change_in_budget
                    price_change_factor = max(0, 1 - (sold / (earned / self.coin.price)) * 0.05)
                    self.coin.price *= price_change_factor

                # Ensure the price doesn't fall below a minimum threshold
                self.coin.price = max(self.coin.price, self.coin.initial_price * 0.01)


            # Record the price and update holdings for each agent type after all agents have acted
            price_history.append(self.coin.price)
            for agent_type in self.agent_types:
                holdings_history[agent_type][t]=agent_holding_metrics[agent_type]

        return price_history, holdings_history

    def plot_price_history(self, price_history, holdings_history):
        fig, axs = plt.subplots(2, 1, figsize=(12, 12))

        axs[0].plot(price_history, label='Price')
        axs[0].set_xlabel('Iteration')
        axs[0].set_ylabel('Price')
        axs[0].set_title('Cryptocurrency Price Simulation')
        axs[0].legend()

        for agent_type, holdings in holdings_history.items():
            axs[1].plot(holdings, label=f'{agent_type} Holdings')
        axs[1].set_xlabel('Iteration')
        axs[1].set_ylabel('Number of Agents Holding')
        axs[1].set_title('Number of Agents Holding by Agent Type')
        axs[1].legend()

        plt.tight_layout()
        plt.show()


# Example usage
btc = Cryptocurrency('CryptoCoin', 1.00, ismeme=False)

# Note: You would need to add the other agents to the market as well for a mixed-agent simulation.
market = CryptoMarket(num_agents=100, initial_coin=btc)
price_history, holdings_history = market.simulate(100)
market.plot_price_history(price_history, holdings_history)
