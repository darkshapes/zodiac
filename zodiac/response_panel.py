#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import Callable
from textual import work
from textual.screen import Screen
from textual.widgets import TextArea
from nnll_01 import dbug, nfo


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

    @work(group="chat")
    async def scribe(self, chat, chat_args, streaming=True):
        from litellm import ModelResponseStream
        from dspy import Prediction
        async for chunk in chat.forward(streaming=streaming, **chat_args):
            try:
                async for c in chunk:
                    if isinstance(c, Prediction):
                        if streaming:
                            self.query_ancestor(Screen).ui["sl"].set_classes(["selectah"])
                            if hasattr(c,"answer"):
                                self.insert(c.answer)
                    elif not streaming:
                        self.tx_data = chat.forward(streaming=streaming, **chat_args)
                    elif isinstance(c, ModelResponseStream):
                        self.insert(c["choices"][0]["delta"]["content"] if c["choices"][0]["delta"]["content"] is not None else " ")
            except (GeneratorExit, RuntimeError, ExceptionGroup) as error_log:
                dbug(error_log)

    @work(group="chat")
    async def synthesis(self, chat, tx_data, ckpt, output:str="text"):
        nfo(ckpt)
        last_hop = True
        chat_args = {"tx_data":tx_data, "model":ckpt.model, "library":ckpt.library,}
        if output != "text" or not last_hop:
            self.scribe(chat_args, streaming=False)
        self.scribe(chat, chat_args, streaming=True) if last_hop else self.synthesis()

