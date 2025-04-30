#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=unused-import, W0212

# type: ignore
import pytest
from textual.containers import Container, Horizontal# noqa
from textual.widgets import DataTable, Footer, TextArea, ContentSwitcher# noqa
from textual.widgets._select import SelectCurrent, SelectOverlay# noqa

from zodiac.main_screen import (Fold,MessagePanel, InputTag, ResponsiveLeftTop, ResponsiveRightBottom, OutputTag,Static,Selectah) # noqa
from zodiac.__main__ import Combo
from zodiac.response_panel import ResponsePanel# noqa
from zodiac.display_bar import DisplayBar# noqa
from zodiac.voice_panel import VoicePanel# noqa


@pytest.mark.asyncio
async def test_screen_widget_contents(app=Combo()):
    """Test elements in screen load"""
    from nnll_01 import nfo
    from sys import modules as sys_modules
    async with app.run_test() as pilot:
        ui_elements = pilot.app._nodes._get_by_id('fold_screen')
        node_list = ui_elements.query("*")
        panel_class_names = [panel_name.__class__.__name__ for panel_name in node_list]
        nfo(list([*panel_class_names]))
        nfo([x for x in panel_class_names if x in sys_modules])
        # nfo(list[if  in sys_modules]))
        assert len([panel_name for panel_name in node_list if str(panel_name.__class__.__name__) in sys_modules]) != 0
