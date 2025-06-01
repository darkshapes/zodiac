# import networkx as nx
# from zodiac.graph import calculate_graph
# import matplotlib.pyplot as plt
# import numpy as np

# from mir.constants import LibType


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


# # when user presses trigger :
# # run shortest distance, then run operations identified on edges

# # seen = set()
# # [e[1] for e in nx_graph.edges if e[1] not in seen and not seen.add(e[1])]

# # nx_graph['speech']['text’] get all paths towards
# #  get all size on graph
# # nx_graph.edges.data(“keys”) get all model name on graph
# # nx_graph.edges['text','speech',0]['key']

# # nx_graph.out_degree('text') get number of edges/paths pointing away
# # nx_graph.in_degree('text') get number of edges/paths pointing towards
# # nx_graph.edges[‘text’, ‘image’][‘weight'] = 4.2 change attribute


# # node_attrib = nx.get_node_attributes(nx_graph, “model”)
# # node_attrib[‘text’]


# # nx.draw_networkx
# # adjacent_pairs = [(key, item) for key, value in VALID_CONVERSIONS.input.items() for item in (value.values if isinstance(value.values, tuple) else ())]
# # from typing import Dict, Tuple
# # from pydantic import BaseModel, Field

# # class ConversionValue(BaseModel):
# #     """(output_medium, more_output_medium)"""

# #     values: Field()


# # class ConversionMap(BaseModel):
# #     """{input_medium: (output_medium, more_output_medium)"""

# #     input: Dict[str, ConversionValue]


# # from networkx import convert_node_labels_to_integers


# # mllama (vllm), text-to-image, text-generation

# # 2. Add nodes for each unique data type and model combination (e.g., `['text']`, `['image']`, etc.) and edges representing the transformations between them using models.


# # # Define a function to add edges based on input-output pairs
# # def add_model_edges(G, input_type, model_dict, output_type):
# #     for model_name, model_path in model_dict.items():
# #         G.add_edge(str(input_type), str(output_type), model_name=model_name, model_path=model_path)


# # # Add the specified paths to your graph
# # add_model_edges(G, ["text"], {"model1": "path1"}, ["text"])
# # add_model_edges(G, ["text", "image"], {"model2": "path2"}, ["text"])
# # add_model_edges(G, ["image"], {"model3": "path3"}, ["text"])
# # add_model_edges(G, ["text"], {"model4": "path4"}, ["image"])
# # add_model_edges(G, ["speech"], {"model5": "path5"}, ["text"])
# # add_model_edges(G, ["text"], {"model6": "path6"}, ["speech"])

# # # Example: Find all paths from ['text'] to ['image']
# # paths = list(nx.all_simple_paths(G, str(["text"]), str(["image"])))
# # print(paths)


# # node would be format
# # edge would be conversion model
# # 'vllm'
# # 'text-generation'

# # input                                                          #output
# # node                             #edge                          #node
# # {['text']}                    { model name: model path} }     { ['text']] }
# # [['text', 'image']:           { model name: model path} }     { ['text']  }
# # {['image']:                   { model name: model path} }     { ['text']  }
# # {['text']:                    { model name: model path} }     { ['image'] }
# # {['speech']:                  { model name: model path} }     { ['text']  }
# # {['text']:                    { model name: model path} }     { ['speech']}


# # bidirectional_shortest_path(G, mode_in, mode_out)

# # G.add_edges_from[(2, 3, {"weight": 3.1415})] #add edge with attribute
# # G.add_nodes_from([(4, {"color": "red"}), (5, {"color": "green"})]) #add node with attribute
# # H = nx.path_graph(10)
# # G.add_nodes_from(H)  # import one graph into another
# # G.add_node(H)  # the entire graph as a node
# # G.clear()

# # class ConversionGraph:
# #     def __init__(self, graph):
# #         self.graph = graph  # Graph where keys are formats, values are dict of {format: (steps, quality)}

# #     def manhattan_distance(self, node1, node2):
# #         return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])

# #     def find_conversion_path(self, initial_format, target_format):
# #         # Check if direct conversion is possible
# #         if target_format in self.graph[initial_format]:
# #             return [(initial_format, target_format)]

# #         # Initialize variables for pathfinding
# #         queue = [[(initial_format, 0, float("inf"))]]  # (format, steps, quality)
# #         visited = set()

# #         while queue:
# #             path = queue.pop(0)
# #             current_node = path[-1][0]
# #             current_steps = path[-1][1]
# #             current_quality = path[-1][2]

# #             if current_node == target_format:
# #                 return path

# #             for neighbor, (steps, quality) in self.graph[current_node].items():
# #                 # Avoid backtracking and only move forward
# #                 if neighbor not in visited:
# #                     new_steps = current_steps + steps
# #                     new_quality = min(current_quality, quality)
# #                     distance_to_goal = self.manhattan_distance((new_steps, new_quality), (0, float("inf")))

# #                     # Prioritize paths with fewer steps but consider higher quality nodes
# #                     queue.append(path + [(neighbor, new_steps, new_quality)])

# #             visited.add(current_node)
# #             queue.sort(key=lambda p: (len(p), -p[-1][2]))  # Sort by path length and quality

# #         return None


# # # (steps, quality)
# # graph = {
# #     "FormatA": {"FormatB": (1, 8), "FormatC": (2, 9)},
# #     "FormatB": {"FormatD": (1, 7)},
# #     "FormatC": {"FormatD": (3, 6), "FormatE": (2, 10)},
# #     "FormatD": {"TargetFormat": (1, 5)},
# #     "FormatE": {"TargetFormat": (1, 9)},
# # }

# # if __name__ == "__main__":
# #     converter = ConversionGraph(graph)
# #     path = converter.find_conversion_path("FormatA", "TargetFormat")
# #     print("Conversion Path:", path)


# #    for model, details in ollama_models.items():
# #        nx_graph.add_edges_from(details.available_tasks, key=model, weight=details.size)
# #    for model, details in hub_models.items():
# #        nx_graph.add_edges_from(details.available_tasks, key=model, weight=details.size)
# #     nx_graph = build_conversion_graph()
# #     ollama_models = from_ollama_cache()
# #     hub_models = from_hf_hub_cache()
# #     for model, details in ollama_models.items():
# #         nx_graph.add_edges_from(details.available_tasks, label=model, weight=details.size)
# #     for model, details in hub_models.items():
# #         nx_graph.add_edges_from(details.available_tasks, label=model, weight=details.size)
