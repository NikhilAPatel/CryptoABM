# CryptoABM

## Introduction

The cryptocurrency market is a unique and volatile environment that differs significantly from traditional stock markets. The lack of regulation leads to the proliferation of market manipulation and unethical practices. The barrier to entry is significantly lower – anyone can create a new cryptocurrency in a matter of seconds using platforms like pump.fun – leading to many new tokens every day, many of which lack solid fundamentals. The 24/7 nature of crypto trading can also exacerbate price movements and contribute to higher volatility, as there are no cooling-off periods or market closures. However, perhaps the most significant difference is that many cryptocurrencies, especially "meme-coins" like WIF or Doge, hold little to no intrinsic value. Instead, their prices are often determined almost entirely by speculation fueled by strong community sentiments, emotional trading, and the effects of rapid information diffusion, herding behavior, and the formation of echo chambers that amplify certain narratives or trading strategies. New coins will often try to gain initial popularity by distributing free coins to users through a process called "airdropping", leveraging network effects to drive up prices. 

## Objectives

We use agent-based modeling to investigate the emergence of herding behavior under different market conditions and the role of airdrops and reputation under the lens of a budget-constrained maximization problem. The goal will be to analyze the performance of different influence maximization algorithms and heuristics under various network structures and agent type distributions. By incorporating the unique attributes of the cryptocurrency market, the model will provide valuable insights into the factors driving the highly speculative and volatile nature of this market. This can inform the development of more effective market mechanisms, regulatory policies, and investment strategies.

## Types of Networks

### 1. Core-Periphery Network

**Characteristics**: A core-periphery structure consists of a dense core of nodes that are highly interconnected and a periphery of nodes that are less connected and mostly linked to the core rather than to each other.

**Relevance**: This structure could simulate markets where there are a few highly influential and connected traders or institutions (the core), surrounded by a large number of less influential market participants (the periphery). Such models are useful for studying how central institutions or influential traders affect market trends and how peripheral participants react.

### 2. Directed Networks

**Characteristics**: In directed networks, connections have a direction, indicating that one node can influence another but not necessarily vice versa.

**Relevance**: Directed networks are useful in markets where the influence is not reciprocal. For example, influencers or news sources may impact many traders' decisions without being affected in return. This is particularly relevant for studying information dissemination and its impact on market behavior.

### 3. Small World

**Characteristics**: Small-world networks are characterized by high clustering coefficients and short average path lengths. In these networks, most nodes are not neighbors of one another, but most nodes can be reached from every other node by a small number of hops or steps.

**Relevance**: Small-world networks can simulate markets where information or influence can spread quickly, even between seemingly distant participants. This is relevant for studying how rumors, news, or trading strategies can rapidly propagate and affect market behavior.

### 4. Scale Free

**Characteristics**: In a scale-free network, the degree distribution follows a power law, with a few highly connected nodes (hubs) and many nodes with low degrees.

**Relevance**: Scale-free networks are useful for modeling markets where a few key players or influencers have a disproportionately large impact on the market. This can help study the role of these key players in shaping market trends and the resilience of the market to their actions.

### 5. Random

**Characteristics**: In a random network, nodes are connected randomly with a certain probability.

**Relevance**: Random networks serve as a baseline for comparison with other, more structured network types. They can also represent markets where interactions are relatively uniform and not strongly influenced by any particular structure.

## Installation and Usage

<!-- Add instructions for installing and running the CryptoABM simulation -->

## Contribution Guidelines

<!-- Add guidelines for contributing to the project -->

## License

<!-- Specify the license under which the project is distributed -->