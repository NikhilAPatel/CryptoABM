import os
import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from Agent import *
import imageio
from tqdm import tqdm

class Cryptocurrency:
    def __init__(self, name, initial_price, ismeme):
        self.coinname = name
        self.price = initial_price
        self.initial_price = initial_price
        self.ismeme=ismeme


class CryptoMarket:
    def __init__(self, num_agents, initial_coin, airdrop_percentage, num_rational_agents):
        num_herding_agents = num_agents - num_rational_agents
        self.agents = ([RationalAgent(i, random.randint(1000, 10000)) for i in range(num_rational_agents)] +
                       [HerdingAgent(i, random.randint(1000, 10000)) for i in range(num_herding_agents)])
        self.coin = initial_coin
        self.network = self.create_network(num_agents)
        self.agent_types = {'RationalAgent': num_rational_agents, 'HerdingAgent': num_herding_agents}

        self.airdrop(random.choices(self.agents, k=int(len(self.agents)*airdrop_percentage)), 100)


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
        network_states = []  # List to store network states
        # Initialize a dictionary to count the number of agents holding the cryptocurrency for each type
        holdings_history = {agent_type: [0] * (num_iterations) for agent_type in self.agent_types}

        for t in tqdm(range(num_iterations)):
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
            color_map = ['green' if agent.holdings > 0 else 'grey' for agent in self.agents]
            network_states.append(color_map)

        return price_history, holdings_history, network_states

    def plot_price_history(self, price_history, holdings_history, show_graph=True):
        fig, axs = plt.subplots(2, 1, figsize=(12, 12), gridspec_kw={'height_ratios': [1, 1]})
        if show_graph:
            fig, axs = plt.subplots(3, 1, figsize=(12, 24), gridspec_kw={'height_ratios': [1, 1, 2]})

        # Plot the price history
        axs[0].plot(price_history, label='Price')
        axs[0].set_xlabel('Iteration')
        axs[0].set_ylabel('Price')
        axs[0].set_title('Cryptocurrency Price Simulation')
        axs[0].legend()

        # Plot the number of agents holding the cryptocurrency
        for agent_type, holdings in holdings_history.items():
            axs[1].plot(holdings, label=f'{agent_type} Holdings')
        axs[1].set_xlabel('Iteration')
        axs[1].set_ylabel('Number of Agents Holding')
        axs[1].set_title('Number of Agents Holding by Agent Type')
        axs[1].legend()

        if show_graph:
            # Draw the network structure
            self.draw_network(axs[2])
            axs[2].set_title('Network Structure of Agents')

        plt.tight_layout()
        plt.show()

    def draw_network(self, ax):
        # Define node colors based on agent type
        color_map = []
        for node in self.network:
            if isinstance(self.agents[node], RationalAgent):
                color_map.append('blue')  # Blue for RationalAgent
            else:
                color_map.append('red')  # Red for HerdingAgent

        pos = nx.spring_layout(self.network)  # Positioning the nodes of the network
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
btc = Cryptocurrency('CryptoCoin', 1.00, ismeme=False)

# Note: You would need to add the other agents to the market as well for a mixed-agent simulation.
market = CryptoMarket(num_agents=100, initial_coin=btc, airdrop_percentage=0, num_rational_agents=50)
price_history, holdings_history, network_states = market.simulate(100)
market.plot_price_history(price_history, holdings_history, show_graph=False)
market.generate_images_and_gif(network_states)
