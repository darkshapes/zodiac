#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Selection Function"""

from textual import events, work
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
    current_cell: reactive[str] = reactive("text")
    scroll_counter = 10
    scroll_max = 10

    def on_mount(self) -> None:
        self.show_header = False
        self.cursor_type = "cell"
        self.cursor_coordinate = (0, 1)

    @debug_monitor
    async def emulate_scroll(self, direction: int = 1) -> str:
        """Trigger datatable cursor movement by fraction of normal sensitivity\n
        :param direction: Positive integer for up, negative integer for down
        :return: The datata in the table *row*

        #### ASSUMING\n
        A: User has the choice to select TAG OR select direction ARROW
        B: We do not know without an operation what the content of the selection is
        Therefore: We cannot use textual's `coordinate_to_cell_key` without incuring computational cost

        We are also assuming there is no way for user to change BOTH INPUT and OUTPUT tags at the same time
        """
        self.scroll_counter += abs(direction)
        if self.scroll_counter < self.scroll_max:
            self.current_cell = self.get_cell_at((self.cursor_row, 1))
        else:
            current_row = max(0, min(self.row_count - 1, self.cursor_row + direction))
            self.move_cursor(row=current_row, column=1)
            self.scroll_counter = 0
            self.current_cell = self.get_cell_at((self.cursor_row, 1))
        if self.id == "input_tag":
            self.query_ancestor(Screen).mode_in = self.current_cell
        elif self.id == "output_tag":
            self.query_ancestor(Screen).mode_out = self.current_cell

    @debug_monitor
    async def action_scroll_button(self, up: bool = False) -> None:
        """Manually trigger scrolling and panel switching\n
        :param up: Scroll direction, defaults to False
        """
        if not up:
            self.scroll_counter = self.scroll_max - 1  # we only scroll + numbers
            await self.emulate_scroll(1)
        else:
            self.scroll_counter = self.scroll_max - 1
            await self.emulate_scroll(-1)

    @debug_monitor
    async def _on_key(self, event: events.Key) -> None:
        """Textual API event trigger, Translate arrow events into datatable cursor movement"""
        if event.key == "up":  # shrinking towards zero
            event.prevent_default()
            self.scroll_counter += self.scroll_max / 2
            await self.emulate_scroll(-1)

        elif event.key == "down":  # gromwing from zero
            event.prevent_default()
            self.scroll_counter += self.scroll_max / 2  # positive integer indicates scroll is ready
            await self.emulate_scroll(1)

    @debug_monitor
    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Textual API event trigger,Translate scroll events into datatable cursor movement
        Trigger scroll at 1/10th intensity when mxenu has focus
        :param event: Event data for the trigger
        """
        await self.emulate_scroll(-1)

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        """Textual API event trigger, Translate scroll events into datatable cursor movement
        Trigger scroll at 1/10th intensity when menu has focus
        :param event: Event data for the trigger
        """
        await self.emulate_scroll(1)

    @debug_monitor
    async def skip_to(self, name="text") -> None:
        """Jump current tag to an index # and change panel context if required\n
        :param id_name: Name of the panel to switch to
        :param top: Whether or not the request comes from in or out tag
        """
        coord = [x for x in range(self.row_count) if self.get_cell_at((1, x)) == name]
        nfo(coord)
        self.scroll_to(x=1, y=coord, force=True, immediate=True, on_complete=self.refresh)
