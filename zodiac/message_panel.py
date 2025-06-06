# # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
# # <!-- // /*  d a r k s h a p e s */ -->
from textual import work
from textual.widgets import TextArea


# from nnll.monitor.file import debug_monitor


class MessagePanel(TextArea):
    """User entry field"""

    def on_mount(self):
        self.cursor_blink = True
        self.focus()

    @work(exclusive=True)
    async def erase_message(self):
        """Empty panel contents"""
        self.clear()
