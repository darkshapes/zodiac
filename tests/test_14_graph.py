# #  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3) */ -->
# #  # # <!-- // /*  d a r k s h a p e s */ -->

# # pylint:disable=redefined-outer-name
# # pylint:disable=redefined-builtin

# import datetime
# from pathlib import PosixPath
# from unittest import mock

# # import matplotlib.pyplot as plt
# import pytest
# from nnll_14 import calculate_graph
# from nnll_15.constants import VALID_CONVERSIONS


# class Model:
#     """Mock ollama Model class"""

#     def __init__(self, model=None, modified_at=None, digest=None, size=None, details=None):
#         self.model = model
#         self.modified_at = modified_at
#         self.digest = digest
#         self.size = size
#         self.details = details


# class ModelDetails:
#     """Mock ollama ModelDetails class"""

#     def __init__(self, parent_model=None, format=None, family=None, families=None, parameter_size=None, quantization_level=None):
#         self.parent_model = parent_model
#         self.format = format
#         self.family = family
#         self.families = families
#         self.parameter_size = parameter_size
#         self.quantization_level = quantization_level


# class ListResponse:
#     """Mock ollama ListResponse class"""

#     def __init__(self, models=None):
#         self.models = models


# @pytest.fixture(scope="session")
# def mock_ollama_data():
#     """Mock ollama response"""
#     with mock.patch("ollama.list", new_callable=mock.MagicMock()) as mock_get_registry_data:
#         data = ListResponse(
#             models=[
#                 Model(
#                     model="hf.co/unsloth/gemma-3-27b-it-GGUF:Q8_0",
#                     modified_at=datetime.datetime(2025, 3, 19, 12, 21, 19, 112890, tzinfo=None),
#                     digest="965289b1e3e63c66bfc018051b6a907b2f0b18620d5721dd1cdfad759b679a2c",
#                     size=29565711760,
#                     details=ModelDetails(parent_model="", format="gguf", family="gemma3", families=["gemma3"], parameter_size="27B", quantization_level="unknown"),
#                 ),
#                 Model(
#                     model="hf.co/unsloth/gemma-3-27b-it-GGUF:Q5_K_M",
#                     modified_at=datetime.datetime(2025, 3, 18, 12, 13, 57, 294851, tzinfo=None),
#                     digest="82c7d241b764d0346f382a9059a7b08056075c7bc2d81ac21dfa20d525556b16",
#                     size=20129415184,
#                     details=ModelDetails(parent_model="", format="gguf", family="gemma3", families=["gemma3"], parameter_size="27B", quantization_level="unknown"),
#                 ),
#                 Model(
#                     model="hf.co/bartowski/RekaAI_reka-flash-3-GGUF:Q5_K_M",
#                     modified_at=datetime.datetime(2025, 3, 13, 18, 28, 57, 859962, tzinfo=None),
#                     digest="43d35cd4e25e90f9cbb33585f60823450bd1f279c4703a1b2831a9cba73e60e4",
#                     size=15635474582,
#                     details=ModelDetails(parent_model="", format="gguf", family="llama", families=["llama"], parameter_size="20.9B", quantization_level="unknown"),
#                 ),
#             ]
#         )
#         mock_get_registry_data.return_value = data
#         yield mock_get_registry_data


# class HFCacheInfo:
#     """Mock hub cache"""

#     def __init__(self, size_on_disk, repos):
#         self.size_on_disk = size_on_disk
#         self.repos = repos


# class CachedRepoInfo:
#     """Mock hub repo cache"""

#     def __init__(self, repo_id, repo_type, repo_path, size_on_disk, nb_files, revisions, files, last_accessed, last_modified):
#         self.repo_id = repo_id
#         self.repo_type = repo_type
#         self.repo_path = repo_path
#         self.size_on_disk = size_on_disk
#         self.nb_files = nb_files
#         self.revisions = revisions
#         self.files = files
#         self.last_accessed = last_accessed
#         self.last_modified = last_modified


# @pytest.fixture(scope="session")
# def mock_hub_data():
#     """Mock hub data"""
#     with mock.patch("huggingface_hub.scan_cache_dir", new_callable=mock.MagicMock()) as mock_get_registry_data:
#         data = HFCacheInfo(
#             size_on_disk=91018285403,
#             repos=frozenset(
#                 {
#                     CachedRepoInfo(
#                         repo_id="parler-tts/parler-tts-large-v1",
#                         repo_type="model",
#                         repo_path=PosixPath("/Users/unauthorized/.cache/huggingface/hub/models--parler-tts--parler-tts-large-v1"),
#                         size_on_disk=9335526346,
#                         nb_files=14,
#                         revisions=None,
#                         files=None,
#                         last_accessed=1741910585.3828554,
#                         last_modified=1741908821.5103855,
#                     ),
#                     CachedRepoInfo(
#                         repo_id="THUDM/CogView3-Plus-3B",
#                         repo_type="model",
#                         repo_path=PosixPath("/Users/unauthorized/.cache/huggingface/hub/models--THUDM--CogView3-Plus-3B"),
#                         size_on_disk=25560123724,
#                         nb_files=20,
#                         revisions=None,
#                         files=None,
#                         last_accessed=1741827083.5111423,
#                         last_modified=1741827083.4126444,
#                     ),
#                 }
#             ),
#         )
#         mock_get_registry_data.return_value = data
#         yield mock_get_registry_data


# def test_mocked_ollama(mock_ollama_data):
#     """Check if mocking ollama correctly"""
#     result = mock_ollama_data()

#     assert len(result.models) == 3
#     next_model = next(iter(result.models))
#     assert next_model.model == "hf.co/unsloth/gemma-3-27b-it-GGUF:Q8_0"
#     assert next_model.size == 29565711760


# def test_mocked_hub(mock_hub_data):
#     """Check if mocking hub correctly.
#     `frozenset` is converted to a sorted list
#     Otherwise hashed return becomes unordered"""
#     result = mock_hub_data()
#     new_list = []
#     assert len(result.repos) == 2
#     next_model = [*result.repos]
#     for x in next_model:
#         new_list.append([x.repo_id, x.size_on_disk])
#     new_list.sort(key=lambda x: x[1])
#     assert new_list[0][0] == "parler-tts/parler-tts-large-v1"
#     assert new_list[0][1] == 9335526346


# def test_create_graph(mock_ollama_data, mock_hub_data):
#     """Run test of graph creation"""
#     nx_graph = calculate_graph()

#     assert list(nx_graph) == VALID_CONVERSIONS
#     key_data = nx_graph.edges.data("key")
#     for edge in key_data:
#         if edge[2] is not None:
#             assert isinstance(edge[2], str)
#         else:
#             assert isinstance(edge[1], str)

#     size_data = nx_graph.edges.data("size")
#     for edge in size_data:
#         if edge[2] is not None:
#             assert isinstance(edge[2], int)
#         else:
#             assert isinstance(edge[1], str)


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
