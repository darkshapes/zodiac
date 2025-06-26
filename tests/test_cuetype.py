#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->


import pytest
from unittest.mock import patch
from typing import List
import pytest_asyncio
from enum import Enum


def has_api(name: str):
    # Mock implementation that always returns True
    return True


class BaseEnum(Enum):
    """Base class for available system packages\n"""

    @classmethod
    def show_all(cls) -> List:
        """Show all POSSIBLE API types of a given class"""
        return [x for x, y in CueType.__members__.items()]

    @classmethod
    def show_available(cls) -> bool:
        """Show all AVAILABLE API types of a given class"""
        return [library.value[1] for library in list(cls) if library.value[0] is True]

    @classmethod
    def check_type(cls, type_name: str, server: bool = False) -> bool:
        """Check for a SINGLE API availability"""
        type_name = type_name.upper()
        if hasattr(cls, type_name):
            available = next(iter(getattr(cls, type_name).value))
            if server and available:
                return has_api(type_name)
            return available


class CueType(BaseEnum):
    """API library constants"""

    # Integers are used to differentiate boolean condition

    OLLAMA: tuple = (has_api("OLLAMA"), "OLLAMA")
    HUB: tuple = (has_api("HUB"), "HUB")
    LM_STUDIO: tuple = (has_api("LM_STUDIO"), "LM_STUDIO")
    CORTEX: tuple = (has_api("CORTEX"), "CORTEX")
    LLAMAFILE: tuple = (has_api("LLAMAFILE"), "LLAMAFILE")
    VLLM: tuple = (has_api("VLLM"), "VLLM")


@pytest_asyncio.fixture(loop_scope="session")
async def mock_has_api():
    with patch("zodiac.providers.constants.has_api", return_value=True) as mocked:
        yield mocked


@pytest.mark.filterwarnings("ignore:open_text")
@pytest.mark.filterwarnings("ignore::DeprecationWarning:")
@patch("zodiac.providers.constants.has_api", side_effect=lambda x: False)
def test_cuetype(mock_has_api):
    assert CueType.OLLAMA.value[0] is True
    assert CueType.HUB.value[0] is True
    assert CueType.LM_STUDIO.value[0] is True
    assert CueType.CORTEX.value[0] is True
    assert CueType.LLAMAFILE.value[0] is True
    assert CueType.VLLM.value[0] is True
