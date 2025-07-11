# # SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# # <!-- // /*  d a r k s h a p e s */ -->

# import os
# import asyncio
# from typing import Callable, Optional

# import toga
# from toga import Key
# from toga.constants import Direction
# from toga.style import Pack


# class StaticApp:
#     def __init__(self):
#         self.formatted_units = [" ❖ chr", " ⟐ tok", ' " sec ']
#         self.bg = None
#         self.bg_static = "#5D5E62"
#         self.static = Pack(color="#727378")
#         self.fg_static = Pack(color="#8D8E94")

#     async def initialize_inputs(self):
#         self.character_stats = toga.Label("{:02}".format(0) + "".join(self.formatted_units[0]), **self.fg_static)
#         self.token_stats = toga.Label("{:02}".format(0) + "".join(self.formatted_units[1]), **self.fg_static)
#         self.time_stats = toga.Label("{:02}".format(0.0) + "".join(self.formatted_units[2]), **self.fg_static)
#         self.status = toga.Label("Ready.", style=Pack(color=self.bg_static))
#         self.input_types = toga.Selection(items=[], on_change=self.populate_model_stack)
#         self.output_types = toga.Selection(items=[], on_change=self.populate_model_stack)
#         self.model_stack = toga.Selection(items=[], on_change=self.on_select_handler)
#         self.task_stack = toga.Selection(items=[])
#         self.message_panel = toga.MultilineTextInput(placeholder="Prompt", on_change=self.token_estimate, style=Pack(flex=0.66, margin=10))
#         self.browser_panel = toga.WebView(url="http://127.0.0.1:8188")
#         self.audio_panel = toga.Canvas()
#         self.response_panel = toga.MultilineTextInput(readonly=True, placeholder="Response", on_change=self.reset_position, style=Pack(flex=5))

#     async def initialize_static(self, parent):
#         """Create the main input fields"""

#         top_left_buffer = toga.Column(
#             children=[toga.Label("In", style=Pack(color="grey")), toga.Label("Out", **self.static)],
#             justify_content="end",
#             style=Pack(
#                 flex=0.1,
#                 margin_top=3,
#                 align_items="end",
#                 justify_content="end",
#                 gap=15,
#             ),
#         )
#         intent_fields = toga.Column(
#             children=[self.input_types, self.output_types],  # , live_stats
#             align_items="start",
#             text_direction="ltr",
#             style=Pack(gap=10, margin="2", flex=0.25),
#         )
#         process_fields = toga.Column(
#             children=[self.model_stack, self.task_stack],
#             align_items="end",
#             text_direction="rtl",
#             style=Pack(gap=10, margin="2", flex=0.25),
#         )
#         line_displays = toga.Column(
#             children=[self.character_stats, self.token_stats, self.time_stats, self.status],
#             style=Pack(flex=1, gap=2, margin_left=2),
#         )
#         top_right_buffer = toga.Column(justify_content="end", style=Pack(flex=0.33))

#         status_bar = toga.Box(
#             children=[top_left_buffer, intent_fields, process_fields, line_displays, top_right_buffer],
#             style=Pack(flex=0, margin=10),
#         )  # height=10,

#         left_buffer = toga.Column(justify_content="start", style=Pack(flex=0.33))
#         right_buffer = toga.Column(justify_content="end", style=Pack(flex=0.33))
#         center_response = toga.Box(children=[self.response_panel], style=Pack(flex=1))
#         center_prompt = toga.Box(children=[self.message_panel], style=Pack(flex=1))
#         lower_section = toga.Row(children=[left_buffer, center_prompt, right_buffer])
#         tab_panel = toga.OptionContainer(
#             content=[
#                 ("Output", center_response),
#                 ("Graph", self.browser_panel),
#             ],
#             style=Pack(background_color="#000000", flex=2),
#             id="tab_panel",
#         )
#         resize_area = toga.SplitContainer(
#             content=[tab_panel, lower_section],
#             direction=Direction.HORIZONTAL,
#             style=Pack(flex=3),
#         )

#         self.final_layout = toga.Column(children=[status_bar, resize_area], style=Pack(background_color=self.bg_text, flex=1))
#         parent.main_window.content = self.final_layout
