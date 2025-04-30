#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Selection Function"""

from huggingface_hub import repo_type_and_id_from_hf_id
from textual import events
from textual.widgets import DataTable
from textual.screen import Screen
from textual.reactive import reactive

from nnll_01 import debug_monitor, nfo  # dbug,


class Carousel(DataTable):
    """Revolving text-line component based on default DataTable widget class"""

    nx_graph: dict
    content_cell: reactive[int] = reactive(0)

    up = "[@click='scroll_button(1)']▲[/]"
    dwn = "[@click='scroll_button()']▼[/]"
    current_cell = "text"
    current_row = 0
    y_coord = 1
    scroll_counter = 10
    scroll_max = 10

    def on_mount(self) -> None:
        self.show_header = False
        self.cursor_type = "cell"

    @debug_monitor
    async def repop(self) -> None:
        """Update the values for"""
        from_query = self.query_ancestor(Screen)
        if from_query.id == "input_tag":
            from_query.ui["ps"].current = from_query.input_map[self.current_cell]
        from_query.ready_tx(io_only=True)
        from_query.walk_intent()
        from_query.ui["sl"].mode_in = from_query.ui["it"].current_cell
        from_query.ui["sl"].mode_out = from_query.ui["ot"].current_cell
        from_query.ui["sl"].prompt = next(iter(from_query.int_proc.models))[0]

    @debug_monitor
    async def emulate_scroll(self, direction: int = 1) -> str:
        """Trigger datatable cursor movement using fractional sensitivity
        :param direction: Positive integer for up, negative integer for down
        :return: The datata in the table *row*"""

        self.scroll_counter += abs(direction)
        if self.scroll_counter < self.scroll_max:
            self.current_cell = self.get_cell_at((self.current_row, 1))
        else:
            self.current_row = max(0, min(self.row_count - 1, self.current_row + direction))
            self.move_cursor(row=self.current_row, column=1)
            self.scroll_counter = 0
            self.current_cell = self.get_cell_at((self.current_row, 1))
            await self.repop()

    @debug_monitor
    async def action_scroll_button(self, up: bool = False) -> None:
        """Manually trigger scrolling and panel switching
        :param up: Scroll direction, defaults to False"""

        if not up:
            self.scroll_counter = self.scroll_max - 1  # we only scroll + numbers
            await self.emulate_scroll(1)
        else:
            self.scroll_counter = self.scroll_max - 1
            await self.emulate_scroll(-1)

    @debug_monitor
    async def _on_key(self, event: events.Key) -> None:
        """Textual API event trigger, Translate arrow events into datatable cursor movement"""
        if event.key == "up":
            event.prevent_default()
            self.scroll_counter += self.scroll_max / 2  # we only scroll + numbers
            await self.emulate_scroll(-1)

        elif event.key == "down":
            event.prevent_default()
            self.scroll_counter += self.scroll_max / 2  # we only scroll + numbers
            await self.emulate_scroll(1)

    @debug_monitor
    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Textual API event trigger,Translate scroll events into datatable cursor movement
        Trigger scroll at 1/10th intensity when menu has focus
        :param event: Event data for the trigger"""

        await self.emulate_scroll(-1)

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        """Textual API event trigger, Translate scroll events into datatable cursor movement
        Trigger scroll at 1/10th intensity when menu has focus
        :param event: Event data for the trigger"""

        await self.emulate_scroll(1)
