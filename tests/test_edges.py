# import datetime
# from enum import Enum
# from pathlib import PosixPath

# # import matplotlib.pyplot as plt
# import pytest
# from nnll_01 import nfo
# from nnll_15.constants import VALID_CONVERSIONS

# # from nnll_15 import RegistryEntry
# from unittest import mock


# def test_mock_edges(mock_has_api):
#     from zodiac.graph import IntentProcessor
#     from datetime import datetime
#     from nnll_15 import from_cache, RegistryEntry

#     int_proc = IntentProcessor()
#     cache = [
#         {
#             "entry": RegistryEntry(
#                 model="🤡",
#                 size=1024,
#                 tags=["speech-translation"],
#                 library=LibType.HUB,
#                 timestamp=int(datetime.now().timestamp()),
#             )
#         }
#     ]
#     for model in cache:
#         int_proc.intent_graph.add_edges_from(model.available_tasks, entry=model, weight=1.0)
#     nfo(int_proc.intent_graph.edges.data())
#     assert int_proc.intent_graph.edges.data()

#     # key_data = int_proc.intent_graph.edges.data("key")
#     # nfo(int_proc.intent_graph.edges.data())
#     # nfo(int_proc.intent_graph.nodes())
#     # int_proc.set_path("text", "text")
#     # nfo(int_proc.coord_path)
#     # nfo(int_proc.intent_graph.edges.data())


# # @pytest.fixture(scope="session")
# # def mock_graph(
# #     mock_has_api,
# #     mock_libtype,
# #     mock_ollama_data,
# #     mock_hub_registry,
# # ):
# #     """Run test of graph creation"""
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     nx_graph = int_proc.calc_graph()

# #     nfo(nx_graph)


# # @pytest.fixture(scope="session")
# # def mock_llama_cache(mock_ollama_data, mock_has_api, mock_libtype):
# #     with mock.patch("nnll_15.from_cache", autocast=True) as mocked:
# #         result = mock_ollama_data()
# #         yield mocked


# # @pytest.fixture(scope="session")
# # def mock_hub_cache(mock_hub_registry, mock_has_api, mock_libtype):
# #     with mock.patch("nnll_15.from_cache", autocast=True) as mocked:
# #         result = mock_hub_registry()
# #         yield mocked


# # def test_checkpoint_processing_t2i(mock_hub_cache, mock_llama_cache, mock_has_api, mock_libtype):
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     nx_graph = int_proc.calc_graph()
# #     for model in mock_hub_cache:
# #         nx_graph.add_edges_from(model.available_tasks, entry=model, weight=1.0)
# #     for model in mock_llama_cache:
# #         nx_graph.add_edges_from(model.available_tasks, entry=model, weight=1.0)
# #     nfo(nx_graph.edges.data())
# #     int_proc.intent_graph = nx_graph

# #     int_proc.set_path("text", "image")
# #     assert int_proc.has_path() is True
# #     int_proc.set_ckpts()
# #     assert int_proc.has_ckpt() is True
# #     expected_models = [("CogVieew3-Plus-3B", "THUDM/CogVieew3-Plus-3B")]
# #     assert int_proc.models == expected_models


# # def setUp(lookit_this, mock_has_api, mock_libtype):
# #     import networkx as nx
# #     from zodiac.graph import IntentProcessor

# #     proc_name = IntentProcessor()  # Replace with actual class name
# #     assert proc_name.has_graph() is True
# #     proc_name.set_path("text", "text")
# #     proc_name.set_ckpts()

# #     return proc_name


# # def test_checkpoint_processing_i2t(
# #     mock_ollama_data,
# #     mock_hub_registry,
# # ):
# #     from zodiac.graph import IntentProcessor

# #     x2 = IntentProcessor()
# #     x2.calc_graph()
# #     x2.set_path("image", "text")
# #     x2.set_ckpts()

# #     expected_models = [("CogView3-Plus-3B", "THUDM/CogView3-Plus-3B")]
# #     assert x2.models == expected_models


# # def test_checkpoint_processing_tts(mock_hub_registry):
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     int_proc.calc_graph()
# #     int_proc.set_path("text", "speech")
# #     int_proc.set_ckpts()

# #     expected_models = [
# #         (
# #             "parler-tts-large-v1",
# #             "parler-tts/parler-tts-large-v1",
# #         )
# #     ]
# #     assert int_proc.models == expected_models


# # def test_checkpoint_processing_s2i_fail(mock_hub_registry):
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     int_proc.calc_graph()

# #     int_proc.set_path("speech", "image")
# #     int_proc.set_ckpts()

# #     assert int_proc.models is None


# # def test_checkpoint_processing_s2t_fail(mock_hub_registry):
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     int_proc.calc_graph()
# #     int_proc.set_path("speech", "text")
# #     int_proc.set_ckpts()

# #     assert int_proc.models is None


# # @pytest.fixture(scope="session")
# # def mock_hub_data_2(mock_hub_registry):
# #     with mock.patch("huggingface_hub.scan_cache_dir", new_callable=mock.MagicMock()) as mock_new_registry:
# #         data = HFCacheInfo(
# #             size_on_disk=91018285403,
# #             repos=frozenset(
# #                 {
# #                     CachedRepoInfo(
# #                         repo_id="parler-tts/parler-tts-large-v1",
# #                         repo_type="model",
# #                         repo_path=PosixPath("/Users/unauthorized/.cache/huggingface/hub/models--parler-tts--parler-tts-large-v1"),
# #                         size_on_disk=9335526346,
# #                         nb_files=14,
# #                         revisions=None,
# #                         files=None,
# #                         pipeline_tag=["text-to-speech"],
# #                         last_accessed=1741910585.3828554,
# #                         last_modified=1741908821.5103855,
# #                     ),
# #                     CachedRepoInfo(
# #                         repo_id="THUDM/CogView3-Plus-3B",
# #                         repo_type="model",
# #                         repo_path=PosixPath("/Users/unauthorized/.cache/huggingface/hub/models--THUDM--CogView3-Plus-3B"),
# #                         size_on_disk=25560123724,
# #                         nb_files=20,
# #                         revisions=None,
# #                         files=None,
# #                         pipeline_tag=["text-to-image", "image-to-text", "text-generation"],
# #                         last_accessed=1741827083.5111423,
# #                         last_modified=1741827083.4126444,
# #                     ),
# #                     CachedRepoInfo(
# #                         repo_id="microsoft/phi-4-multimodal-instruct",
# #                         repo_type="model",
# #                         repo_path=PosixPath("/Users/unauthorized/.cache/huggingface/hub/models--microsoft--Phi-4-multimodal-x"),
# #                         size_on_disk=12855234702,
# #                         nb_files=46,
# #                         revisions=None,
# #                         files=None,
# #                         pipeline_tag=["text-to-speech", "automatic-speech-recognition", "speech-to-text", "image-classification"],
# #                         last_accessed=1746206750.655514,
# #                         last_modified=1746156656.7660124,
# #                     ),
# #                 }
# #             ),
# #         )
# #         mock_new_registry.return_value = data
# #         yield mock_new_registry


# # def test_mocked_hub_v2(mock_hub_data_2):
# #     """Check if mocking hub correctly.
# #     `frozenset` is converted to a sorted list
# #     Otherwise hashed return becomes unordered"""
# #     result = mock_hub_data_2()
# #     new_list = []
# #     assert len(result.repos) == 3
# #     next_model = [*result.repos]
# #     nfo("result. ", result.repos)
# #     for x in next_model:
# #         new_list.append([x.repo_id, x.size_on_disk])
# #     new_list.sort(key=lambda x: x[1])
# #     nfo(new_list)
# #     assert new_list[0][0] == "parler-tts/parler-tts-large-v1"
# #     assert new_list[0][1] == 9335526346


# # def test_checkpoint_processing_stt(mock_hub_data_2):
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     int_proc.calc_graph()
# #     int_proc.set_path("speech", "text")
# #     int_proc.set_ckpts()

# #     expected_models = [("phi-4-multimodal-instruct", "microsoft/phi-4-multimodal-instruct")]
# #     assert int_proc.models == expected_models


# # def test_checkpoint_processing_s2i(mock_hub_data_2):
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     int_proc.calc_graph()
# #     int_proc.set_path("speech", "image")
# #     int_proc.set_ckpts()

# #     expected_models = [
# #         ("phi-4-multimodal-instruct", "microsoft/phi-4-multimodal-instruct"),
# #         ("CogView3-Plus-3B", "THUDM/CogView3-Plus-3B"),
# #     ]
# #     assert int_proc.models == expected_models


# # def test_checkpoint_processing_s2s(mock_hub_data_2):
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     int_proc.calc_graph()
# #     int_proc.set_path("speech", "speech")
# #     int_proc.set_ckpts()

# #     expected_models = [
# #         ("phi-4-multimodal-instruct", "microsoft/phi-4-multimodal-instruct"),
# #         (
# #             "parler-tts-large-v1",
# #             "parler-tts/parler-tts-large-v1",
# #         ),
# #     ]
# #     assert int_proc.models == expected_models


# # def test_checkpoint_processing_t2t(mock_ollama_data):
# #     from zodiac.graph import IntentProcessor

# #     int_proc = IntentProcessor()
# #     int_proc.calc_graph()
# #     int_proc.set_path("text", "text")
# #     int_proc.set_ckpts()

# #     expected_models = [("x:Q8_0", "ollama_chat/hf.co/unsloth/x:Q8_0"), ("gemma-3-27b-it-GGUF:Q5_K_M", "ollama_chat/hf.co/unsloth/gemma-3-27b-it-GGUF:Q5_K_M")]
# #     assert int_proc.models == expected_models


# if __name__ == "__main__":
#     pytest.main()
