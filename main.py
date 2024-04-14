import os
import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from Agent import *
import imageio
from tqdm import tqdm
import scipy as sp
from CPN import *

class Cryptocurrency:
    def __init__(self, name, initial_price, ismeme):
        self.coinname = name
        self.price = initial_price
        self.initial_price = initial_price
        self.ismeme = ismeme


class CryptoMarket:
    def __init__(self, num_agents, network_type, initial_coins, airdrop_percentage, airdrop_amount, num_rational_agents):
        self.descriptor_string = f"{num_agents} agents, {num_rational_agents} rational - {airdrop_percentage}% airdrop"
        self.network_type = network_type
        id_generator = IDGenerator(num_agents)
        num_herding_agents = num_agents - num_rational_agents
        self.agents = ([RationalAgent(id_generator.get_next_id(), budget=random.randint(1000, 10000)) for i in
                        range(num_rational_agents)] +
                       [BudgetProportionHerdingAgent(id_generator.get_next_id(), budget=random.randint(1000, 10000)) for i in
                        range(num_herding_agents)])
        random.shuffle(self.agents)
        self.coins = initial_coins
        self.network = self.create_network()
        self.agent_types = {'RationalAgent': num_rational_agents, 'BudgetProportionHerdingAgent': num_herding_agents}

        for coin in self.coins:
            self.airdrop(random.choices(self.agents, k=int(len(self.agents) * airdrop_percentage)), coin, airdrop_amount)

    def create_network(self):
        if self.network_type == 'random':
            return nx.erdos_renyi_graph(len(self.agents), 0.1, directed=True)
        elif self.network_type == 'scale_free':
            return nx.barabasi_albert_graph(len(self.agents), 2)
        elif self.network_type == 'small_world':
            return nx.watts_strogatz_graph(len(self.agents), 4, 0.1)
        elif self.network_type == 'directed_random':
            return nx.gnp_random_graph(len(self.agents), 0.1)
        elif self.network_type == 'directed_scale_free':
            G = nx.DiGraph()
            G.add_nodes_from(range(len(self.agents)))
            edges = nx.scale_free_graph(len(self.agents), alpha=0.41, beta=0.54, gamma=0.05, delta_in=0.2,
                                        delta_out=0).edges()
            G.add_edges_from(edges)
            return G
        elif self.network_type == 'directed_small_world':
            return nx.watts_strogatz_graph(len(self.agents), 4, 0.1, directed=True)
        elif self.network_type == "core_periphery":
            return create_core_periphery_network(len(self.agents), core_percent=0.1, core_connected_prob=0.8,
                                                 periphery_connected_prob=0.01)
        elif self.network_type == "directed_core_periphery":
            return create_directed_core_periphery_network(len(self.agents), core_percent=0.2, core_to_core_prob=0.5,
                                                          core_to_periphery_prob=0.5, periphery_to_periphery_prob=0.1,
                                                          periphery_to_core_prob=0.01)
        elif self.network_type == "multiple_core_periphery":
            return create_multiple_core_periphery_networks(total_agents=len(self.agents), networks_count=5,
                                                           interlink_probability=0.01, directed=False)
        elif self.network_type == "directed_multiple_core_periphery":
            return create_multiple_core_periphery_networks(total_agents=len(self.agents), networks_count=5,
                                                           interlink_probability=0.01, directed=True)

    def get_coin_price(self, coin_name):
        for coin in self.coins:
            if coin.coinname == coin_name:
                return coin.price
        return None

    def set_coin_price(self, coin_name, new_price):
        for coin in self.coins:
            if coin.coinname == coin_name:
                coin.price = new_price
                break

    def airdrop(self, agents, coin, amount):
        for agent in agents:
            agent.holdings[coin.coinname] = agent.holdings.get(coin.coinname, 0) + amount
            agent.average_buy_prices[coin] = 0

    def simulate(self, num_iterations):
        price_histories = {coin.coinname: [coin.price] for coin in self.coins}
        network_states = []
        net_trade_volume_histories = {coin.coinname: [] for coin in self.coins}
        holdings_histories = {coin.coinname: {agent_type: [0] * (num_iterations + 1) for agent_type in self.agent_types}
                              for coin in self.coins}

        for coin in self.coins:
            for agent in self.agents:
                if agent.holdings.get(coin.coinname, 0) > 0:
                    holdings_histories[coin.coinname][agent.get_type()][0] += 1

        for t in tqdm(range(num_iterations)):
            for coin in self.coins:
                agent_holding_metrics = {agent_type: 0 for agent_type in self.agent_types}
                random.shuffle(self.agents)
                trade_volume = 0

                for agent in self.agents:
                    initial_holdings = agent.holdings.get(coin.coinname, 0)
                    initial_budget = agent.budget
                    agent.act(self, coin)

                    if agent.holdings.get(coin.coinname, 0) > 0:
                        agent_holding_metrics[agent.get_type()] += 1

                    change_in_holdings = agent.holdings.get(coin.coinname, 0) - initial_holdings
                    change_in_budget = agent.budget - initial_budget

                    if change_in_holdings > 0:
                        bought = change_in_holdings
                        spent = -change_in_budget
                        price_change_factor = 1 + (bought / (spent / coin.price)) * 0.05
                        coin.price *= price_change_factor
                    elif change_in_holdings < 0:
                        sold = -change_in_holdings
                        earned = change_in_budget
                        price_change_factor = max(0, 1 - (sold / (earned / coin.price)) * 0.05)
                        coin.price *= price_change_factor

                    coin.price = max(coin.price, coin.initial_price * 0.01)
                    trade_volume += change_in_holdings

                price_histories[coin.coinname].append(coin.price)
                for agent_type in self.agent_types:
                    holdings_histories[coin.coinname][agent_type][t + 1] = agent_holding_metrics[agent_type]
                color_map = ['green' if agent.holdings.get(coin.coinname, 0) > 0 else 'grey' for agent in self.agents]
                network_states.append(color_map)
                net_trade_volume_histories[coin.coinname].append(trade_volume)

        return price_histories, holdings_histories, network_states, net_trade_volume_histories

    def plot_price_history(self, price_histories, holdings_histories, net_trade_volume_histories, show_graph=True):
        num_coins = len(self.coins)
        fig, axs = plt.subplots(3, 1, figsize=(12, 12), gridspec_kw={'height_ratios': [1, num_coins, 1]})
        if show_graph:
            fig, axs = plt.subplots(4, 1, figsize=(12, 24), gridspec_kw={'height_ratios': [1, num_coins, 1, 2]})

        for coin in self.coins:
            axs[0].plot(price_histories[coin.coinname], label=coin.coinname)
        axs[0].set_xlabel('Iteration')
        axs[0].set_ylabel('Price')
        axs[0].set_title('Cryptocurrency Price Simulation')
        axs[0].legend()

        for i, coin in enumerate(self.coins):
            for agent_type, holdings in holdings_histories[coin.coinname].items():
                axs[1].plot(holdings, label=f'{coin.coinname} - {agent_type} Holdings')
            axs[1].set_xlabel('Iteration')
            axs[1].set_ylabel('Number of Agents Holding')
            axs[1].set_title('Number of Agents Holding by Agent Type')
            axs[1].legend()

        for coin in self.coins:
            axs[2].bar(range(len(net_trade_volume_histories[coin.coinname])), net_trade_volume_histories[coin.coinname],
                       alpha=0.5, label=f'{coin.coinname} Net Trade Volume')
        axs[2].set_xlabel('Iteration')
        axs[2].set_ylabel('Net Trade Volume')
        axs[2].set_title('Net Trade Volume Over Time')
        axs[2].legend()

        if show_graph:
            self.draw_network(axs[3])
            axs[3].set_title('Network Structure of Agents')

        fig.suptitle(self.descriptor_string)
        plt.tight_layout()
        fig.subplots_adjust(top=0.90)
        plt.show()
    def draw_network(self, ax):
        color_map = []
        for node in self.network:
            if isinstance(self.agents[node], RationalAgent):
                color_map.append('blue')
            else:
                color_map.append('red')

        pos = nx.spring_layout(self.network)
        nx.draw(self.network, pos, node_color=color_map, with_labels=True, ax=ax)

    def generate_images_and_gif(self, network_states, output_filename='network_behavior.gif'):
        frames_directory = 'network_frames'
        os.makedirs(frames_directory, exist_ok=True)  # Ensure the directory exists

        pos = nx.spring_layout(self.network, seed=42)  # Use a fixed layout

        for iteration, state in enumerate(network_states):
            fig, ax = plt.subplots(figsize=(8, 6))
            nx.draw(self.network, pos, node_color=state, with_labels=True, node_size=300, ax=ax)
            ax.set_title(f'Iteration {iteration}')
            plt.savefig(f"{frames_directory}/frame_{iteration:04d}.png")
            plt.close()

        # Creating GIF from frames
        images = []
        for file_name in sorted(os.listdir(frames_directory)):
            if file_name.endswith('.png'):
                file_path = os.path.join(frames_directory, file_name)
                images.append(imageio.imread(file_path))
        imageio.mimsave(output_filename, images, fps=5)  # Adjust fps to control speed of the GIF


# Example usage
btc = Cryptocurrency('Bitcoin', 1.00, ismeme=False)
# eth = Cryptocurrency('Ethereum', 0.50, ismeme=False)
wif = Cryptocurrency('DogWifHat', 0.25, ismeme=True)

market = CryptoMarket(num_agents=1000, network_type='multiple_core_periphery', initial_coins=[btc],
                      airdrop_percentage=.75, airdrop_amount=10000, num_rational_agents=500)
price_histories, holdings_histories, network_states, net_trade_volume_histories = market.simulate(100)
market.plot_price_history(price_histories, holdings_histories, net_trade_volume_histories, show_graph=False)
for coin in market.coins:
    print(f"Final {coin.coinname} Price: {price_histories[coin.coinname][-1]}")
