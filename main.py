import os
from textwrap import wrap

import imageio
import matplotlib.pyplot as plt
from tqdm import tqdm
from Agent import *
from Airdrop import *
from CPN import *
from AgentStructure import AgentStructure

class Cryptocurrency:
    def __init__(self, name, initial_price, ismeme):
        self.name = name
        self.price = initial_price
        self.initial_price = initial_price
        self.is_meme = ismeme
        self.highest_price = 0


class CryptoMarket:
    def __init__(self, network_type, initial_coins, airdrop_strategies, agent_structure):
        self.num_agents = agent_structure.num_agents
        self.agent_structure = agent_structure
        self.agent_types = agent_structure.agent_types
        self.descriptor_string = f"{network_type}: {agent_structure.get_descriptor()} - {[airdrop_strategy.get_descriptor() for airdrop_strategy in airdrop_strategies]}"
        self.network_type = network_type
        self.airdrop_strategies = airdrop_strategies
        self.coins = initial_coins
        self.network = self.create_network()

    def create_network(self):
        if self.network_type == 'random':
            return nx.erdos_renyi_graph(self.num_agents, 0.1, directed=True)
        elif self.network_type == 'scale_free':
            return nx.barabasi_albert_graph(self.num_agents, 2)
        elif self.network_type == 'small_world':
            return nx.watts_strogatz_graph(self.num_agents, 4, 0.1)
        elif self.network_type == 'directed_random':
            return nx.gnp_random_graph(self.num_agents, 0.1)
        elif self.network_type == 'directed_scale_free':
            G = nx.DiGraph()
            G.add_nodes_from(range(self.num_agents))
            edges = nx.scale_free_graph(self.num_agents, alpha=0.41, beta=0.54, gamma=0.05, delta_in=0.2,
                                        delta_out=0).edges()
            G.add_edges_from(edges)
            return G
        elif self.network_type == 'directed_small_world':
            return nx.watts_strogatz_graph(self.num_agents, 4, 0.1, directed=True)
        elif self.network_type == "core_periphery":
            return create_core_periphery_network(self.num_agents, core_percent=0.1, core_connected_prob=0.8,
                                                 periphery_connected_prob=0.01)
        elif self.network_type == "directed_core_periphery":
            return create_directed_core_periphery_network(self.num_agents, core_percent=0.2, core_to_core_prob=0.5,
                                                          core_to_periphery_prob=0.5, periphery_to_periphery_prob=0.1,
                                                          periphery_to_core_prob=0.01)
        elif self.network_type == "multiple_core_periphery":
            return create_multiple_core_periphery_networks(total_agents=self.num_agents, networks_count=5, interlink_probability=.01, directed=False)
        elif self.network_type == "directed_multiple_core_periphery":
            return create_multiple_core_periphery_networks(total_agents=self.num_agents, networks_count=5, interlink_probability=.01, directed=True)

    def get_coin_price(self, coin_name):
        for coin in self.coins:
            if coin.name == coin_name:
                return coin.price
        return None

    def set_coin_price(self, coin_name, new_price):
        for coin in self.coins:
            if coin.name == coin_name:
                coin.price = new_price
                coin.highest_price = max(coin.highest_price, new_price)
                break

    def simulate(self, num_iterations):
        price_histories = {coin.name: [coin.price] for coin in self.coins}
        network_states = []
        net_trade_volume_histories = {coin.name: [] for coin in self.coins}

        holdings_histories = {coin.name: {agent_type: [0] * (num_iterations + 1) for agent_type in self.agent_types}
                              for coin in self.coins}
        asset_allocation_data = []

        for t in tqdm(range(num_iterations)):
            #Execute the airdrop when needed
            for airdrop_strategy in self.airdrop_strategies:
                if int(airdrop_strategy.time * num_iterations)==t:
                    airdrop_strategy.do_airdrop(market)
            #if we did an airdrop on the first iteration, lets update the holdings history just as a special exception
            if t==0:
                for coin in self.coins:
                    for agent in self.agent_structure.agents:
                        if agent.holdings.get(coin.name, 0) > 0:
                            holdings_histories[coin.name][agent.get_type()][0] += 1

            timestep_data = {'cash': sum(agent.budget for agent in self.agent_structure.agents)}
            for coin in self.coins:
                agent_holding_metrics = {agent_type: 0 for agent_type in self.agent_types}
                random.shuffle(self.agent_structure.agents)
                trade_volume = 0

                for agent in self.agent_structure.agents:
                    initial_holdings = agent.holdings.get(coin.name, 0)
                    initial_budget = agent.budget
                    agent.act(self, coin)

                    if agent.holdings.get(coin.name, 0) > 0:
                        agent_holding_metrics[agent.get_type()] += 1

                    change_in_holdings = agent.holdings.get(coin.name, 0) - initial_holdings
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

                    coin.price = max(coin.price, coin.initial_price * 0.01) #enforce a minimum price for the coin
                    coin.highest_price = max(coin.highest_price, coin.price)
                    trade_volume += change_in_holdings

                    price_histories[coin.name].append(coin.price)
                for agent_type in self.agent_types:
                    holdings_histories[coin.name][agent_type][t + 1] = agent_holding_metrics[agent_type]
                color_map = ['green' if agent.holdings.get(coin.name, 0) > 0 else 'grey' for agent in self.agent_structure.agents]
                network_states.append(color_map)
                net_trade_volume_histories[coin.name].append(trade_volume)
                timestep_data[coin.name] = sum(agent.holdings.get(coin.name, 0) for agent in self.agent_structure.agents)

            asset_allocation_data.append(timestep_data)

        return price_histories, holdings_histories, network_states, net_trade_volume_histories, asset_allocation_data

    def plot_price_history(self, price_histories, holdings_histories, net_trade_volume_histories, asset_allocation_data, show_graph=True):
        num_coins = len(self.coins)
        fig, axs = plt.subplots(4, 1, figsize=(12, 16), gridspec_kw={'height_ratios': [1, num_coins, 1, 1]})
        if show_graph:
            fig, axs = plt.subplots(5, 1, figsize=(12, 30), gridspec_kw={'height_ratios': [1, num_coins, 1, 1, 2]})

        for coin in self.coins:
            x_values = [i/self.num_agents for i in range(len(price_histories[coin.name]))]
            axs[0].plot(x_values, price_histories[coin.name], label=coin.name)
        axs[0].set_xlabel('Iteration')
        axs[0].set_ylabel('Price')
        axs[0].set_title('Cryptocurrency Price Simulation')
        axs[0].legend()

        for i, coin in enumerate(self.coins):
            for agent_type, holdings in holdings_histories[coin.name].items():
                axs[1].plot(holdings, label=f'{coin.name} - {agent_type} Holdings')
            axs[1].set_xlabel('Iteration')
            axs[1].set_ylabel('Number of Agents Holding')
            axs[1].set_title('Number of Agents Holding by Agent Type')
            axs[1].legend()

        for coin in self.coins:
            axs[2].bar(range(len(net_trade_volume_histories[coin.name])), net_trade_volume_histories[coin.name],
                       alpha=0.5, label=f'{coin.name} Net Trade Volume')
        axs[2].set_xlabel('Iteration')
        axs[2].set_ylabel('Net Trade Volume')
        axs[2].set_title('Net Trade Volume Over Time')
        axs[2].legend()

        asset_allocation = {'Uninvested Cash': []}
        for coin in self.coins:
            asset_allocation[coin.name] = []

        for t in range(len(asset_allocation_data)):
            total_wealth = asset_allocation_data[t]['cash']
            for coin in self.coins:
                total_wealth += asset_allocation_data[t][coin.name] * price_histories[coin.name][t]

            asset_allocation['Uninvested Cash'].append(asset_allocation_data[t]['cash'] / total_wealth * 100)
            for coin in self.coins:
                asset_allocation[coin.name].append(
                    asset_allocation_data[t][coin.name] * price_histories[coin.name][t] / total_wealth * 100)

        for asset, allocation in asset_allocation.items():
            axs[3].plot(allocation, label=asset)
        axs[3].set_xlabel('Iteration')
        axs[3].set_ylabel('Percentage of Total Wealth')
        axs[3].set_title('Asset Allocation Over Time')
        axs[3].legend()

        if show_graph:
            self.draw_network(axs[4])
            axs[4].set_title('Network Structure of Agents')

        fig.suptitle("\n".join(wrap(self.descriptor_string)))
        plt.tight_layout()
        fig.subplots_adjust(top=0.90)
        plt.show()
    def draw_network(self, ax):
        color_map = []
        for node in self.network:
            if isinstance(self.agent_structure.get_agent(node), RationalAgent):
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
eth = Cryptocurrency('Ethereum', 0.50, ismeme=False)
wif = Cryptocurrency('DogWifHat', .25, ismeme=True)
cheese = Cryptocurrency('Cheese', .25, ismeme=True)

leader_airdrop_strategy = LeaderAirdropStrategy(btc, 0.3, 100, 0)
wif_airdrop_strategy = BiggestHoldersAirdropStrategy(wif, 0.4, 10000, 0.5, btc)

agent_structure = AgentStructure(100)
agent_structure.add_agents(RationalAgent, 20)
agent_structure.add_agents(NeighborhoodProbabilisticInvestor, 80)

market = CryptoMarket(network_type='scale_free', initial_coins=[btc, wif],
                      airdrop_strategies=[leader_airdrop_strategy, wif_airdrop_strategy], agent_structure = agent_structure)

agent_structure.budgets_based_on_popularity(market) #has to be done after the market is defined

price_histories, holdings_histories, network_states, net_trade_volume_histories, asset_allocation_data = market.simulate(100)
market.plot_price_history(price_histories, holdings_histories, net_trade_volume_histories, asset_allocation_data, show_graph=True)
for coin in market.coins:
    print(f"Final {coin.name} Price: {price_histories[coin.name][-1]:.2f}, Max Price: {coin.highest_price:.2f}")

# market.generate_images_and_gif(network_states)

