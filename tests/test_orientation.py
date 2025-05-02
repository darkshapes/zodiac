import pytest

from zodiac.__main__ import Combo
from nnll_01 import nfo
from textual.screen import Screen
from textual.containers import Horizontal


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.asyncio(loop_scope="session")
async def test_responsive_layout(app=Combo()):
    """Screen rotation function"""
    async with app.run_test() as pilot:
        await pilot.resize_terminal(40, 20)
        fold_scr = pilot.app._nodes._get_by_id('fold_screen')
        expected = "app-grid-horizontal"
        nfo(fold_scr.query_one(Horizontal).classes)
        assert fold_scr.query_one(Horizontal).classes == frozenset({expected})

        await pilot.resize_terminal(39, 20)
        expected = "app-grid-vertical"
        assert fold_scr.query_one(Horizontal).classes == frozenset({expected})
