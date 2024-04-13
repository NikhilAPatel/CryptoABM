import random
import networkx as nx
import matplotlib.pyplot as plt


class Cryptocurrency:
    def __init__(self, name, initial_price, is_meme_coin=False):
        self.name = name
        self.price = initial_price
        self.is_meme_coin = is_meme_coin
        self.initial_price = initial_price


class Agent:
    def __init__(self, id, budget, agent_type):
        self.id = id
        self.budget = budget
        self.portfolio = {}
        self.agent_type = agent_type

    def buy(self, coin, amount):
        if self.budget >= amount * coin.price:
            if coin.name in self.portfolio:
                self.portfolio[coin.name] += amount
            else:
                self.portfolio[coin.name] = amount
            self.budget -= amount * coin.price
            return True
        return False

    def sell(self, coin, amount):
        if coin.name in self.portfolio and self.portfolio[coin.name] >= amount:
            self.portfolio[coin.name] -= amount
            self.budget += amount * coin.price
            return True
        return False

    def act(self, market):
        pass


class RationalAgent(Agent):
    def act(self, market):
        for coin_name, coin in market.coins.items():
            if coin.price < market.get_fair_value(coin_name):
                self.buy(coin, random.randint(1, 10))
            elif coin.price > market.get_fair_value(coin_name):
                self.sell(coin, random.randint(1, 10))


class HerdingAgent(Agent):
    def act(self, market):
        for coin_name, coin in market.coins.items():
            if market.get_sentiment(coin_name) > 0.5:
                self.buy(coin, random.randint(1, 10))
            else:
                self.sell(coin, random.randint(1, 10))


class MemeCoinAgent(Agent):
    def act(self, market):
        meme_coins = [coin for coin in market.coins.values() if coin.is_meme_coin]
        if len(meme_coins) > 0:
            coin = random.choice(meme_coins)
            self.buy(coin, random.randint(1, 10))


class SniperAgent(Agent):
    def act(self, market):
        for coin_name, coin in market.coins.items():
            if coin.price < coin.initial_price * 0.5:
                self.buy(coin, random.randint(1, 10))
            elif coin.price > coin.initial_price * 2:
                self.sell(coin, random.randint(1, 10))


class CryptoMarket:
    def __init__(self, num_agents, network_type, initial_coins, agent_types):
        self.agents = []
        for i in range(num_agents):
            agent_type = random.choice(agent_types)
            self.agents.append(agent_type(i, random.randint(1000, 10000), agent_type.__name__))

        self.coins = {coin.name: coin for coin in initial_coins}
        self.network = self.create_network(network_type)

    def create_network(self, network_type):
        if network_type == 'random':
            return nx.erdos_renyi_graph(len(self.agents), 0.1)
        elif network_type == 'scale_free':
            return nx.barabasi_albert_graph(len(self.agents), 2)
        elif network_type == 'small_world':
            return nx.watts_strogatz_graph(len(self.agents), 4, 0.1)

    def airdrop(self, coin, amount):
        for agent in self.agents:
            agent.portfolio[coin.name] = amount

    def get_coin_price(self, coin_name):
        return self.coins[coin_name].price

    def set_coin_price(self, coin_name, new_price):
        self.coins[coin_name].price = new_price

    def get_fair_value(self, coin_name):
        return self.coins[coin_name].initial_price

    def get_sentiment(self, coin_name):
        return sum(coin_name in agent.portfolio for agent in self.agents) / len(self.agents)

    def simulate(self, num_iterations):
        price_history = {coin_name: [coin.price] for coin_name, coin in self.coins.items()}

        for i in range(num_iterations):
            for agent in self.agents:
                agent.act(self)

            for coin_name, coin in self.coins.items():
                sentiment = self.get_sentiment(coin_name)
                self.set_coin_price(coin_name, coin.price * (1 + sentiment))
                price_history[coin_name].append(coin.price)

        self.plot_price_history(price_history)

    def plot_price_history(self, price_history):
        plt.figure(figsize=(12, 6))
        for coin_name, prices in price_history.items():
            plt.plot(range(len(prices)), prices, label=coin_name)

        plt.xlabel('Iteration')
        plt.ylabel('Price')
        plt.title('Cryptocurrency Price History')
        plt.legend()
        plt.show()


# Example usage
initial_coins = [
    Cryptocurrency('BTC', 50000),
    Cryptocurrency('ETH', 3000),
    Cryptocurrency('DOGE', 0.5, is_meme_coin=True)
]

agent_types = [RationalAgent, HerdingAgent, MemeCoinAgent, SniperAgent]
market = CryptoMarket(100, 'scale_free', initial_coins, agent_types)

# Airdrop a new meme coin
new_coin = Cryptocurrency('MEME', 0.01, is_meme_coin=True)
market.coins[new_coin.name] = new_coin
market.airdrop(new_coin, 100)

market.simulate(50)