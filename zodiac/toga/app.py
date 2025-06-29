from typing import Any, Callable, List
import networkx as nx
import asyncio
import toga
from toga.constants import COLUMN, ROW, Direction
from toga.sources import Source
from toga.style import Pack


class ModelSource(Source):
    async def model_graph(self) -> None:
        """Build an intent graph from models using the IntentProcessor class"""
        from zodiac.graph import IntentProcessor

        self._graph = {}
        # self._graph.add_listener(self)
        self._graph = IntentProcessor()
        self._graph.calc_graph()

    async def show_edges(self, target: bool = False) -> List[str]:
        """Retrieve and sort edges from the intent graph.\n
        :param target: If True, sorts based on the second element of each edge pair; defaults to False.
        :return: A sorted list of unique elements from the edge pairs."""

        if self._graph.has_graph():
            edge_pairs = list(self._graph.intent_graph.edges)
            pair = 0 if not target else 1
            seen = []
            for edge in edge_pairs:
                if edge[pair] not in seen:
                    seen.append(edge[pair])
            seen.sort(key=len)
            return seen

    async def ready_tx(self, mode_in: str, mode_out: str):
        from nnll.monitor.file import dbuq

        self._graph.set_path(mode_in=mode_in, mode_out=mode_out)
        self._graph.set_registry_entries()
        dbuq(f"triggered recalculation : {self._graph.coord_path} {self._graph.registry_entries}")
        self._models = self._graph.models
        return self._models

    def __len__(self):
        return len(list(self._models()))

    def __getitem__(self, index):
        return self._models()[index]

    def index(self, entry):
        return self._models().index(entry)

    async def clear(self):
        self._models = []
        self.notify("clear")

        # if not io_only:
        #     self.tx_data = {
        #         "text": self.ui["mp"].text,
        #         "speech": self.ui["vm"].snd.audio_stream,
        # "attachment": self.message_panel.file # drag and drop from external window
        # "image": self.image_panel.image #  active video feed / screenshot / import file
        # }


class ModelList(toga.App):
    UNIT1 = "/ "  # Display Bar Units
    UNIT2 = "/ "
    UNIT3 = "″"
    unit_labels = [{"chr": UNIT1, "tkn": UNIT2, "sec": UNIT3}]

    async def on_select_handler(self, widget, **kwargs):
        """React to a widget choice.
        :param widget: The widget that triggered the event."""
        row = widget.value
        self.status.text = f"In = {self.in_types.value.title()} /  Out = {self.out_types.value.title()}" if row is not None else "Select conversion."
        await self.build_model_stack()

    async def model_graph(self):
        """Builds the model graph."""
        self.model_data = ModelSource()
        await self.model_data.model_graph()

    async def build_in_types(self):
        """Builds the input types selection."""
        in_edge_names = await self.model_data.show_edges()
        self.in_types = toga.Selection(
            style=Pack(flex=0.25),
            items=in_edge_names,
            on_change=self.build_model_stack,
        )

    async def build_out_types(self):
        """Builds the output types selection."""
        out_edges = await self.model_data.show_edges(target=True)
        self.out_types = toga.Selection(
            style=Pack(flex=0.25),
            items=out_edges,
            on_change=self.build_model_stack,
        )

    async def build_model_stack(self, widget):
        """Builds the model stack selection dropdown."""
        await self.model_data.clear()
        if self.in_types.value and self.out_types.value:
            self.models = await self.model_data.ready_tx(self.in_types.value, self.out_types.value)
            self.model_stack.items = self.models

    async def build_fields(self):
        """Create the main input fields"""
        self.model_stack = toga.Selection(items=self.models, on_change=self.on_select_handler, style=Pack(flex=1))
        self.counter = toga.Table(id="counters", accessors={"chr", "tkn", "sec"}, data=self.unit_labels, text_direction="ltr", style=Pack(height=30, margin_right=0, margin_left=0, flex=1))
        intent_fields = toga.Column(children=[self.in_types, self.out_types], align_items="start", text_direction="ltr")  # style=Pack(flex=0.5)
        model_fields = toga.Row(children=[intent_fields, self.counter, self.model_stack], vertical_align_items="center")
        self.message_panel = toga.MultilineTextInput(flex=1, value="Message", style=Pack(flex=1))
        combined_top = toga.SplitContainer(content=[self.message_panel, model_fields], direction=Direction.HORIZONTAL)

        self.response_panel = toga.MultilineTextInput(readonly=True, flex=1, value="")
        self.center_layout = toga.SplitContainer(
            content=[combined_top, self.response_panel],
            direction=Direction.HORIZONTAL,
            style=Pack(
                flex=10,
                direction=COLUMN,
                margin=0,
            ),
        )

    async def build_layout(self):
        """Create the layout of the application."""
        self.status = toga.Label("Ready.")
        status_bar = toga.Box(children=[self.status], style=Pack(flex=1))
        outer_box = toga.Column(
            children=[self.center_layout, status_bar],
            style=Pack(
                flex=1,
                margin=10,
            ),
        )
        left_buffer = toga.Column(children=[toga.Label("")], justify_content="start", width=148)
        right_buffer = toga.Column(children=[toga.Label("")], justify_content="end", width=148)
        center_column = toga.Row(children=[left_buffer, outer_box, right_buffer], style=Pack(flex=5))

        self.main_window.content = center_column

        # self.whole_screen = toga.Box(children=[self.input_controls])
        # self.main_window.content = self.whole_screen

    def startup(self):
        """Initializes the application."""
        self.main_window = toga.MainWindow()
        asyncio.create_task(self.model_graph())
        asyncio.create_task(self.build_in_types())
        asyncio.create_task(self.build_out_types())
        # asyncio.create_task(self.build_stack_controls())
        asyncio.create_task(self.build_model_stack(self))
        asyncio.create_task(self.build_fields())
        asyncio.create_task(self.build_layout())

        self.main_window.show()


def main():
    """The entry point for the application."""
    app = ModelList("Model Selection", "org.beeware.toga.examples.table_source")
    app.main_loop()
