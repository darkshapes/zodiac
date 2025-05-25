#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# from typing import Callable
from textual import work
from textual.screen import Screen
from textual.widgets import TextArea
from nnll_01 import nfo  # dbug,
from nnll_15 import RegistryEntry
from dspy import Signature, Module as dspy_Module


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
            async for c in chunk:
                if isinstance(c, Prediction) and streaming:
                    if hasattr(c, "answer"):
                        if c.answer not in self.text:
                            self.insert(c.answer)
                    self.query_ancestor(Screen).ui["sl"].set_classes(["selectah"])
                elif isinstance(c, ModelResponseStream):
                    self.insert(c["choices"][0]["delta"]["content"] if c["choices"][0]["delta"]["content"] is not None else " ")

    @work(group="chat", exclusive=True)
    async def pass_req(self, sig: Signature, tx_data: dict, ckpt: RegistryEntry, out_type: str = "text", last_hop=True) -> dict | None:
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
        from nnll_11 import ChatMachineWithMemory

        chat_args = {"tx_data": tx_data, "model": ckpt.model, "library": ckpt.library}
        stream = out_type == "text" and last_hop
        nfo(f"stream_type: {stream} for {ckpt.model} in {ckpt.library}")
        chat = ChatMachineWithMemory(sig=sig, max_workers=8, stream=stream)  # and this
        self.notify("Processing request...", severity="information")
        if not stream:
            chat.forward_hub(out_type=out_type, **chat_args)
        else:
            self.synthesize(chat=chat, chat_args=chat_args, streaming=stream)

