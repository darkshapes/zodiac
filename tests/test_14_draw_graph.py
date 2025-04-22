# import networkx as nx
# from nnll_14 import calculate_graph
# import matplotlib.pyplot as plt
# import numpy as np

# from nnll_15.constants import LibType


# def draw_matplot_labeled(nx_graph: nx.Graph) -> None:
#     nx_graph = calculate_graph()
#     path = nx.bidirectional_shortest_path(nx_graph, "text", "image")
#     path_edges = list(zip(path, path[1:]))
#     edge_colors = ["red" if edge in path_edges or tuple(reversed(edge)) in path_edges else "black" for edge in nx_graph.edges()]
#     pos = nx.spring_layout(nx_graph)
#     nx.draw_networkx_nodes(nx_graph, pos)
#     nx.draw_networkx_edges(nx_graph, pos, edge_color=edge_colors)
#     nx.draw_networkx_labels(nx_graph, pos)
#     # nx.draw_networkx_edges(nx_graph, pos)
#     # nx.draw_networkx_edges(nx_graph, pos, edge_labels={(u, v): d for u, v, d in nx_graph.edges(data=True)})
#     nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels={(u, v): d for u, v, d in nx_graph.edges(data=True)}, font_size=3, alpha=0.5, rotate=False)
#     plt.show()


# def draw_matplot_circular() -> None:
#     nx_graph = calculate_graph()
#     path = nx.bidirectional_shortest_path(nx_graph, "image", "speech")
#     path_edges = list(zip(path, path[1:]))
#     edge_colors = ["red" if edge in path_edges or tuple(reversed(edge)) in path_edges else "black" for edge in nx_graph.edges()]
#     pos = nx.circular_layout(nx_graph)
#     nx.draw_networkx_nodes(nx_graph, pos)
#     nx.draw_networkx_edges(nx_graph, pos, edge_color=edge_colors)
#     nx.draw_networkx_labels(nx_graph, pos)
#     nx.draw_circular(nx_graph)
#     plt.show()


# def draw_matplot_graphviz() -> None:
#     nx_graph = calculate_graph()
#     path = nx.bidirectional_shortest_path(nx_graph, "image", "speech")
#     path_edges = list(zip(path, path[1:]))
#     edge_colors = ["red" if edge in path_edges or tuple(reversed(edge)) in path_edges else "black" for edge in nx_graph.edges()]
#     pos = nx.nx_agraph.graphviz_layout(nx_graph, prog="twopi", root=0)
#     options = {"with_labels": False, "alpha": 0.5, "node_size": 15}
#     nx.draw(nx_graph, pos, node_color=edge_colors, **options)
#     plt.show()


# def draw_matplot_weights() -> None:
#     nx_graph = calculate_graph()
#     pos = nx.spring_layout(nx_graph, scale=20, k=3 / np.sqrt(nx_graph.order()))
#     nx.draw(nx_graph, pos=pos, node_color="lightblue", with_labels=True, node_size=500)
#     labels = nx.get_edge_attributes(nx_graph, "weight")
#     nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=labels)
#     plt.show()


# if __name__ == "__main__":
#     # draw_matplot_weights()
#     draw_matplot_circular()


# # from textual.app import App, ComposeResult
# # from textual.widgets import Static
# # from textual_plot import HiResMode  # , PlotWidget
# # from textual_plotext import PlotextPlot
# # from networkx import convert_node_labels_to_integers
# # import numpy as np
# # from typing import Sequence
# # class MinimalApp(App[None]):
# #     def compose(self) -> ComposeResult:
# #         yield Static()
# #         # yield PlotextPlot(id="plotext")
# #         # yield PlotWidget(id="plot)

# #     def on_mount(self) -> None:

# #         nx_graph = label_edge_attrib_for(nx_graph)
# # self.draw_matplot(nx_graph)
# #         # nx_graph_num = convert_node_labels_to_integers(nx_graph)
# #         # self.draw_textual_plotext(nx_graph_num)
# #         # self.draw_textual_plot(nx_graph_num)


# #     def draw_textual_plotext(self, nx_graph_num: nx.Graph) -> None:
# #         plot = self.query_one("#plotext")
# #         first_column = [item[0] for item in list(nx_graph_num.edges())]
# #         second_column = [item[1] for item in list(nx_graph_num.edges())]
# #         plot.plot(x=first_column, y=second_column, hires_mode=HiResMode.BRAILLE, line_style="purple")

# #     def draw_textual_plot(self, nx_graph_num: nx.Graph) -> None:
# #         plot = self.query_one("#plot")
# #         plot.plt.scatter(nx_graph_num.edges())


# # if __name__ == "__main__":
# #     MinimalApp().run()

# # data = dict(list(nx_graph_num.edges()))
# # for each in list(nx_graph_num.edges()):


# # # nx
# # # plt.show()
# # # # plot.set_xticks([])
# # # # plot.set_yticks([])
# # # # plot.set_xlabel("")
# # # # plot.set_ylabel("")
# # # # plot.set_styles("background: #1f1f1f;")
