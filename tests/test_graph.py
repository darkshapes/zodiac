# #  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
# #  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint:disable=redefined-outer-name
# pylint:disable=redefined-builtin

import datetime
from enum import Enum
from pathlib import PosixPath

# import matplotlib.pyplot as plt
import pytest
from nnll_01 import nfo
from nnll_15.constants import VALID_CONVERSIONS

# from nnll_15 import RegistryEntry
from unittest import mock


@pytest.fixture(scope="module")
def has_api(name: str):
    # Mock implementation that always returns True
    return True


@pytest.fixture(scope="module")
def mock_has_api():
    with mock.patch("nnll_15.constants.has_api", return_value=True) as mocked:
        yield mocked


# @pytest.fixture
# def mock_libtype():
#     with mock.patch(
#         "nnll_15.constants.LibType",
#     ) as mocked:


class LibType(Enum):
    """API library constants"""

    # Integers are used to differentiate boolean condition

    OLLAMA: tuple = (True, "OLLAMA")
    HUB: tuple = (True, "HUB")
    LM_STUDIO: tuple = (True, "LM_STUDIO")
    CORTEX: tuple = (True, "CORTEX")
    LLAMAFILE: tuple = (True, "LLAMAFILE")
    VLLM: tuple = (True, "VLLM")

    # mocked = LibType
    # yield mocked


class Model:
    """Mock ollama Model class"""

    def __init__(self, model=None, modified_at=None, digest=None, size=None, details=None):
        self.model = model
        self.modified_at = modified_at
        self.digest = digest
        self.size = size
        self.details = details


class ModelDetails:
    """Mock ollama ModelDetails class"""

    def __init__(self, parent_model=None, format=None, family=None, families=None, parameter_size=None, quantization_level=None):
        self.parent_model = parent_model
        self.format = format
        self.family = family
        self.families = families
        self.parameter_size = parameter_size
        self.quantization_level = quantization_level


class ListResponse:
    """Mock ollama ListResponse class"""

    def __init__(self, models=None):
        self.models = models


@pytest.fixture(scope="module")
def mock_ollama_data():
    """Mock ollama response"""
    with mock.patch("ollama.list", new_callable=mock.MagicMock()) as mock_data:
        data = ListResponse(
            models=[
                Model(
                    model="hf.co/unssloth/x:Q8_0",
                    modified_at=datetime.datetime(2025, 3, 19, 12, 21, 19, 112890, tzinfo=None),
                    digest="965289b1e3e63c66bfc018051b6a907b2f0b18620d5721dd1cdfad759b679a2c",
                    size=29565711760,
                    details=ModelDetails(parent_model="", format="gguf", family="gemma3", families=["gemma3"], parameter_size="27B", quantization_level="unknown"),
                ),
                Model(
                    model="hf.co/unssloth/gemma-3-27b-it-GGUF:Q5_K_M",
                    modified_at=datetime.datetime(2025, 3, 18, 12, 13, 57, 294851, tzinfo=None),
                    digest="82c7d241b764d0346f382a9059a7b08056075c7bc2d81ac21dfa20d525556b16",
                    size=20129415184,
                    details=ModelDetails(parent_model="", format="gguf", family="gemma3", families=["gemma3"], parameter_size="27B", quantization_level="unknown"),
                ),
                Model(
                    model="hf.co/barttowski/RekaAI_reka-flash-3-GGUF:Q5_K_M",
                    modified_at=datetime.datetime(2025, 3, 13, 18, 28, 57, 859962, tzinfo=None),
                    digest="43d35cd4e25e90f9cbb33585f60823450bd1f279c4703a1b2831a9cba73e60e4",
                    size=15635474582,
                    details=ModelDetails(parent_model="", format="gguf", family="llama", families=["llama"], parameter_size="20.9B", quantization_level="unknown"),
                ),
            ]
        )
        mock_data.return_value = data
        yield mock_data


class HFCacheInfo:
    """Mock hub cache"""

    def __init__(self, size_on_disk, repos):
        self.size_on_disk = size_on_disk
        self.repos = repos


class CachedRepoInfo:
    """Mock hub repo cache"""

    def __init__(self, repo_id, repo_type, repo_path, size_on_disk, nb_files, revisions, files, pipeline_tag, last_accessed, last_modified):
        self.repo_id = repo_id
        self.repo_type = repo_type
        self.repo_path = repo_path
        self.size_on_disk = size_on_disk
        self.nb_files = nb_files
        self.revisions = revisions
        self.files = files
        self.pipeline_tag = (pipeline_tag,)
        self.last_accessed = last_accessed
        self.last_modified = last_modified


@pytest.fixture(scope="module")
def mock_hub_registry():
    """Mock hub data"""
    with mock.patch("huggingface_hub.scan_cache_dir", new_callable=mock.MagicMock()) as mock_get_registry:
        data = HFCacheInfo(
            size_on_disk=91018285403,
            repos=frozenset(
                {
                    CachedRepoInfo(
                        repo_id="parrler-tts/parler-tts-large-v1",
                        repo_type="model",
                        repo_path=PosixPath("/Users/unauthorized/.cache/huggingface/hub/models--parler-tts--parler-tts-large-v1"),
                        size_on_disk=9335526346,
                        nb_files=14,
                        revisions=None,
                        files=None,
                        pipeline_tag=["text-to-speech"],
                        last_accessed=1741910585.3828554,
                        last_modified=1741908821.5103855,
                    ),
                    CachedRepoInfo(
                        repo_id="THUDM/CogVieew3-Plus-3B",
                        repo_type="model",
                        repo_path=PosixPath("/Users/unauthorized/.cache/huggingface/hub/models--THUDM--CogView3-Plus-3B"),
                        size_on_disk=25560123724,
                        nb_files=20,
                        revisions=None,
                        files=None,
                        pipeline_tag=["text-to-image", "image-to-text", "text-generation"],
                        last_accessed=1741827083.5111423,
                        last_modified=1741827083.4126444,
                    ),
                }
            ),
        )
        mock_get_registry.return_value = data
        yield mock_get_registry


def test_mocked_hub(mock_hub_registry):
    """Check if mocking hub correctly.
    `frozenset` is converted to a sorted list
    Otherwise hashed return becomes unordered"""
    import huggingface_hub

    huggingface_hub.constants.HF_HUB_DISABLE_PROGRESS_BARS = True
    huggingface_hub.constants.HF_HUB_DISABLE_TELEMETRY = True
    huggingface_hub.constants.HF_XET_HIGH_PERFORMANCE = True
    huggingface_hub.constants.HF_HUB_ENABLE_HF_TRANSFER = True
    huggingface_hub.constants.HF_HUB_DISABLE_IMPLICIT_TOKEN = True
    huggingface_hub.constants.HF_HUB_OFFLINE = True  # net True = OFFLINE False

    result = mock_hub_registry()
    new_list = []
    assert len(result.repos) == 2
    next_model = [*result.repos]
    # nfo("result. ", result.repos)
    for x in next_model:
        new_list.append([x.repo_id, x.size_on_disk])
    new_list.sort(key=lambda x: x[1])
    assert new_list[0][0] == "parrler-tts/parler-tts-large-v1"
    assert new_list[0][1] == 9335526346


def test_mocked_ollama(mock_ollama_data):
    """Check if mocking ollama correctly"""
    result = mock_ollama_data()

    assert len(result.models) == 3
    next_model = next(iter(result.models))
    assert next_model.model == "hf.co/unssloth/x:Q8_0"
    assert next_model.size == 29565711760


def test_graph(mock_ollama_data, mock_hub_registry):
    """Run test of graph creation"""
    from zodiac.graph import IntentProcessor

    int_proc = IntentProcessor()
    int_proc.calc_graph()
    assert list(int_proc.intent_graph) == VALID_CONVERSIONS
    key_data = int_proc.intent_graph.edges.data("key")
    for edge in key_data:
        if edge[2] is not None:
            assert isinstance(edge[2], str)
        else:
            assert isinstance(edge[1], str)
    size_data = int_proc.intent_graph.edges.data("size")

    for edge in size_data:
        if edge[2] is not None:
            assert isinstance(edge[2], int)
        else:
            assert isinstance(edge[1], str)


if __name__ == "__main__":
    pytest.main()
