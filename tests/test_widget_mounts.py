# import pytest
# from textual.containers import Container, Horizontal
# from textual.widgets import DataTable, Footer, Static, TextArea, _footer

# from package.display_bar import DisplayBar
# from package.fold import Fold
# from package.input_tag import InputTag
# from package.main_screen import ResponsiveLeftTop, ResponsiveRightBottom
# from package.message_panel import MessagePanel
# from package.__main__ import Combo
# from package.panel_swap import PanelSwap
# from package.response_panel import ResponsePanel
# from package.tag_line import TagLine
# from package.voice_panel import VoicePanel


# @pytest.mark.asyncio
# async def test_screen_widget_contents(app=Combo()):
#     """Test elements in screen load"""
#     async with app.run_test() as pilot:
#         ui_elements = list(pilot.app.query("*"))
#         assert isinstance(ui_elements[1], Footer)  # lowest element, then skip 2 footer keys
#         assert isinstance(ui_elements[2], _footer.FooterKey)  # keybinds 1 (go/del)
#         assert isinstance(ui_elements[3], _footer.FooterKey)  # keybinds 2 (escape/exit)
#         assert isinstance(ui_elements[4], _footer.FooterKey)  # keybinds 1 (enter)
#         assert isinstance(ui_elements[5], _footer.FooterKey)  # keybinds 2 (space)
#         assert isinstance(ui_elements[6], Horizontal)  # Layout grid
#         assert isinstance(ui_elements[7], ResponsiveLeftTop)  # central container
#         assert isinstance(ui_elements[8], Static)  # sidebar contents

#         assert isinstance(ui_elements[19], ResponsiveRightBottom)  # close sidebar
#         assert isinstance(ui_elements[20], Static)  # sidebar contents
#         assert isinstance(ui_elements[21], Static)  # More Sidebar contents contents


# @pytest.mark.asyncio
# async def test_centre_contents(app=Combo()):
#     """Test interactive elements"""
#     async with app.run_test() as pilot:
#         ui_elements = list(pilot.app.query("*"))
#         assert isinstance(ui_elements[9], Fold)  # centre screen
#         assert isinstance(ui_elements[10], Container)  # responsive input
#         assert isinstance(ui_elements[11], PanelSwap)  # widget swap
#         assert isinstance(ui_elements[12], MessagePanel)  # message panel
#         assert isinstance(ui_elements[13], VoicePanel)  # voice panel
#         # assert isinstance(ui_elements[13], VoicePanel)  # image panel
#         # assert isinstance(ui_elements[13], VoicePanel)  # video panel
#         assert isinstance(ui_elements[14], InputTag)  # type tag panel
#         assert isinstance(ui_elements[15], DisplayBar)  # display bar
#         assert isinstance(ui_elements[16], Container)  # responsive display
#         assert isinstance(ui_elements[17], ResponsePanel)  # response panel
#         assert isinstance(ui_elements[18], TagLine)  #  tag line
