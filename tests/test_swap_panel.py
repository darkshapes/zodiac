from unittest import mock

import pytest
import pytest_asyncio
from test_graph import mock_hub_data, mock_ollama_data, test_create_graph, test_mocked_hub, test_mocked_ollama
from zodiac.__main__ import Combo
from zodiac.main_screen import Fold


@pytest_asyncio.fixture(loop_scope="module")
async def mock_app(mock_ollama_data, mock_hub_data):
    """Create an instance of the app"""
    app = Combo()
    yield app


# async def test_flip_mode()
#
