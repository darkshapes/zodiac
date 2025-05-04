#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=unused-import, W0212

# type: ignore
import pytest
from textual.containers import Container, Horizontal  # noqa

from zodiac.__main__ import Combo
from test_graph import mock_ollama_data, mock_hub_registry, test_mocked_hub, test_mocked_ollama, test_graph


@pytest.mark.asyncio(loop_scope="module")
async def test_screen_widget_contents(mock_ollama_data, mock_hub_registry, app=Combo()):
    """Test elements in screen load"""
    from nnll_01 import nfo
    import sys

    async with app.run_test() as pilot:
        ui_elements = pilot.app._nodes._get_by_id("fold_screen")
        node_list = ui_elements.query("*")
        panel_class_names = [panel_name.__class__.__name__ for panel_name in node_list]
        nfo("total nodes :", len(list([*panel_class_names])))
        nfo("nodes in sys.modules : ", len([panel_name.__class__.__module__ in sys.modules for panel_name in node_list]))
        # nfo(list[if  in sys_modules]))
        assert all(panel_name.__class__.__module__ in sys.modules for panel_name in node_list) is True
