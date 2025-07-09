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
    units = [["chr ", 000000, " / "], ["tok ", 000000, " / "], ["sec ", 000.00, "″"]]
    background = "#1B1B1B"  # "#09090B"

    async def ticker(self, widget: Callable, external: bool = False, **kwargs) -> None:
        """Process and synthesize input data based on selected model.\n
        :param widget: The UI widget that triggered this action, typically used for state management.\n
        :type widget: toga.widgets
        :param external: Indicates whether the processing should be handled externally (e.g., via clipboard), defaults to False
        :type external: bool"""
        from zodiac.toga.signatures import QATask
        from dspy import Prediction
        from litellm import ModelResponseStream
        from dspy.utils.exceptions import AdapterParseError

        prompts = {"text": self.message_panel.value, "audio": [0], "image": []}
        self.chat.ready(self.registry_entry, sig=QATask, streaming=True)
        self.status.text = f"Processing : {self.model_stack.value}" + self.status.text
        self.response_panel.scroll_to_bottom()
        async for prediction in self.chat(prompts=prompts):  # mode_out=self.out_types.value):
            try:
                async for chunk in prediction:
                    print(sum(len(x) for x in prediction))
                    if isinstance(chunk, Prediction):
                        if hasattr(chunk, "answer"):
                            self.response_panel.value += ""
                            self.status.text = "Processing complete."
                    elif chunk and isinstance(chunk, ModelResponseStream):
                        self.response_panel.value += (
                            chunk["choices"][0]["delta"]["content"].replace(
                                "/n",
                                """
            """,
                            )
                            if chunk["choices"][0]["delta"]["content"]
                            else str("")
                        )
            except (AdapterParseError, TypeError) as error_log:
                print(f"LM parse error : {error_log}")

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
        await self.update_status()

    async def update_status(self, widget: Callable = None):
        index = int(self.intent_swipe.value)
        self.current_intent.text = f"{self.chart_path[index]}"  # if selection else ""

    async def traverse(self, slider, **kwargs):
        await self.update_status()  # slider.value
        index = int(self.intent_swipe.value)
        traversal = f"{self.chart_path[index]}"  # {slider.value}"
        self.current_intent.text = traversal

    async def model_graph(self):
        """Builds the model graph."""
        self.model_source = ModelStream()
        self.task_source = TaskStream()
        await self.model_source.model_graph()

    async def create_chat(self):
        from zodiac.inference import InferenceProcessor

        self.chat = InferenceProcessor()

    async def token_estimate(self, widget, **kwargs):
        from zodiac.providers.token_counters import tk_count

        token_count, character_count = await tk_count(self.registry_entry.model, widget.value)
        formatted_units = [f"{unit[0]}{unit[1]}" for unit in self.units]
        self.character_stats.text = "".join(formatted_units[0]) + str(character_count)
        self.token_stats.text = "".join(formatted_units[1]) + str(token_count)
        self.time_stats.text = "".join(formatted_units[2])

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
        from decimal import Decimal

        await self.model_source.clear()
        if self.input_types.value and self.output_types.value:
            models = await self.model_source.trace_models(self.input_types.value, self.output_types.value)
            self.model_stack.items = [model[0][:20] for model in models if len(model[0]) > 20]
            self.chart_path = await self.model_source.chart_path()
            range = len(self.chart_path)
            self.intent_swipe.tick_count = range
            self.intent_swipe.max = Decimal(str(range - 1) + ".0")

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
        # if tasks:
        # self.task_stack.style = Pack(flex=1, visibility="visible")
        self.task_stack.items = tasks

    def initialize_inputs(self):
        self.character_stats = toga.Label("")
        self.token_stats = toga.Label("")
        self.time_stats = toga.Label("")
        self.status = toga.Label("Ready.")
        self.current_intent = toga.Label("", style=Pack(gap=2, margin=5))
        self.intent_swipe = toga.Slider(min=0, tick_count=2, on_change=self.traverse, style=Pack(flex=1, margin=5))
        self.input_types = toga.Selection(items=[], style=Pack(flex=0.25, background_color=self.background), on_change=self.populate_model_stack)
        self.output_types = toga.Selection(items=[], style=Pack(flex=0.25, background_color=self.background), on_change=self.populate_model_stack)
        self.model_stack = toga.Selection(items=[], style=Pack(flex=0.25, background_color=self.background), on_change=self.on_select_handler)
        self.task_stack = toga.Selection(items=[], style=Pack(flex=1, background_color=self.background))
        self.message_panel = toga.MultilineTextInput(value="Prompt", on_change=self.token_estimate, style=Pack(flex=0.1))
        self.response_panel = toga.MultilineTextInput(readonly=True, value="", style=Pack(flex=5))

    def initialize_static(self):
        """Create the main input fields"""
        prompt_stats = toga.Row(
            children=[self.character_stats, self.token_stats, self.time_stats],
            style=Pack(flex=3, height=20, gap=2, margin=5, background_color=self.background),
        )
        live_stats = toga.Row(children=[prompt_stats, self.current_intent])
        detail_fields = toga.Column(
            children=[live_stats, self.intent_swipe],
            style=Pack(flex=5, margin_left=0, margin_right=0, background_color=self.background),
        )
        process_fields = toga.Column(
            children=[self.model_stack, self.task_stack],
            align_items="end",
            text_direction="rtl",
            style=Pack(gap=10, background_color=self.background),
        )
        intent_fields = toga.Column(
            children=[self.input_types, self.output_types],
            align_items="start",
            text_direction="ltr",
            style=Pack(gap=10, background_color=self.background),
        )
        fields_bar = toga.Row(children=[intent_fields, detail_fields, process_fields], vertical_align_items="center")
        status_bar = toga.Box(children=[self.status], style=Pack(flex=1, height=10, background_color=self.background))
        display_bar = toga.Column(children=[fields_bar, status_bar], style=Pack(margin=5, background_color=self.background))
        top_center = toga.Column(children=[self.message_panel, display_bar], style=Pack(flex=0.66, background_color=self.background))
        browser_panel = toga.WebView(url="http://127.0.0.1:8188", style=Pack(background_color=self.background))
        audio_panel = toga.Canvas(style=Pack(background_color=self.background))
        model_graph = toga.Canvas(style=Pack(background_color=self.background))
        bottom_section = toga.OptionContainer(
            content=[
                ("Language", self.response_panel),
                ("Waveform", audio_panel),
                ("Model Graph", model_graph),
                ("Node Graph", browser_panel),
            ],
            style=Pack(background_color="#000000"),
        )
        left_buffer = toga.Column(justify_content="start", style=Pack(flex=0.33, background_color=self.background))
        right_buffer = toga.Column(justify_content="end", style=Pack(flex=0.33, background_color=self.background))
        top_section = toga.Row(children=[left_buffer, top_center, right_buffer], style=Pack(background_color=self.background))
        self.final_layout = toga.SplitContainer(
            content=[top_section, bottom_section],
            direction=Direction.HORIZONTAL,
            style=Pack(flex=20, margin=0, background_color=self.background),
        )

    def initialize_layout(self):
        """Create the layout of the application."""
        self.main_window.content = self.final_layout

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
        attach = toga.Command.standard(
            self,
            toga.Command.OPEN,
            text="Attack File...",
            tooltip="Attach a file to the prompt.",
            shortcut=Key.MOD_1 + Key.O,
            action=self.include_file,
            group=control_group,
            section=1,
        )
        self.commands.add(start, stop, attach)

        self.initialize_inputs()
        self.initialize_static()
        self.initialize_layout()
        asyncio.create_task(self.token_estimate(self))
        asyncio.create_task(self.model_graph())
        asyncio.create_task(self.create_chat())
        asyncio.create_task(self.populate_in_types())
        asyncio.create_task(self.populate_out_types())
        asyncio.create_task(self.populate_model_stack())
        asyncio.create_task(self.populate_task_stack())

        self.main_window.show()


def main():
    """The entry point for the application."""
    app = Interface("Shadowbox", "org.darkshapes.shadowbox", author="Darkshapes", home_page="https://darkshapes.github.io")
    app.main_loop()
