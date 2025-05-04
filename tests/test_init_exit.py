#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=redefined-outer-name, protected-access

from unittest import mock

import pytest
import pytest_asyncio

from zodiac.main_screen import Fold

from test_graph import mock_ollama_data, mock_hub_registry, test_mocked_ollama, test_graph

from zodiac.__main__ import Combo


@pytest.mark.asyncio(loop_scope="module")
async def test_initial_state(app=Combo()):
    """Test that the initial state of the app is correct."""

    async with app.run_test() as pilot:
        # ui_elements = list(pilot.app.query("*"))
        assert isinstance(pilot.app._nodes._get_by_id("fold_screen"), Fold)  # root


@pytest_asyncio.fixture(loop_scope="module")
async def mock_app(mock_ollama_data, mock_hub_registry):
    """Create an instance of the app"""
    app = Combo()
    yield app


@pytest_asyncio.fixture(loop_scope="module")
async def mock_exit(mock_app):
    """Create a decoy app exit"""

    with mock.patch.object(mock_app, "exit", autospec=True) as mocked:
        yield mocked


@pytest.mark.asyncio(loop_scope="module")
async def test_no_exit(mock_app, mock_exit):
    """Test that the app exits correctly."""

    async with mock_app.run_test() as pilot:
        ui_elements = pilot.app._nodes._get_by_id("fold_screen")
        assert ui_elements.safety == 1
        await pilot.press("tab", "k")
        assert ui_elements.safety == 1
        await pilot.press("escape")
        assert ui_elements.safety == 0
        await pilot.press("ctrl")
        assert ui_elements.safety == 1
        await pilot.press("escape")
        assert ui_elements.safety == 0
        mock_exit.assert_not_called()


@pytest.mark.asyncio(loop_scope="module")
async def test_exits(mock_app, mock_exit):
    """Test that the app exits correctly."""
    from nnll_01 import nfo

    async with mock_app.run_test() as pilot:
        ui_elements = pilot.app._nodes._get_by_id("fold_screen")
        nfo("safety", ui_elements.safety)

        # ensure exit
        await pilot.press(",")
        assert ui_elements.safety == 1
        await pilot.press("escape")
        assert ui_elements.safety == 0
        nfo("safety", ui_elements.safety)

        await pilot.press("escape")
        assert ui_elements.safety == -1
        nfo("safety", ui_elements.safety)
        mock_exit.assert_called_once()
