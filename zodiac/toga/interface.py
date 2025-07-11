# # SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# # <!-- // /*  d a r k s h a p e s */ -->

# import os
# import asyncio
# from typing import Callable, Optional

# import toga
# from toga import Key
# from zodiac.streams.model_stream import ModelStream
# from zodiac.streams.task_stream import TaskStream
# from zodiac.streams.token_stream import TokenStream


# class DynamicApp:
#     character_stats = None

#     def __init__(self):
#         self.registry_entry = None
#         self.model_source = ModelStream()
#         self.task_source = TaskStream()
#         self.token_source = TokenStream()

#     async def initialize(self):
#         asyncio.create_task(self.token_estimate(self))
#         asyncio.create_task(self.model_graph())
#         asyncio.create_task(self.populate_in_types())
#         asyncio.create_task(self.populate_out_types())
#         asyncio.create_task(self.populate_model_stack())
#         asyncio.create_task(self.populate_task_stack())

#     async def ticker(self, widget: Callable, external: bool = False, **kwargs) -> None:
#         """Process and synthesize input data based on selected model.\n
#         :param widget: The UI widget that triggered this action, typically used for state management.\n
#         :type widget: toga.widgets
#         :param external: Indicates whether the processing should be handled externally (e.g., via clipboard), defaults to False
#         :type external: bool"""
#         from zodiac.toga.signatures import text_qa_stream
#         from dspy.streaming import StatusMessage

#         prompts = {"text": self.message_panel.value, "audio": [0], "image": []}
#         # self.status.text = "Processing..."
#         async for chunk in text_qa_stream(registry_entry=self.registry_entry, prompt=prompts["text"]):
#             if chunk and isinstance(chunk, StatusMessage):
#                 self.status.text = chunk.message
#             elif chunk:
#                 self.response_panel.value += chunk

#     async def empty_prompt(self, widget, **kwargs) -> None:
#         self.message_panel.value = ""

#     async def halt(self, widget, **kwargs) -> None:
#         """Stop processing prompt\n
#         :param widget: The calling widget object"""
#         self.status.text = "Cancelled."

#     async def include_file(self, widget, **kwargs) -> None:
#         import json

#         try:
#             file_path_named = await self.main_window.dialog(toga.OpenFileDialog(title="Attach a file to the prompt"))
#             self.status.text = f"Read. {file_path_named}"
#             if file_path_named is not None:
#                 from nnll.metadata.json_io import read_json_file

#                 file_contents = read_json_file(file_path_named)
#                 self.message_panel.scroll_to_bottom()
#                 self.message_panel.value = json.dumps(file_contents)
#                 self.status.text = f"Attached {os.path.basename(file_path_named)}."
#             else:
#                 self.status.text = "No file. "
#         except (ValueError, json.JSONDecodeError):
#             self.status.text = "Read failed... "

#     async def reset_position(self, widget, **kwargs) -> None:
#         widget.scroll_to_bottom()

#     async def on_select_handler(self, widget, **kwargs):
#         """React to input/output choice\n
#         :param widget: The widget that triggered the event."""
#         selection = widget.value
#         registry_entry = next(iter(registry["entry"] for registry in self.model_source._graph.registry_entries if selection in registry["entry"].model))
#         self.registry_entry = registry_entry
#         await self.populate_task_stack()
#         await self.token_source.set_tokenizer(registry_entry)

#     async def model_graph(self):
#         """Builds the model graph."""
#         await self.model_source.model_graph()

#     async def token_estimate(self, widget, **kwargs):
#         token_count, character_count = await self.token_source.token_count(widget.value)
#         self.character_stats.text = "{:02}".format(character_count) + "".join(self.formatted_units[0])
#         self.token_stats.text = "{:02}".format(token_count) + "".join(self.formatted_units[1])
#         self.time_stats.text = "{:02}".format(0.0) + "".join(self.formatted_units[2])

#     async def populate_in_types(self):
#         """Builds the input types selection."""

#         in_edge_names = await self.model_source.show_edges()
#         self.input_types.items = in_edge_names

#     async def populate_out_types(self):
#         """Builds the output types selection."""

#         out_edges = await self.model_source.show_edges(target=True)
#         self.output_types.items = out_edges

#     async def populate_model_stack(self, widget: Optional[Callable] = None):
#         """Builds the model stack selection dropdown."""

#         await self.model_source.clear()
#         if self.input_types.value and self.output_types.value:
#             models = await self.model_source.trace_models(self.input_types.value, self.output_types.value)
#             self.model_stack.items = models  # [model[0][:20] for model in models if len(model[0]) > 20]

#     async def populate_task_stack(self, widget: Optional[Callable] = None):
#         """Builds the task stack selection dropdown."""
#         selection = self.model_stack.value
#         registry_entry = next(
#             iter(
#                 registry["entry"]  # formatting
#                 for registry in self.model_source._graph.registry_entries  # formatting
#                 if selection in registry["entry"].model
#             )
#         )
#         await self.task_source.set_filter_type(self.input_types.value, self.output_types.value)
#         tasks = await self.task_source.trace_tasks(registry_entry)

#         self.task_stack.items = tasks

#     async def switch_tabs(self, widget: Optional[Callable] = None):
#         self.bg = self.bg_graph if self.bg == self.bg_text else self.bg_text
#         self.final_layout.style.background_color = self.bg
#         self.final_layout.refresh()
#         self.browser_panel.evaluate_javascript("location.reload();")

#     async def add_commands(self, parent):
#         # control_group = toga.Group("Controls", order=40)
#         start = toga.Command(
#             self.ticker,
#             text="Start",
#             tooltip="Run the current available prompts.",
#             shortcut=Key.MOD_1 + Key.ENTER,
#             group=toga.Group.APP,
#             section=-1,
#         )
#         stop = toga.Command(
#             self.halt,
#             text="Stop",
#             tooltip="Cancel the current sequence generation.",
#             shortcut=Key.ESCAPE,
#             group=toga.Group.APP,
#             section=0,
#         )
#         attach = toga.Command.standard(
#             self,
#             toga.Command.OPEN,
#             text="Attach File...",
#             tooltip="Attach a file to the prompt.",
#             shortcut=Key.MOD_1 + Key.O,
#             action=self.include_file,
#             group=toga.Group.APP,
#             section=1,
#         )
#         clear = toga.Command(
#             self.empty_prompt,
#             text="Clear Prompt",
#             tooltip="Empty the prompt field.",
#             shortcut=Key.MOD_3 + Key.BACKSPACE,
#             group=toga.Group.APP,
#             section=2,
#         )
#         parent.commands.add(start, stop, attach, clear)

#     # async def ticker(self, widget: Callable, external: bool = False, **kwargs) -> None:
#     #     """Process and synthesize input data based on selected model.\n
#     #     :param widget: The UI widget that triggered this action, typically used for state management.\n
#     #     :type widget: toga.widgets
#     #     :param external: Indicates whether the processing should be handled externally (e.g., via clipboard), defaults to False
#     #     :type external: bool"""
#     #     from zodiac.toga.signatures import text_qa_stream
#     #     from dspy.streaming import StatusMessage

#     #     prompts = {"text": self.message_panel.value, "audio": [0], "image": []}
#     #     # self.status.text = "Processing..."
#     #     async for chunk in text_qa_stream(registry_entry=self.registry_entry, prompt=prompts["text"]):
#     #         if chunk and isinstance(chunk, StatusMessage):
#     #             self.status.text = chunk.message
#     #         elif chunk:
#     #             self.response_panel.value += chunk

#     # async def empty_prompt(self, widget, **kwargs) -> None:
#     #     self.message_panel.value = ""

#     # async def halt(self, widget, **kwargs) -> None:
#     #     """Stop processing prompt\n
#     #     :param widget: The calling widget object"""
#     #     self.status.text = "Cancelled."

#     # async def include_file(self, widget, **kwargs) -> None:
#     #     import json

#     #     try:
#     #         file_path_named = await self.main_window.dialog(toga.OpenFileDialog(title="Attach a file to the prompt"))
#     #         self.status.text = f"Read. {file_path_named}"
#     #         if file_path_named is not None:
#     #             from nnll.metadata.json_io import read_json_file

#     #             file_contents = read_json_file(file_path_named)
#     #             self.message_panel.scroll_to_bottom()
#     #             self.message_panel.value = json.dumps(file_contents)
#     #             self.status.text = f"Attached {os.path.basename(file_path_named)}."
#     #         else:
#     #             self.status.text = "No file. "
#     #     except (ValueError, json.JSONDecodeError):
#     #         self.status.text = "Read failed... "

#     # async def reset_position(self, widget, **kwargs) -> None:
#     #     self.widget.scroll_to_bottom()

#     # async def on_select_handler(self, widget, **kwargs):
#     #     """React to input/output choice\n
#     #     :param widget: The widget that triggered the event."""
#     #     selection = widget.value
#     #     registry_entry = next(iter(registry["entry"] for registry in self.model_source._graph.registry_entries if selection in registry["entry"].model))
#     #     self.registry_entry = registry_entry
#     #     await self.populate_task_stack()
#     #     await self.token_source.set_tokenizer(registry_entry)

#     # async def token_estimate(self, widget, **kwargs):
#     #     token_count, character_count = await self.token_source.token_count(widget.value)
#     #     self.static_interface.character_stats.text = "{:02}".format(character_count) + "".join(self.static_interface.formatted_units[0])
#     #     self.static_interface.token_stats.text = "{:02}".format(token_count) + "".join(self.static_interface.formatted_units[1])
#     #     self.static_interface.time_stats.text = "{:02}".format(0.0) + "".join(self.static_interface.formatted_units[2])

#     # async def populate_in_types(self):
#     #     """Builds the input types selection."""

#     #     in_edge_names = await self.model_source.show_edges()
#     #     self.input_types.items = in_edge_names

#     # async def populate_out_types(self):
#     #     """Builds the output types selection."""

#     #     out_edges = await self.model_source.show_edges(target=True)
#     #     self.output_types.items = out_edges

#     # async def populate_model_stack(self, widget: Optional[Callable] = None):
#     #     """Builds the model stack selection dropdown."""

#     #     await self.model_source.clear()
#     #     if self.input_types.value and self.output_types.value:
#     #         models = await self.model_source.trace_models(self.input_types.value, self.output_types.value)
#     #         self.model_stack.items = models  # [model[0][:20] for model in models if len(model[0]) > 20]

#     # async def populate_task_stack(self, widget: Optional[Callable] = None):
#     #     """Builds the task stack selection dropdown."""
#     #     selection = self.model_stack.value
#     #     registry_entry = next(
#     #         iter(
#     #             registry["entry"]  # formatting
#     #             for registry in self.model_source._graph.registry_entries  # formatting
#     #             if selection in registry["entry"].model
#     #         )
#     #     )
#     #     await self.task_source.set_filter_type(self.input_types.value, self.output_types.value)
#     #     tasks = await self.task_source.trace_tasks(registry_entry)

#     #     self.task_stack.items = tasks

#     # async def switch_tabs(self, widget: Optional[Callable] = None):
#     #     self.bg = self.bg_graph if self.bg == self.bg_text else self.bg_text
#     #     self.final_layout.style.background_color = self.bg
#     #     self.final_layout.refresh()
#     #     self.browser_panel.evaluate_javascript("location.reload();")
