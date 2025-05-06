#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-outside-toplevel

import networkx as nx
from textual import on, events, work
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Select
from textual.widgets._select import SelectOverlay  # , SelectCurrent,

from nnll_01 import dbug, debug_monitor


class Selectah(Select):
    mode_in: reactive[str] = reactive("text")
    mode_out: reactive[str] = reactive("text")
    hover = True

    @on(Select.Changed)
    async def on_changed(self) -> None:  # event: Select.Changed) -> None:
        """Rearrange models"""
        from_fold = self.query_ancestor(Screen)
        if self.value != Select.BLANK and self.value != "No Models.":
            try:
                from_fold.int_proc.edit_weight(selection=self.value, mode_in=self.mode_in, mode_out=self.mode_out)
            except ValueError as error_log:
                dbug(error_log)
            self.expanded = False
            from_fold.next_intent()

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
