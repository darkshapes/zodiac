#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import Callable
from textual import work
from textual.screen import Screen
from textual.widgets import TextArea
from nnll_01 import dbug, nfo
from nnll_15 import RegistryEntry
from dspy import Module as dspy_Module

class ResponsePanel(TextArea):
    """Machine response field"""

    def on_mount(self) -> None:
        """Textual API, triggers when widget initializes"""
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
    async def synthesize(self, chat: dspy_Module, chat_args: dict, streaming=True) -> dict | None:
        """Generate media \n
        :param chat: Processing module for request
        :param chat_args: _description_
        :param streaming: _description_, defaults to True
        :return: Next response for the chain
        """
        from litellm import ModelResponseStream
        from dspy import Prediction
        async for chunk in chat.forward(streaming=streaming, **chat_args):
            try:
                async for c in chunk:
                    if isinstance(c, Prediction) and streaming:
                        if hasattr(c,"answer"):
                            if c.answer not in self.document.text:
                                self.insert(c.answer)
                        self.query_ancestor(Screen).ui["sl"].set_classes(["selectah"])
                    elif not streaming:
                        tx_data = chat.forward(streaming=streaming, **chat_args)
                        return tx_data
                    elif isinstance(c, ModelResponseStream):
                        self.insert(c["choices"][0]["delta"]["content"] if c["choices"][0]["delta"]["content"] is not None else " ")
            except (GeneratorExit, RuntimeError, ExceptionGroup) as error_log:
                dbug(error_log)

    @work(group="chat")
    async def pass_req(self, chat: dspy_Module, tx_data: dict, ckpt:RegistryEntry , out_type: str="text") -> dict | None:
        """Pack arguments and prepare final stage before generation\n\n
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
        :param ckpt: Model entry to fulfill request
        :param out_type: Media type for this pass, defaults to 'text'
        """
        nfo(ckpt)
        last_hop = True
        chat_args = {"tx_data":tx_data, "model":ckpt.model, "library":ckpt.library,}
        if out_type != "text" or not last_hop:
            tx_data = self.synthesize(chat=chat, chat_args=chat_args, streaming=False)
            return tx_data
        self.synthesize(chat=chat, chat_args=chat_args, streaming=True)
        return None
