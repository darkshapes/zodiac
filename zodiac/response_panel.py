#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->


# from typing import Callable
from textual import work
from textual.widgets import TextArea


# from nnll_01 import dbug
# from nnll_11 import chat_machine


class ResponsePanel(TextArea):
    """Machine response field"""

    def on_mount(self) -> None:
        self.language = "markdown"
        self.read_only = True
        self.soft_wrap = True

    @work(group="chat")
    async def on_text_area_changed(self) -> None:
        """Send cursor to end of document and animate scroll"""
        self.move_cursor(self.document.end)
        self.scroll_cursor_visible(center=True, animate=True)
        self.scroll_end(animate=True)
