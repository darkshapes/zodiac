#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# from typing import Callable
from textual import work
from textual.screen import Screen
from textual.widgets import TextArea
from nnll_01 import nfo  # dbug,
from nnll_15 import RegistryEntry
from dspy import Signature, Module as dspy_Module
from typing import Callable


class ResponsePanel(TextArea):
    """Machine response field"""

    def on_mount(self) -> None:
        """Textual API, triggers when widget initializes"""
        self.language = "markdown"
        self.read_only = True
        self.soft_wrap = True

    @work(exclusive=True)
    async def on_text_area_changed(self) -> None:
        """Send cursor to end of document and animate scroll"""
        self.move_cursor(self.document.end)
        self.scroll_cursor_visible(center=True, animate=True)
        self.scroll_end(animate=True)

    @work(group="chat", exclusive=True)
    async def synthesize(self, chat: dspy_Module, mode_out: str, tx_data: dict) -> dict | None:
        """Generate media \n
        :param chat: Processing module for request
        :param chat_args: _description_
        :param streaming: _description_, defaults to True
        :return: Next response for the chain
        ```
        name    [ medium : data ]
                ,-text     string # json?
                ⏐-image    array
        tx_data-⏐-speech   array
                ⏐-video    array
                '-music    array
        ```
        :param chat: Processing module for request
        :param tx_data: Prompt request
        :param out_type: Media type for this pass, defaults to 'text'
        """

        from litellm import ModelResponseStream
        from dspy import Prediction

        streaming = mode_out == "text"
        if not streaming:
            chat.forward(tx_data, out_type=mode_out)
        else:
            async for chunk in chat.forward(tx_data, out_type=mode_out):
                async for c in chunk:
                    if isinstance(c, Prediction) and streaming:
                        if hasattr(c, "answer"):
                            if c.answer not in self.text:
                                self.insert(c.answer)
                        self.query_ancestor(Screen).ui["sl"].set_classes(["selectah"])
                    elif isinstance(c, ModelResponseStream):
                        self.insert(c["choices"][0]["delta"]["content"] if c["choices"][0]["delta"]["content"] is not None else " ")
