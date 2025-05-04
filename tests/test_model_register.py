# #  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
# #  # # <!-- // /*  d a r k s h a p e s */ -->

# # pylint: disable=redefined-outer-name, protected-access

from unittest import mock
import pytest
import pytest_asyncio

from zodiac.__main__ import Combo

from nnll_01 import nfo


@pytest_asyncio.fixture(loop_scope="module")
def mock_generate_response():
    """Create a decoy chat machine"""
    with mock.patch("zodiac.main_screen.Fold.send_tx", mock.MagicMock()) as mocked:
        yield mocked


@pytest.mark.asyncio(loop_scope="module")
async def test_status_color_remains(app=Combo()):
    """Control test for status color reflected in text line"""
    from nnll_01 import nfo

    async with app.run_test() as pilot:
        expected = frozenset({"selectah"})
        ui_elements = pilot.app._nodes._get_by_id("fold_screen")
        nfo([*ui_elements.query("*").nodes])
        # assert any([element for element in ui_elements if isinstance(element, Fold)]) is True
        assert ui_elements.query_one("#selectah").classes == expected


@pytest.mark.asyncio(loop_scope="module")
async def test_status_color_continues_to_remain(mock_generate_response, app=Combo()):
    """Ensure cannot accidentally trigger"""
    async with app.run_test() as pilot:
        # ensure no accidental triggers
        await pilot.press("x", "tab")
        expected = frozenset({"selectah"})
        ui_elements = pilot.app._nodes._get_by_id("fold_screen")
        assert ui_elements.query_one("#selectah").classes == expected
        mock_generate_response.assert_not_called()


@pytest.mark.asyncio(loop_scope="module")
async def test_status_color_changes(mock_generate_response, app=Combo()):
    """Ensure color changes when activated"""
    async with app.run_test() as pilot:
        text_insert = "chunk"
        ui_elements = pilot.app._nodes._get_by_id("fold_screen")
        ui_elements.query_one("#message_panel").insert(text_insert)
        ui_elements.focus()
        await pilot.press("k", "tab", "enter")
        expected = frozenset({"selectah"})
        assert ui_elements.query_one("#selectah").classes == expected

        # print(pilot.app.query_one("#selectah").classes)
    mock_generate_response.assert_called_once()
    # last_model = next(iter(ui_elements.int_proc.models))
    # nfo(last_model)
    # pilot.app.exit()
