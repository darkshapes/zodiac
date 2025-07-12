#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

import os
import asyncio
from typing import Callable, Optional

import toga
import toga.app
from toga import Key
from toga.constants import Direction
from toga.style import Pack

from zodiac.streams.model_stream import ModelStream
from zodiac.streams.task_stream import TaskStream
from zodiac.streams.token_stream import TokenStream


class Interface(toga.App):
    formatted_units = [" ❖ chr", " ⟐ tok", ' " sec ']
    bg_graph = "#070708"
    bg_text = "#1B1B1B"  # "#1B1B1B"  # "#09090B"
    bg = bg_text
    bg_static = "#5D5E62"
    activity = "#8122C4"

    static = Pack(color="#727378")
    fg_static = Pack(color="#8D8E94")
    scroll_buffer = 5000

    async def ticker(self, widget: Callable, external: bool = False, **kwargs) -> None:
        """Process and synthesize input data based on selected model.\n
        :param widget: The UI widget that triggered this action, typically used for state management.\n
        :type widget: toga.widgets
        :param external: Indicates whether the processing should be handled externally (e.g., via clipboard), defaults to False
        :type external: bool"""
        from zodiac.toga.signatures import Predictor, ready_predictor
        from litellm.types.utils import ModelResponseStream
        from dspy.streaming import StreamResponse, StatusMessage
        from dspy import Prediction, streamify, context

        await self.token_source.set_tokenizer(self.registry_entry)
        prompts = {"text": self.message_panel.value, "audio": [0], "image": []}
        self.status.style = Pack(color=self.activity)
        context_kwargs, predictor_kwargs = await ready_predictor(self.registry_entry)
        with context(**context_kwargs):
            program = streamify(Predictor(), **predictor_kwargs)
            output = program(question=prompts["text"])

            async for prediction in output:
                if isinstance(prediction, ModelResponseStream) and prediction["choices"][0]["delta"]["content"]:
                    self.response_panel.value += prediction["choices"][0]["delta"]["content"]
                elif isinstance(prediction, StreamResponse):
                    self.response_panel.value += prediction.chunk
                elif hasattr(prediction, "answer") and isinstance(prediction, Prediction):
                    self.response_panel.value += prediction.answer
                elif isinstance(prediction, StatusMessage):
                    self.status.text = prediction.message
                # print(str(prediction))
        self.response_panel.value += "\n---\n\n"
        self.status.style = Pack(color=self.bg_static)
        return widget

    async def empty_prompt(self, widget, **kwargs) -> None:
        """Clears the prompt input area.
        :param widget: Triggering widget"""
        self.message_panel.value = ""

    async def halt(self, widget, **kwargs) -> None:
        """Stop processing prompt\n
        :param widget: The calling widget object"""
        self.status.text = "Cancelled."

    async def include_file(self, widget, **kwargs) -> None:
        """Attaches a file's contents to the prompt area.
        :param widget: Triggering widget"""
        import json

        try:
            file_path_named = await self.main_window.dialog(toga.OpenFileDialog(title="Attach a file to the prompt"))
            self.status.text = f"Read. {file_path_named}"
            if file_path_named is not None:
                from nnll.metadata.json_io import read_json_file

                file_contents = read_json_file(file_path_named)
                self.message_panel.scroll_to_bottom()
                self.message_panel.value = json.dumps(file_contents)
                self.status.text = f"Attached {os.path.basename(file_path_named)}."
            else:
                self.status.text = "No file. "
        except (ValueError, json.JSONDecodeError):
            self.status.text = "Read failed... "

    # async def reset_position(self, widget, **kwargs) -> None:
    #     """Scrolls text panel to bottom after content update.
    #     :param widget: text panel widget
    #     """
    #     setattr(self, "position_counter", getattr(self, "position_counter", 0) + 1)
    #     if max(self.scroll_buffer, self.position_counter) >= self.scroll_buffer:
    #         self.position_counter = 0
    #         widget.scroll_to_bottom()

    async def on_select_handler(self, widget, **kwargs):
        """React to input/output choice\n
        :param widget: The widget that triggered the event."""
        selection = widget.value
        registry_entry = next(iter(registry["entry"] for registry in self.model_source._graph.registry_entries if selection in registry["entry"].model))
        self.registry_entry = registry_entry
        await self.populate_task_stack()
        await self.token_source.set_tokenizer(self.registry_entry)

    async def model_graph(self):
        """Builds the model graph."""
        await self.model_source.model_graph()

    async def token_estimate(self, widget, **kwargs):
        """Updates character and token count based on user input.
        :param widget: Input widget providing text"""
        token_count, character_count = await self.token_source.token_count(message=self.message_panel.value)
        self.character_stats.text = "{:02}".format(character_count) + "".join(self.formatted_units[0])
        self.token_stats.text = "{:02}".format(token_count) + "".join(self.formatted_units[1])
        self.time_stats.text = "{:02}".format(0.0) + "".join(self.formatted_units[2])

    async def populate_in_types(self):
        """Builds the input types selection."""
        in_edge_names = await self.model_source.show_edges()
        self.input_types.items = in_edge_names

    async def populate_out_types(self):
        """Builds the output types selection."""
        out_edges = await self.model_source.show_edges(target=True)
        self.output_types.items = out_edges

    async def populate_model_stack(self, widget: Optional[Callable] = None):
        """Builds the model stack selection dropdown."""

        await self.model_source.clear()
        if self.input_types.value and self.output_types.value:
            models = await self.model_source.trace_models(self.input_types.value, self.output_types.value)
            self.model_stack.items = models  # [model[0][:20] for model in models if len(model[0]) > 20]
            await self.token_estimate(widget=self.message_panel)

    async def populate_task_stack(self, widget: Optional[Callable] = None):
        """Builds the task stack selection dropdown."""
        selection = self.model_stack.value
        registry_entry = next(
            iter(
                registry["entry"]  # formatting
                for registry in self.model_source._graph.registry_entries  # formatting
                if selection in registry["entry"].model
            )
        )
        await self.task_source.set_filter_type(self.input_types.value, self.output_types.value)
        tasks = await self.task_source.trace_tasks(registry_entry)

        self.task_stack.items = tasks

    async def switch_tabs(self, widget: Optional[Callable] = None):
        """Switches between text and graph tabs.
        :param widget: The triggering widget (optional), defaults to None"""
        self.browser_panel.evaluate_javascript("location.reload();")
        self.bg = self.bg_graph if self.bg == self.bg_text else self.bg_text
        self.final_layout.style.background_color = self.bg
        self.final_layout.refresh()

    def initialize_inputs(self):
        """Initializes UI elements for input handling."""
        self.character_stats = toga.Label("{:02}".format(0) + "".join(self.formatted_units[0]), **self.fg_static)
        self.token_stats = toga.Label("{:02}".format(0) + "".join(self.formatted_units[1]), **self.fg_static)
        self.time_stats = toga.Label("{:02}".format(0.0) + "".join(self.formatted_units[2]), **self.fg_static)
        self.status = toga.Label("Ready.", style=Pack(color=self.bg_static))
        self.input_types = toga.Selection(items=[], on_change=self.populate_model_stack)
        self.output_types = toga.Selection(items=[], on_change=self.populate_model_stack)
        self.model_stack = toga.Selection(items=[], on_change=self.on_select_handler)
        self.task_stack = toga.Selection(items=[])
        self.message_panel = toga.MultilineTextInput(placeholder="Prompt", on_change=self.token_estimate, style=Pack(flex=0.66, margin=10))
        self.browser_panel = toga.WebView(url="http://127.0.0.1:8188")
        self.audio_panel = toga.Canvas()
        self.response_panel = toga.MultilineTextInput(readonly=True, placeholder="Response", style=Pack(flex=5))  # , on_change=self.reset_position))

    def initialize_static(self):
        """Create the main input fields"""

        top_left_buffer = toga.Column(
            children=[toga.Label("From:", style=Pack(color="grey")), toga.Label("To:", **self.static)],
            justify_content="end",
            style=Pack(
                flex=0.1,
                margin_top=3,
                align_items="end",
                justify_content="end",
                gap=15,
            ),
        )
        intent_fields = toga.Column(
            children=[self.input_types, self.output_types],  # , live_stats
            align_items="start",
            text_direction="ltr",
            style=Pack(gap=10, margin="2", flex=0.25),
        )
        process_fields = toga.Column(
            children=[self.model_stack, self.task_stack],
            align_items="end",
            text_direction="rtl",
            style=Pack(gap=10, margin="2", flex=0.25),
        )
        line_displays = toga.Column(
            children=[self.character_stats, self.token_stats, self.time_stats, self.status],
            style=Pack(flex=1, gap=2, margin_left=2),
        )
        top_right_buffer = toga.Column(justify_content="end", style=Pack(flex=0.33))

        status_bar = toga.Box(
            children=[top_left_buffer, intent_fields, process_fields, line_displays, top_right_buffer],
            style=Pack(flex=0, margin=10),
        )  # height=10,

        left_buffer = toga.Column(justify_content="start", style=Pack(flex=0.33))
        right_buffer = toga.Column(justify_content="end", style=Pack(flex=0.33))
        center_response = toga.Box(children=[self.response_panel], style=Pack(flex=1))
        center_prompt = toga.Box(children=[self.message_panel], style=Pack(flex=1))
        lower_section = toga.Row(children=[left_buffer, center_prompt, right_buffer])
        tab_panel = toga.OptionContainer(
            content=[
                ("Output", center_response),
                ("Graph", self.browser_panel),
            ],
            on_select=self.switch_tabs,
            style=Pack(background_color="#000000", flex=2),
            id="tab_panel",
        )
        resize_area = toga.SplitContainer(
            content=[tab_panel, lower_section],
            direction=Direction.HORIZONTAL,
            style=Pack(flex=3),
        )

        self.final_layout = toga.Column(children=[status_bar, resize_area], style=Pack(background_color=self.bg_text, flex=1))

    def initialize_layout(self):
        """Create the layout of the application."""
        self.main_window.content = self.final_layout

    def startup(self):
        """Startup Logic. Initialize widgets and layout, then asynchronous tasks for populating datagets"""
        self.main_window = toga.MainWindow()
        self.model_source = ModelStream()
        self.task_source = TaskStream()
        self.token_source = TokenStream()

        # control_group = toga.Group("Controls", order=40)
        start = toga.Command(
            self.ticker,
            text="Start",
            tooltip="Run the current available prompts.",
            shortcut=Key.MOD_1 + Key.ENTER,
            group=toga.Group.APP,
            section=-1,
        )
        stop = toga.Command(
            self.halt,
            text="Stop",
            tooltip="Cancel the current sequence generation.",
            shortcut=Key.ESCAPE,
            group=toga.Group.APP,
            section=0,
        )
        attach = toga.Command.standard(
            self,
            toga.Command.OPEN,
            text="Attach File...",
            tooltip="Attach a file to the prompt.",
            shortcut=Key.MOD_1 + Key.O,
            action=self.include_file,
            group=toga.Group.APP,
            section=1,
        )
        clear = toga.Command(
            self.empty_prompt,
            text="Clear Prompt",
            tooltip="Empty the prompt field.",
            shortcut=Key.MOD_3 + Key.BACKSPACE,
            group=toga.Group.APP,
            section=2,
        )
        self.commands.add(start, stop, attach, clear)

        self.initialize_inputs()
        self.initialize_static()
        self.initialize_layout()
        asyncio.create_task(self.model_graph())
        asyncio.create_task(self.token_estimate(self))
        asyncio.create_task(self.populate_in_types())
        asyncio.create_task(self.populate_out_types())
        asyncio.create_task(self.populate_model_stack())
        asyncio.create_task(self.populate_task_stack())
        self.main_window.show()


def main():
    """The entry point for the application."""
    app = Interface(
        formal_name="Shadowbox",
        app_id="org.darkshapes.shadowbox",
        app_name="sdbx",
        author="Darkshapes",
        home_page="https://darkshapes.github.io",
        description=" A generative AI instrument. ",
    )
    app.icon = toga.Icon(path="resources/anomaly_128x")
    app.main_loop()
