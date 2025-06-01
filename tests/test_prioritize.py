# # type: ignore
# from pathlib import PosixPath
# import pytest
# import datetime
# from textual.containers import Container, Horizontal  # noqa
# from unittest import mock
# from zodiac.__main__ import Combo


# class Model:
#     """Mock ollama Model class"""

#     def __init__(self, model=None, modified_at=None, digest=None, size=None, details=None):
#         self.model = model
#         self.modified_at = modified_at
#         self.digest = digest
#         self.size = size
#         self.details = details


# # Test cases
# @pytest.fixture
# def registry_entry_ollama():
#     return RegistryEntry(
#         model="🤡",
#         size=1024,
#         tags=["mllama", "llava", "text"],
#         library=LibType.OLLAMA,
#         timestamp=int(datetime.now().timestamp()),
#     )


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


# ollama_data = data = ListResponse(
#     models=[
#         Model(
#             model="hf.co/unsloth/x:Q8_0",
#             modified_at=datetime.datetime(2025, 3, 19, 12, 21, 19, 112890, tzinfo=None),
#             digest="965289b1e3e63c66bfc018051b6a907b2f0b18620d5721dd1cdfad759b679a2c",
#             size=29565711760,
#             details=ModelDetails(parent_model="", format="gguf", family="gemma3", families=["gemma3"], parameter_size="27B", quantization_level="unknown"),
#         ),
#         Model(
#             model="hf.co/unsloth/gemma-3-27b-it-GGUF:Q5_K_M",
#             modified_at=datetime.datetime(2025, 3, 18, 12, 13, 57, 294851, tzinfo=None),
#             digest="82c7d241b764d0346f382a9059a7b08056075c7bc2d81ac21dfa20d525556b16",
#             size=20129415184,
#             details=ModelDetails(parent_model="", format="gguf", family="gemma3", families=["gemma3"], parameter_size="27B", quantization_level="unknown"),
#         ),
#         Model(
#             model="hf.co/bartowski/RekaAI_reka-flash-3-GGUF:Q5_K_M",
#             modified_at=datetime.datetime(2025, 3, 13, 18, 28, 57, 859962, tzinfo=None),
#             digest="43d35cd4e25e90f9cbb33585f60823450bd1f279c4703a1b2831a9cba73e60e4",
#             size=15635474582,
#             details=ModelDetails(parent_model="", format="gguf", family="llama", families=["llama"], parameter_size="20.9B", quantization_level="unknown"),
#         ),
#     ]
# )


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


# @pytest.fixture(scope="module")
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


# @pytest.fixture(scope="module")
# def mock_ollama_data():
#     """Mock ollama response"""
#     with mock.patch("ollama.list", new_callable=mock.MagicMock()) as mock_get_registry_data:
#         mock_get_registry_data.return_value = ollama_data
#         yield mock_get_registry_data


# @pytest.mark.asyncio(loop_scope="module")
# async def test_top_priority_single(mock_ollama_data, mock_hub_data, app=Combo()):
#     # add star and move to top
#     from nnll.monitor.file import nfo
#     import sys
#     import os

#     async with app.run_test() as pilot:
#         screen_id = pilot.app._nodes._get_by_id("fold_screen")
#         screen_id.int_proc.calc_graph(ollama_data)
#         nfo(screen_id.int_proc.models)
#         nfo(screen_id.int_proc.ckpts)
#         zero_order = {}
#         for i, model in enumerate(screen_id.int_proc.ckpts):
#             zero_order.setdefault(i, model)  # test control original order
#             screen_id.int_proc.ckpts[i]["weight"] = 1.0

#         floor = len(screen_id.int_proc.ckpts) - 1
#         screen_id.int_proc.ckpts[floor]["weight"] = 0.9
#         screen_id.int_proc.set_ckpts()
#         model_id = zero_order[floor]["entry"].model
#         nfo(screen_id.int_proc.ckpts)
#         assert (f"*{os.path.basename(model_id)}", model_id) == screen_id.int_proc.models[0]


# @pytest.mark.asyncio(loop_scope="module")
# async def test_top_priority_multiple_value_add_star(mock_ollama_data, mock_hub_data, app=Combo()):
#     # add star and move to top
#     from nnll.monitor.file import nfo
#     import sys
#     import os

#     async with app.run_test() as pilot:
#         screen_id = pilot.app._nodes._get_by_id("fold_screen")

#         nfo(screen_id.int_proc.models)
#         nfo(screen_id.int_proc.ckpts)
#         zero_order = {}
#         for i, model in enumerate(screen_id.int_proc.ckpts):
#             zero_order.setdefault(i, model)  # test control original order
#             screen_id.int_proc.ckpts[i]["weight"] = 1.0

#         floor = len(screen_id.int_proc.ckpts) - 2
#         assert screen_id.int_proc.ckpts[floor]["weight"] == 1.0
#         screen_id.int_proc.ckpts[floor]["weight"] = 0.9

#         screen_id.int_proc.set_ckpts()

#         model_id_1 = zero_order[floor]["entry"].model
#         nfo(f"model 1 changed to 0.9{model_id_1}")
#         assert "gemma" in model_id_1

#         floor = len(screen_id.int_proc.ckpts) - 1
#         assert screen_id.int_proc.ckpts[floor]["weight"] == 1.0
#         screen_id.int_proc.ckpts[floor]["weight"] = 0.9

#         screen_id.int_proc.set_ckpts()
#         model_id_2 = zero_order[floor]["entry"].model
#         assert "reka" in model_id_2
#         nfo(f"model 2 changed to 0.9{model_id_2}")
#         nfo(screen_id.int_proc.ckpts)
#         model_prev_top = zero_order[0]["entry"].model
#         assert [(f"*{os.path.basename(model_id_1)}", model_id_1), (f"*{os.path.basename(model_id_2)}", model_id_2), (f"{os.path.basename(model_prev_top)}", model_prev_top)] == screen_id.int_proc.models
