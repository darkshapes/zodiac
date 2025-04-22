#  # # <!-- // /*  SPDX-License-Identifier: blessing */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Selection Function"""

from textual.widgets import DataTable
from textual.screen import Screen
from textual.reactive import reactive

from nnll_01 import debug_monitor, info_message as nfo  # debug_message as dbug,


class Carousel(DataTable):
    """Revolving text-line component based on default DataTable widget class"""

    nx_graph: dict
    content_cell: reactive[int] = reactive(0)

    up = "[@click='scroll_button(1)']▲[/]"
    dwn = "[@click='scroll_button']▼[/]"
    current_cell = "text"
    current_row = 0
    y_coord = 1
    scroll_counter = 10

    def on_mount(self) -> None:
        self.show_header = False
        self.cursor_type = "cell"

    @debug_monitor
    def emulate_scroll_down(self, interval: int = 1) -> str:
        """Trigger datatable cursor movement using fractional sensitivity
        :param ceiling: Total entry count of the table *column*
        :return: The datata in the table *row*
        """

        if (self.row_count - 1) >= (self.current_row + interval):
            if self.y_coord < self.scroll_counter:
                self.y_coord += interval
            else:
                self.y_coord = interval
                self.current_row += interval
                self.move_cursor(row=self.current_row, column=1)
        self.current_cell = self.get_cell_at((self.current_row, 1))
        return self.current_cell

    @debug_monitor
    def emulate_scroll_up(self, interval: int = 1) -> str:
        """Trigger datatable cursor movement using fractional sensitivity
        :param ceiling: Total entry count of the table *column*
        :return: The datata in the table *row*
        """

        if 0 <= self.current_row - interval:
            if self.y_coord >= 1:
                self.y_coord -= interval
            else:
                self.y_coord = self.scroll_counter
                self.current_row -= interval
                self.move_cursor(row=self.current_row, column=1)
        self.current_cell = self.get_cell_at((self.current_row, 1))
        return self.current_cell

    @debug_monitor
    def action_scroll_button(self, up: bool = False) -> None:
        """Manually trigger scrolling and panel switching
        :param up: Scroll direction, defaults to False
        """
        if up:
            self.current_cell = self.emulate_scroll_up(interval=self.y_coord + 1)
            if self.id == "input_tag":
                self.query_ancestor(Screen).foldr["ps"].current = self.query_ancestor(Screen).input_map[self.current_cell]
                self.query_ancestor(Screen).ready_tx(io_only=True)
        else:
            self.current_cell = self.emulate_scroll_down(interval=self.scroll_counter - self.y_coord - 1)
            if self.id == "input_tag":
                self.query_ancestor(Screen).foldr["ps"].current = self.query_ancestor(Screen).input_map[self.current_cell]
                self.query_ancestor(Screen).ready_tx(io_only=True)
