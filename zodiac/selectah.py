#  # # <!-- // /*  SPDX-License-Identifier: blessing) */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-outside-toplevel

import networkx as nx
from textual import on, events, work
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Select
from textual.widgets._select import SelectCurrent, SelectOverlay

from nnll_01 import debug_message as dbug, debug_monitor, info_message as nfo


class Selectah(Select):
    models: reactive[list[tuple[str, str]]] = reactive([("", "")])
    graph: nx.Graph = None
    mode_in: str = "text"
    mode_out: str = "text"
    focused = True
    hover = True

    def on_mount(self) -> None:
        # self.options = self.graph.models
        self.graph = self.query_ancestor(Screen).int_proc
        # self.prompt = os.path.basename(next(iter(self.graph.models))[0])

    @on(Select.Changed)
    async def on_changed(self) -> None:  # event: Select.Changed) -> None:
        """Rearrange models"""
        self.graph = self.query_ancestor(Screen).int_proc
        try:
            assert self.query_one(SelectCurrent).has_value
            assert self.graph.models is not None
        except AssertionError as error_log:
            dbug(error_log)
        else:
            try:
                self.graph.edit_weight(selection=self.value, mode_in=self.mode_in, mode_out=self.mode_out)
            except ValueError as error_log:
                dbug(error_log)
            else:
                self.set_options(self.graph.models)
                self.prompt = next(iter(self.graph.models))[0]
        self.expanded = False

    @debug_monitor
    @work(exclusive=True)
    @on(events.Enter)
    async def on_enter(self, event: events.Enter) -> None:
        """Force terminal mouse event monitoring"""
        if event.node == SelectOverlay or event.node == self:
            self.hover = True

    @debug_monitor
    @work(exclusive=True)
    @on(events.Leave)
    async def on_leave(self, event: events.Leave) -> None:
        """Force terminal mouse event monitoring"""
        if event.node == SelectOverlay or event.node == self:
            self.hover = True

    @work(exclusive=True)
    @on(events.Focus)
    async def on_focus(self, event: events.Focus) -> None:
        """Expand panel immediately when clicked in terminal"""
        if SelectOverlay.has_focus or self.has_focus:
            self.focused = True
            self.graph = self.query_ancestor(Screen).int_proc
            if self.graph is not None and hasattr(self.graph, "models") and self.graph.models is not None:
                self.set_options(self.graph.models)
            else:
                self.focused = False

    @work(exclusive=True)
    @on(events.MouseDown)
    async def on_mouse_down(self, event: events.MouseDown) -> None:
        """Expand panel immediately when clicked in terminal"""
        if self.hover and not self.expanded:
            self.expanded = True
        elif (SelectOverlay.has_focus or self.has_focus) and self.expanded:
            self.blur()

    @work(exclusive=True)
    @on(events.MouseUp)
    async def on_mouse_up(self, event: events.MouseUp) -> None:
        """Expand panel immediately when clicked in terminal"""
        if self.hover and self.focus and self.expanded:
            self.expanded = False
        elif self.hover and not self.expanded:
            self.expanded = True


#    if self.expanded is False:
#                 self.expanded = True

# @on(SelectOverlay.blur)
# def on_select_overlay_blur(self, event: events.Blur) -> None:
#     from rich.text import Text

#     nfo(event.control.id, "blah blah blah")
#     # if event.control == SelectOverlay:
#     self.ui["sl"].prompt = next(iter(self.int_proc.models))[0]
#     label = self.ui["sl"].query_one("#label", Static)
#     try:
#         assert label.renderable == next(iter(self.int_proc.models))[0]
#     except AssertionError as error_log:
#         dbug(error_log)
#         self.ui["sl"].prompt = next(iter(self.int_proc.models))[0]

# @on(OptionList.OptionSelected)
# def on_select_overlay_option_selected(self, event: OptionList.OptionSelected) -> None:
#     """Textual API event, refresh pathing, Switch checkpoint assignments"""
#     nfo(" test write")
#     overlay = self.ui["sl"].query_one(SelectOverlay)
#     mode_in = self.ui["it"].get_cell_at((self.ui["it"].current_row, 1))
#     mode_out = self.ui["ot"].get_cell_at((self.ui["ot"].current_row, 1))
#     if self.ui["sl"].selection == Select.BLANK or self.ui["sl"].selection is None:
#         selection = next(iter(self.int_proc.models))[1]
#     else:
#         selection = self.ui["sl"].selection
#     self.int_proc.edit_weight(selection=selection, mode_in=mode_in, mode_out=mode_out)
#     self.ready_tx()
#     self.walk_intent()
#     overlay.recompose()
#     # self.ui["sl"].set_options(self.int_proc.models)

# self.ready_tx()
# if self.int_proc.has_graph() and self.int_proc.has_path():
#     self.walk_intent()
# if self.int_proc.has_ckpt():

# self.ui["sl"].set_options(options=self.int_proc.models)
# nfo(self.int_proc.has_ckpt())
# self.ui["sl"].expanded = False

# @work(exclusive=True)
