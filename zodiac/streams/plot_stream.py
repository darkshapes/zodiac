# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->


import asyncio

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx

from zodiac.streams import ModelStream


async def main():
    model_source = ModelStream()
    await model_source.model_graph()
    await model_source.trace_models("image", "speech")
    graph_copy = model_source._graph.intent_graph.to_undirected()
    nx_graph = nx.Graph(graph_copy)

    pos = nx.spring_layout(nx_graph, seed=7)  # positions for all nodes - seed for reproducibility

    # nodes
    nx.draw_networkx_nodes(nx_graph, pos, node_size=700)

    # edges
    # print(nx_graph.edges())
    # print(nx_graph.adjacency())
    path = nx.bidirectional_shortest_path(nx_graph, "image", "speech")
    path_list = [nx_graph[path[x]][path[x + 1]] for x in range(len(path) - 1)]
    nx.draw_networkx_edges(nx_graph, pos, edgelist=nx_graph.edges(), width=6)
    nx.draw_networkx_edges(nx_graph, pos, edgelist=path_list, width=6, alpha=0.5, edge_color="b", style="dashed")

    # node labels
    nx.draw_networkx_labels(nx_graph, pos, font_size=20, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(nx_graph, "weight")
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels)

    ax = plt.gca()
    ax.margins(0.08)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    asyncio.run(main())
