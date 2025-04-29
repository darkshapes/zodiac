# # <!-- // /*  SPDX-License-Identifier: LAL-1.3) */ -->
# # <!-- // /*  d a r k s h a p e s */ -->
from textual import work
from textual.widgets import TextArea


# from nnll_01 import debug_monitor


class MessagePanel(TextArea):
    """User entry field"""

    def on_mount(self):
        self.cursor_blink = True

    @work(exclusive=True)
    async def erase_message(self):
        """Empty panel contents"""
        self.clear()
