#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

import os
import asyncio
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from urllib3.exceptions import MaxRetryError, NewConnectionError
from typing import Callable

import toga
import toga.app
from toga import Key
from toga.constants import Direction
from toga.style import Pack

from zodiac.streams.model_stream import ModelStream
from zodiac.streams.task_stream import TaskStream
from zodiac.streams.token_stream import TokenStream
import platform
from dspy import Prediction, streamify, context as dspy_context, inspect_history

OS_NAME = platform.system  # replace with config from sdbx later


class Interface(toga.App):
    formatted_units = [" ❖ chr", " ⟐ tok", ' " sec ']
    bg_graph = "#070708"
    bg_text = "#1B1B1B"  # "#1B1B1B"  # "#09090B"
    bg = bg_text
    bg_static = "#5D5E62"
    activity = "#8122C4"

    static = Pack(color="#727378")
    fg_static = Pack(color="#8D8E94")
    scroll_buffer = 5000  # chunks required to scroll down
    graph_disabled = "http://localhost"
    graph_server = "http://127.0.0.1:8188"
    status_info = ("Connecting...", "Server?", "Ready.", "Done.", "No File.", "Read Failed.", "Attached.", "Copied.")
    _is_cancelled = False

    async def ticker(self, widget: Callable, external: bool = False, **kwargs) -> toga.Widget:
        """Process and synthesize input data based on selected model.\n
        :param widget: The UI widget that triggered this action, typically used for state management.\n
        :type widget: toga.widgets
        :param external: Indicates whether the processing should be handled externally (e.g., via clipboard), defaults to False
        :type external: bool"""
        from zodiac.toga.signatures import Predictor, ready_predictor
        from litellm.types.utils import ModelResponseStream  # StatusStreamingCallback
        from dspy.streaming import StatusMessage, StreamResponse

        self.response_panel.value += f"{os.path.basename(self.registry_entry.model)} :\n"

        await self.token_source.set_tokenizer(self.registry_entry)
        prompts = {"text": self.message_panel.value, "audio": [0], "image": []}
        context_kwargs, predictor_kwargs = await ready_predictor(self.registry_entry, dspy_stream=True, async_stream=True, cache=False)  # ,dspy_stream=False)
        self.response_panel.scroll_to_bottom()
        with dspy_context(**context_kwargs):
            self.program = streamify(Predictor(), **predictor_kwargs)
            async for prediction in self.program(question=prompts["text"]):
                if isinstance(prediction, ModelResponseStream) and prediction["choices"][0]["delta"]["content"]:
                    self.response_panel.value += prediction["choices"][0]["delta"]["content"]
                elif isinstance(prediction, StreamResponse):
                    self.response_panel.value += str(prediction.chunk)
                elif isinstance(prediction, Prediction):
                    self.response_panel.value += str(prediction.answer)
                elif isinstance(prediction, StatusMessage):
                    self.status_display.text = self.status_text_prefix + str(prediction.message)

        self.response_panel.value += "\n---\n\n"
        return widget

    async def halt(self, widget, **kwargs) -> None:
        """Stop processing prompt\n
        :param widget: The calling widget object"""
        if not self.program.done():
            import gc

            del self.program
            gc.collect()
            self.status_display.text = self.status_text_prefix + "Cancelled."

    async def empty_prompt(self, widget, **kwargs) -> None:
        """Clears the prompt input area.
        :param widget: Triggering widget"""
        self.message_panel.value = ""

    async def copy_reply(self, widget, **kwargs) -> None:
        """_summary_
        :param widget: _description_"""
        import pyperclip

        pyperclip.copy(self.response_panel.value)
        self.status_display.text = self.status_text_prefix + self.status_info[7]

    async def attach_file(self, widget, **kwargs) -> None:
        """Attaches a file's contents to the prompt area.
        :param widget: Triggering widget"""
        import json

        try:
            file_path_named = await self.main_window.dialog(toga.OpenFileDialog(title="Attach a file to the prompt"))
            self.status_display.text = f"Read. {file_path_named}"
            if file_path_named is not None:
                from nnll.metadata.json_io import read_json_file

                file_contents = read_json_file(file_path_named)
                self.message_panel.scroll_to_bottom()
                self.message_panel.value = json.dumps(file_contents)
                self.status_display.text = self.status_text_prefix + self.status_info[6]
            else:
                self.status_display.text = self.status_text_prefix + self.status_info[4]
        except (ValueError, json.JSONDecodeError):
            self.status_display.text = self.status_text_prefix + self.status_info[5]

    async def reset_position(self, widget, **kwargs) -> None:
        """Scrolls text panel to bottom after content update.
        :param widget: text panel widget
        """
        setattr(self, "position_counter", getattr(self, "position_counter", 0) + 1)
        if max(self.scroll_buffer, self.position_counter) >= self.scroll_buffer:
            self.position_counter = 0
            widget.scroll_to_bottom()

    async def on_select_handler(self, widget, **kwargs) -> None:
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

    async def token_estimate(self, widget, **kwargs) -> None:
        """Updates character and token count based on user input.
        :param widget: Input widget providing text"""
        token_count, character_count = await self.token_source.token_count(message=self.message_panel.value)
        self.character_stats.text = "{:02}".format(character_count) + "".join(self.formatted_units[0])
        self.token_stats.text = "{:02}".format(token_count) + "".join(self.formatted_units[1])
        self.time_stats.text = "{:02}".format(0.0) + "".join(self.formatted_units[2])

    async def populate_in_types(self) -> None:
        """Builds the input types selection."""
        in_edge_names = await self.model_source.show_edges()
        self.input_types.items = in_edge_names

    async def populate_out_types(self) -> None:
        """Builds the output types selection."""
        out_edges = await self.model_source.show_edges(target=True)
        self.output_types.items = out_edges

    async def populate_model_stack(self, widget: toga.Widget = None, **kwargs) -> None:
        """Builds the model stack selection dropdown."""

        await self.model_source.clear()
        if self.input_types.value and self.output_types.value:
            models = await self.model_source.trace_models(self.input_types.value, self.output_types.value)
            self.model_stack.items = models  # [model[0][:20] for model in models if len(model[0]) > 20]
            await self.token_estimate(widget=self.message_panel)

    async def populate_task_stack(self, widget: toga.Widget = None, **kwargs) -> None:
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

    async def switch_tabs(self, widget: toga.Widget = None, **kwargs) -> None:
        """Switches between text and graph tabs.
        :param widget: The triggering widget (optional), defaults to None"""
        self.browser_panel.evaluate_javascript("location.reload();")
        self.bg = self.bg_graph if self.bg == self.bg_text else self.bg_text
        self.final_layout.style.background_color = self.bg
        self.final_layout.refresh()
        self.status_display.text += self.status_info[0]
        await self.ping_server(widget=self.status_display)

    async def ping_server(self, widget: toga.Widget, **kwargs) -> toga.Widget:
        self.browser_panel.url = self.graph_server
        try:
            request = requests.get(self.graph_server, timeout=(3, 3))
            if request is not None:
                if hasattr(request, "status_code"):
                    status = request.status_code
                if (hasattr(request, "ok") and request.ok) or (hasattr(request, "reason") and request.reason == "OK"):
                    await self.active_server()
                elif hasattr(request, "json"):
                    status = request.json()
                    if status.get("result") == "OK":
                        await self.active_server()
                else:
                    self.browser_panel.url = self.graph_disabled
                    await self.active_server(False)
            else:
                self.browser_panel.url = self.graph_disabled
                await self.active_server(False)
        except (ConnectTimeout, ConnectionError, ConnectionRefusedError, MaxRetryError, NewConnectionError, OSError):
            await self.active_server(False)
            pass
        return widget

    async def active_server(self, enabled: bool = True):
        if not enabled:
            status_info = self.status_info[1]
            self.browser_panel.url = self.graph_disabled
        else:
            status_info = self.status_info[2]
            self.browser_panel.url = self.graph_server
        for info in self.status_info:
            self.status_display.text = self.status_display.text.replace(info, "")
        self.status_display.text += status_info

    def initialize_inputs(self):
        """Initializes UI elements for input handling."""
        self.character_stats = toga.Label("{:02}".format(0) + "".join(self.formatted_units[0]), **self.fg_static)
        self.token_stats = toga.Label("{:02}".format(0) + "".join(self.formatted_units[1]), **self.fg_static)
        self.time_stats = toga.Label("{:02}".format(0.0) + "".join(self.formatted_units[2]), **self.fg_static)
        self.input_types = toga.Selection(items=[], on_change=self.populate_model_stack)
        self.output_types = toga.Selection(items=[], on_change=self.populate_model_stack)
        self.model_stack = toga.Selection(items=[], on_change=self.on_select_handler)
        self.task_stack = toga.Selection(items=[], style=Pack(align_items="end"))
        self.message_panel = toga.MultilineTextInput(placeholder="Prompt", on_change=self.token_estimate, style=Pack(flex=0.66, margin=10))
        self.browser_panel = toga.WebView(url=self.graph_server, id="Graph ")
        self.audio_panel = toga.Canvas()
        self.response_panel = toga.MultilineTextInput(readonly=True, placeholder="Response", style=Pack(flex=5), on_change=self.reset_position)

    def initialize_static(self) -> None:
        """Create the main input fields"""

        status_bar = toga.Row(
            children=[
                toga.Column(
                    children=[
                        toga.Row(
                            children=[self.input_types, toga.Label("➾"), self.output_types, self.task_stack],
                            style=Pack(align_items="end", gap=5),
                        ),
                        toga.Row(
                            children=[self.model_stack, toga.Label("↪︎")],  # , live_stats
                            style=Pack(align_items="end", text_direction="rtl", gap=5),
                        ),
                    ],
                    style=Pack(vertical_align_items="center", gap=5, justify_content="end", align_items="end"),
                ),
                toga.Row(
                    children=[
                        toga.Column(children=[self.character_stats, self.token_stats, self.time_stats]),
                        toga.Column(
                            children=[
                                toga.Button("▶︎", on_press=self.ticker, style=Pack(width=30, height=20, font_size="12")),
                                toga.Button("⧉", on_press=self.copy_reply, style=Pack(width=30, height=20, font_size=15, vertical_align_items="start")),
                            ],
                            style=Pack(gap=5),
                        ),
                        toga.Column(
                            children=[
                                toga.Button(
                                    """📎
                                _""",
                                    on_press=self.attach_file,
                                    style=Pack(width=30, height=20, font_size="10", align_items="start", justify_content="start"),
                                ),
                                toga.Button("⌫", on_press=self.empty_prompt, style=Pack(width=30, height=20, font_size="14")),
                            ],
                            style=Pack(font_size="15", gap=5),
                        ),
                    ],
                    style=Pack(vertical_align_items="center", gap=5, justify_content="start", align_items="start"),
                ),
            ],
            style=Pack(margin=10, gap=5, vertical_align_items="center", justify_content="start", align_items="start"),
        )
        self.status_log = toga.Label(f"{inspect_history()}")  # show llm history
        self.status_tab = toga.OptionItem(text="|  Connecting...", content=self.status_log, enabled=False)
        resize_area = toga.SplitContainer(
            content=[
                toga.OptionContainer(
                    content=[
                        ("Output", toga.Box(children=[self.response_panel], style=Pack(flex=1))),
                        ("Graph", self.browser_panel),
                        self.status_tab,
                    ],
                    on_select=self.switch_tabs,
                    style=Pack(background_color="#000000", flex=2),
                    id="tab_panel",
                ),
                toga.Row(
                    children=[
                        toga.Column(justify_content="start", style=Pack(flex=0.33)),
                        toga.Box(children=[self.message_panel], style=Pack(flex=1)),
                        toga.Column(style=Pack(flex=0.33, justify_content="start")),
                    ]
                ),
            ],
            direction=Direction.HORIZONTAL,
            style=Pack(flex=3),
        )

        self.final_layout = toga.Column(children=[status_bar, resize_area], style=Pack(background_color=self.bg_text, flex=1))

    def initialize_layout(self) -> None:
        """Create the layout of the application."""
        self.main_window.content = self.final_layout

    def startup(self) -> None:
        """Startup Logic. Initialize widgets and layout, then asynchronous tasks for populating datagets"""
        self.main_window = toga.MainWindow()
        self.model_source = ModelStream()
        self.task_source = TaskStream()
        self.token_source = TokenStream()

        start = toga.Command(
            self.ticker,
            text="Start",
            tooltip="Run the current available prompts.",
            shortcut=Key.MOD_1 + Key.ENTER,
            group=toga.Group.APP,
            section=-1,
        )
        attach = toga.Command.standard(
            self,
            toga.Command.OPEN,
            text="Attach File...",
            tooltip="Attach a file to the prompt.",
            shortcut=Key.MOD_1 + Key.O,
            action=self.attach_file,
            group=toga.Group.APP,
            section=0,
        )
        copy_reply = toga.Command(
            self.copy_reply,
            text="Copy Response",
            tooltip="Copy the response provided by the system",
            group=toga.Group.APP,
            section=0,
        )
        clear = toga.Command(
            self.empty_prompt,
            text="Clear Prompt",
            tooltip="Empty the user prompt field.",
            shortcut=Key.MOD_3 + Key.BACKSPACE,
            group=toga.Group.APP,
            section=1,
        )
        stop = toga.Command(
            self.halt,
            text="Stop",
            tooltip="Cancel the current sequence generation.",
            shortcut=Key.MOD_1 + Key.ESCAPE,  #
            group=toga.Group.APP,
            section=1,
        )
        self.commands.add(start, attach, copy_reply, clear, stop)

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
        self.status_display = self.status_tab
        self.bg = self.bg_graph
        self.status_text_prefix = "|  "

        asyncio.create_task(self.switch_tabs())


def main(url: str):
    """The entry point for the application."""
    app = Interface(
        formal_name="Shadowbox",
        app_id="org.darkshapes.shadowbox",
        app_name="sdbx",
        author="Darkshapes",
        home_page="https://darkshapes.org",
        description=" A generative AI instrument. ",
    )
    app.icon = toga.Icon(path="resources/anomaly_128x")
    app.main_loop()
    app.graph_server = url
