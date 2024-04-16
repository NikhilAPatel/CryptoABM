#Gets agents with the highest degrees and prints some stats about them
# top_degree_nodes = sorted(market.network.nodes(), key=lambda x: market.network.degree(x), reverse=True)[:5]
#
# for node in top_degree_nodes:
#     degree = market.network.degree(node)
#     agent_type = market.agent_structure.get_agent(node).get_type()
#     budget = market.agent_structure.get_agent(node).budget
#     print(f"Agent ID: {node}, Degree: {degree}, Type: {agent_type}, Budget: {budget}")
#
# lowest_degree_nodes = sorted(market.network.nodes(), key=lambda x: market.network.degree(x), reverse=False)[:5]
# for node in lowest_degree_nodes:
#     degree = market.network.degree(node)
#     agent_type = market.agent_structure.get_agent(node).get_type()
#     budget = market.agent_structure.get_agent(node).budget
#     print(f"Agent ID: {node}, Degree: {degree}, Type: {agent_type}, Budget: {budget}")