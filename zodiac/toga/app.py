#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import Callable, Optional

import asyncio
import toga
import toga.app
from toga.constants import Direction
from toga.style import Pack
from toga import Key
from zodiac.streams.model_stream import ModelStream
from zodiac.streams.task_stream import TaskStream


class Interface(toga.App):
    units = [["characters / ", 00000], ["tokens / ", 00000], ["seconds ″", 0]]

    async def ticker(self, widget: Callable, external: bool = False, **kwargs) -> None:
        """Process and synthesize input data based on selected model.\n
        :param widget: The UI widget that triggered this action, typically used for state management.\n
        :type widget: toga.widgets
        :param external: Indicates whether the processing should be handled externally (e.g., via clipboard), defaults to False
        :type external: bool"""
        from zodiac.toga.synthesis import synthesize
        from zodiac.text_machine import QASignature

        prompts = {"text": self.message_panel.value, "audio": [0], "image": []}
        # selection = self.model_stack.value
        self.chat.active_models(self.registry_entry, sig=QASignature, streaming=True)
        self.status.text = f"Beginning processing : {self.model_stack.value}" + self.status.text
        self.response_panel.scroll_to_bottom()
        async for prediction in synthesize(chat=self.chat, tx_data=prompts, mode_out=self.out_types.value):
            if prediction:  # and not external:
                self.response_panel.value += prediction.replace(
                    "/n",
                    """
""",
                )
        # if external:
        #     import pyperclip
        #     pyperclip.set_clipboard("pyobjc")
        # if external and pyperclip.is_available:
        #     await pyperclip.copy(prediction)
        #     await pyperclip.paste()
        # if not prediction:
        #     self.status.text = "Processing complete."

    async def halt(self, widget, **kwargs) -> None:
        """Stop processing prompt\n
        :param widget: The calling widget object"""
        self.status.text = "Processing cancelled."

    async def include_file(self, widget, **kwargs) -> None:
        import json

        try:
            file_path_named = await self.main_window.dialog(toga.OpenFileDialog(title="Attach a file to the prompt"))
            self.status.text = f"Reading : {file_path_named}"
            if file_path_named is not None:
                from nnll.metadata.json_io import read_json_file

                file_contents = read_json_file(file_path_named)
                self.message_panel.scroll_to_bottom()
                self.message_panel.value = json.dumps(file_contents)
            else:
                self.status.text = "Attachment cancelled, no file selected. " + self.status_text
        except (ValueError, json.JSONDecodeError):
            self.status.text = "Attachment cancelled, file could not be read... " + self.status_text

    async def on_select_handler(self, widget, **kwargs):
        """React to input/output choice\n
        :param widget: The widget that triggered the event."""
        selection = widget.value
        self.registry_entry = next(iter(registry["entry"] for registry in self.model_source._graph.registry_entries if selection in registry["entry"].model))
        await self.populate_task_stack()
        await self.update_status(selection)

    async def update_status(self, selection):
        self.status.text = f"In = {self.in_types.value.title()} / Out = {self.out_types.value.title()}" if selection else "Select conversion."

    async def traverse(self, slider, **kwargs):
        await self.update_status(slider.value)
        traversal = f" - {self.chart_path} {self.model_stack.value} {slider.value}"
        self.status.text += traversal

    async def model_graph(self):
        """Builds the model graph."""
        self.model_source = ModelStream()
        self.task_source = TaskStream()
        await self.model_source.model_graph()

    async def create_chat(self):
        from zodiac.text_machine import TextMachine

        self.chat = TextMachine()

    async def token_estimate(self, widget, **kwargs):
        from zodiac.providers.token_counters import tk_count

        token_count, character_count = await tk_count(self.registry_entry.model, widget.value)
        formatted_units = [f"{unit[0]}{unit[1]}" for unit in self.units]
        self.char_units.text = "".join(formatted_units[0]) + str(character_count)
        self.token_units.text = "".join(formatted_units[1]) + str(token_count)
        self.sec_units.text = "".join(formatted_units[2])
        # setattr(self, unit[0], toga.Label(f"{unit[2]}"))
        # setattr(self, unit[0] + "_symbol", toga.Label(unit[1]))

    async def populate_in_types(self):
        """Builds the input types selection."""

        in_edge_names = await self.model_source.show_edges()
        self.in_types.items = in_edge_names

    async def populate_out_types(self):
        """Builds the output types selection."""

        out_edges = await self.model_source.show_edges(target=True)
        self.out_types.items = out_edges

    async def populate_model_stack(self, widget: Optional[Callable] = None):
        """Builds the model stack selection dropdown."""
        await self.model_source.clear()
        if self.in_types.value and self.out_types.value:
            models = await self.model_source.trace_models(self.in_types.value, self.out_types.value)
            self.model_stack.items = models
            self.chart_path = await self.model_source.chart_path()
            self.path_slider.tick_count = len(self.chart_path)

    async def populate_task_stack(self, widget: Optional[Callable] = None):
        """Builds the task stack selection dropdown."""
        selection = self.model_stack.value
        registry_entry = next(iter(registry["entry"] for registry in self.model_source._graph.registry_entries if selection in registry["entry"].model))
        await self.task_source.set_filter_type(self.in_types.value, self.out_types.value)
        tasks = await self.task_source.trace_tasks(registry_entry)
        # if tasks:
        # self.task_stack.style = Pack(flex=1, visibility="visible")
        self.task_stack.items = tasks

    def initialize_widgets(self):
        """Create the main input fields"""
        self.status = toga.Label("Ready.")
        self.counter = toga.Row(style=Pack(height=20, flex=1, align_items="center", justify_content="center", gap=5, margin=5))
        formatted_units = [f"{unit[0]}{unit[1]}" for unit in self.units]
        self.char_units = toga.Label("".join(formatted_units[0]))
        self.token_units = toga.Label("".join(formatted_units[1]))
        self.sec_units = toga.Label("".join(formatted_units[2]))
        self.counter.children.extend([self.char_units, self.token_units, self.sec_units])
        self.path_slider = toga.Slider(min=0, tick_count=2, on_change=self.traverse, style=Pack(flex=1, margin=5))
        self.counter_slider = toga.Column(children=[self.counter, self.path_slider], style=Pack(flex=1))
        self.in_types = toga.Selection(items=[], style=Pack(flex=0.25), on_change=self.populate_model_stack)
        self.out_types = toga.Selection(items=[], style=Pack(flex=0.25), on_change=self.populate_model_stack)

        self.model_stack = toga.Selection(items=[], on_change=self.on_select_handler, style=Pack(flex=0.5))
        self.task_stack = toga.Selection(items=[], style=Pack(flex=1))
        self.parameter_stack = toga.Column(children=[self.model_stack, self.task_stack], align_items="end", text_direction="rtl", style=Pack(gap=10))
        intent_fields = toga.Column(children=[self.in_types, self.out_types], align_items="start", text_direction="ltr", style=Pack(gap=10))
        model_fields = toga.Row(children=[intent_fields, self.counter_slider, self.parameter_stack], vertical_align_items="center")
        status_bar = toga.Box(children=[self.status], style=Pack(flex=1, height=10))
        center_panel = toga.Column(children=[model_fields, status_bar], style=Pack(margin=5))
        self.message_panel = toga.MultilineTextInput(value="Message", style=Pack(flex=1), on_change=self.token_estimate)
        combined_top = toga.Column(children=[self.message_panel, center_panel], style=Pack(flex=1))

        self.response_panel = toga.MultilineTextInput(readonly=True, value="", style=Pack(flex=5))
        self.center_layout = toga.SplitContainer(content=[combined_top, self.response_panel], direction=Direction.HORIZONTAL, flex=20, margin=0)

    def initialize_layout(self):
        """Create the layout of the application."""
        self.main_window.content = self.center_layout

    def startup(self):
        """Startup Logic. Initialize widgets and layout, then asynchronous tasks for populating datagets"""
        self.main_window = toga.MainWindow()
        control_group = toga.Group("Controls", order=40)
        start = toga.Command(
            self.ticker,
            text="Start",
            tooltip="Run the current available prompts.",
            shortcut=Key.MOD_1 + Key.ENTER,
            group=control_group,
            section=0,
        )
        stop = toga.Command(
            self.halt,
            text="Stop",
            tooltip="Cancel the current sequence generation.",
            shortcut=Key.ESCAPE,
            group=control_group,
            section=0,
        )
        add_file = toga.Command.standard(
            self,
            toga.Command.OPEN,
            text="Add File...",
            tooltip="Attach a file to the prompt.",
            shortcut=Key.MOD_1 + Key.O,
            action=self.include_file,
            group=control_group,
            section=1,
        )
        self.commands.add(start, stop, add_file)
        # self.main_window.toolbar.add(add_file)
        self.initialize_widgets()
        self.initialize_layout()

        asyncio.create_task(self.model_graph())
        asyncio.create_task(self.create_chat())
        asyncio.create_task(self.populate_in_types())
        asyncio.create_task(self.populate_out_types())
        asyncio.create_task(self.populate_model_stack())
        asyncio.create_task(self.populate_task_stack())

        self.main_window.show()


def main():
    """The entry point for the application."""
    app = Interface("Shadowbox", "org.beeware.toga.examples.table_source")
    app.main_loop()
