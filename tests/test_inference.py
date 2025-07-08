#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

import asyncio
from enum import Enum
from unittest.mock import patch

import pytest
import pytest_asyncio

from nnll.mir.json_cache import JSONCache
from zodiac.providers.constants import CUETYPE_PATH_NAMED


class CueType(Enum):
    """API library constants"""

    # Integers are used to differentiate boolean condition

    OLLAMA: tuple = (True, "OLLAMA")
    HUB: tuple = (True, "HUB")
    LM_STUDIO: tuple = (True, "LM_STUDIO")
    CORTEX: tuple = (True, "CORTEX")
    LLAMAFILE: tuple = (True, "LLAMAFILE")
    VLLM: tuple = (True, "VLLM")
    MLX_AUDIO: tuple = (True, "MLX_AUDIO")
    KAGGLE: tuple = (True, "KAGGLE")


@pytest_asyncio.fixture(loop_scope="module")
async def mock_signature():
    with patch("zodiac.inference.dspy.Signature", autospec=True) as mocked:
        yield mocked


@pytest_asyncio.fixture(loop_scope="module")
async def mock_predict():
    with patch("zodiac.inference.dspy.Predict", autospec=True) as mocked:
        yield mocked


@pytest_asyncio.fixture(loop_scope="module")
async def has_api():
    with patch("zodiac.providers.constants.has_api", autospec=True) as mocked:
        mocked.return_value = True
        yield mocked


class PlaceholderClass:
    model = "🤡"
    cuetype = CueType.CORTEX
    api_kwargs = {}


@pytest.mark.filterwarnings("ignore:open_text")
@pytest.mark.filterwarnings("ignore::DeprecationWarning:")
@pytest.mark.asyncio(loop_scope="module")
async def test_chat_instance(mock_signature, mock_predict):
    mock_predict.return_value = mock_predict
    mock_signature.return_value = mock_signature

    # Create an instance of ChatMachineWithMemory

    from zodiac.inference import InferenceProcessor

    inference = InferenceProcessor()
    inference.max_workers = 8
    return inference
    # sig=mock_signature,


# @pytest.mark.filterwarnings("ignore:open_text")
# @pytest.mark.filterwarnings("ignore::DeprecationWarning:")
# @pytest.mark.asyncio(loop_scope="module")
# async def test_inference_initialization(mock_signature, mock_predict):
#     inference = await test_chat_instance(mock_signature, mock_predict)
#     with patch("zodiac.inference.dspy.LM", autospec=True, return_value="🤡") as mock_lm:
#         assert hasattr(inference, "mir_db")
#         assert inference.mir_db.database is not None
#         assert callable(inference.mir_db.find_path)
#         assert hasattr(inference, "factory")
#         assert inference.factory is not None
#         assert callable(inference.factory.create_pipeline)
#         assert callable(inference)
#         assert callable(inference.forward)


@pytest.mark.filterwarnings("ignore:open_text")
@pytest.mark.filterwarnings("ignore::DeprecationWarning:")
@pytest.mark.asyncio(loop_scope="module")
async def test_inference_generation(mock_signature, mock_predict, has_api):
    # from zodiac.inference import ChatMachineWithMemory

    # inference = ChatMachineWithMemory(max_workers=8)
    inference = await test_chat_instance(mock_signature, mock_predict)
    assert inference.pipe is None
    # inference.pipe = None

    with patch("zodiac.inference.dspy.LM", autospec=True, return_value="🤡") as mock_lm:
        inference.ready(registry_entries=PlaceholderClass, sig=mock_signature)

        assert callable(inference.pipe)
        assert inference.pipe is not None
