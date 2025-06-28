from typing import Any, Callable, List
import networkx as nx
import asyncio
import toga
from toga.constants import COLUMN, ROW
from toga.sources import Source
from toga.style import Pack


class ModelSource(Source):
    async def build_graph(self):
        from zodiac.graph import IntentProcessor

        self.int_proc = IntentProcessor()
        self.int_proc.calc_graph()

    async def show_edges(self, out: bool = False):
        if self.int_proc.has_graph():
            self.edge_pairs = self.int_proc.intent_graph.edges
            self.edges_in = {edge[0] for edge in self.edge_pairs.items()}
            return self.edges_in


class ModelList(toga.App):
    def on_select_handler(self, widget, **kwargs):
        row = widget.value
        self.label.text = f"You selected row: {row}" if row is not None else "No row selected"

    async def launch_graph(self):
        self.model_data = ModelSource()
        await self.model_data.build_graph()

    async def build_in_types(self):
        in_edge_names = await self.model_data.show_edges()

        self.in_types = toga.Selection(
            style=Pack(flex=1),
            items=set(in_edge_names),
            on_change=self.on_select_handler,
        )

    async def build_out_types(self):
        out_edges = await self.model_data.show_edges(out=True)
        self.out_types = toga.Selection(
            style=Pack(flex=1),
            items=out_edges,
            on_change=self.on_select_handler,
        )

    async def build_layout(self):
        tablebox = toga.Box(children=[self.in_types, self.out_types], style=Pack(flex=1))
        self.outer_box = toga.Box(
            children=[tablebox, self.label],
            style=Pack(
                flex=1,
                direction=COLUMN,
                margin=10,
            ),
        )
        self.main_window.content = self.outer_box

    def startup(self):
        self.label = toga.Label("Ready.")
        asyncio.create_task(self.launch_graph())
        asyncio.create_task(self.build_in_types())
        asyncio.create_task(self.build_out_types())
        asyncio.create_task(self.build_layout())

        self.main_window = toga.MainWindow()

        self.main_window.show()


def main():
    app = ModelList("Model Selection", "org.beeware.toga.examples.table_source").main_loop()


#     def lauout(self) -> Any:
#
#         self.blank = ListSource(accessors=["model", "path"])
#         self.model_data = ValueSource(self.int_proc.models, add_listener(change=self.update_selections))
#         self.models = ListSource(accessors=["model", "path"])
#         self.selectah = toga.Selection(
#             items=self.blank,
#             align_items="end",
#         )

#         message_box = toga.MultilineTextInput(flex=1)
#         message_box.value = "Message"

#         middle_label = toga.Label("Tokens/Models", text_direction="ltr")
#         middle_bar = toga.Column(flex=0, align_items="end", text_direction="rtl")
#         middle_bar.add(middle_label, self.selectah)

#         bottom_bar = toga.SplitContainer(content=[message_box, middle_bar], direction=Direction.HORIZONTAL, flex=1)

#         response_box = toga.MultilineTextInput(readonly=True, flex=1)
#         response_box.value = "Response"
#         box_c = toga.SplitContainer(content=[bottom_bar, response_box], direction=Direction.HORIZONTAL, flex=20)

#         left = toga.Label("left")
#         box_l = toga.Column(align_items="start", width=148)
#         box_l.add(left)

#         right = toga.Label("right")
#         box_r = toga.Column(align_items="end", width=148)
#         box_r.add(right)

#         whole_screen = toga.Row()
#         whole_screen.add(box_l, box_c, box_r)
