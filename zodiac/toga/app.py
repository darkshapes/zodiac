#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import Callable, Optional

import asyncio
import toga
from toga.constants import Direction
from toga.style import Pack
from zodiac.streams.model_stream import ModelStream
from zodiac.streams.task_stream import TaskStream


class Interface(toga.App):
    units = [("characters", "/", 00000), ("tokens", "/", 00000), ("seconds", "″", 00)]

    async def on_select_handler(self, widget, **kwargs):
        """React to a widget choice.
        :param widget: The widget that triggered the event."""
        selection = widget.value
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
        self.counter = toga.Row(style=Pack(height=20, flex=1, align_items="center", justify_content="center", gap=5, margin=10))

        for unit in self.units:
            setattr(self, unit[0], toga.Label(f"{unit[2]}"))
            setattr(self, unit[0] + "_symbol", toga.Label(unit[1]))
            self.counter.children.extend([getattr(self, unit[0]), getattr(self, unit[0] + "_symbol")])
        self.path_slider = toga.Slider(min=0, tick_count=2, on_change=self.traverse, style=Pack(flex=1, margin=10))
        self.counter_slider = toga.Column(children=[self.counter, self.path_slider], style=Pack(flex=1))
        self.in_types = toga.Selection(items=[], style=Pack(flex=0.25), on_change=self.populate_model_stack)
        self.out_types = toga.Selection(items=[], style=Pack(flex=0.25), on_change=self.populate_model_stack)

        self.model_stack = toga.Selection(items=[], on_change=self.on_select_handler, style=Pack(flex=0.5))
        self.task_stack = toga.Selection(items=[], style=Pack(flex=1))
        self.parameter_stack = toga.Column(children=[self.model_stack, self.task_stack], align_items="end", text_direction="rtl", style=Pack(gap=15))
        intent_fields = toga.Column(children=[self.in_types, self.out_types], align_items="start", text_direction="ltr", style=Pack(gap=15))
        model_fields = toga.Row(children=[intent_fields, self.counter_slider, self.parameter_stack], vertical_align_items="center")
        status_bar = toga.Box(children=[self.status], style=Pack(flex=1, height=15))

        self.message_panel = toga.MultilineTextInput(value="Message", style=Pack(flex=1))
        combined_top = toga.Column(children=[self.message_panel, model_fields, status_bar])

        self.response_panel = toga.MultilineTextInput(readonly=True, value="")
        self.center_layout = toga.SplitContainer(content=[combined_top, self.response_panel], direction=Direction.HORIZONTAL, flex=20, margin=0)

    def initialize_layout(self):
        """Create the layout of the application."""
        # outer_box = toga.Column(children=[self.center_layout, status_bar], style=Pack(flex=1, margin=10))

        # left_buffer = toga.Column(children=[toga.Label("")], justify_content="start", style=Pack(flex=0.15))
        # right_buffer = toga.Column(children=[toga.Label("")], justify_content="end", style=Pack(flex=0.15))

        # center_column = toga.Row(children=[left_buffer, self.center_layout, right_buffer], style=Pack(flex=5))
        self.main_window.content = self.center_layout

    def startup(self):
        """Startup Logic. Initialize widgets and layout, then asynchronous tasks for populating datagets"""
        self.main_window = toga.MainWindow()

        self.initialize_widgets()
        self.initialize_layout()

        asyncio.create_task(self.model_graph())
        asyncio.create_task(self.populate_in_types())
        asyncio.create_task(self.populate_out_types())
        asyncio.create_task(self.populate_model_stack())
        asyncio.create_task(self.populate_task_stack())

        self.main_window.show()


def main():
    """The entry point for the application."""
    app = Interface("Shadowbox", "org.beeware.toga.examples.table_source")
    app.main_loop()
