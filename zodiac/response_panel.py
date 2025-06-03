#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# from typing import Callable
from textual import work
from textual.screen import Screen
from textual.widgets import TextArea
from nnll.monitor.file import nfo  # dbug
from dspy import Module as dspy_Module


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
    async def synthesize(self, chat: dspy_Module, tx_data: dict, mode_out: str) -> dict | None:
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
        from nnll.metadata import save_generation as disk

        nfo("sync")
        nfo(f"chat registry entries : {chat.reg_entries}")
        streaming = mode_out == "text"
        if not streaming:
            metadata = {}
            prompt = tx_data["text"]
            content = chat.pipe(prompt=prompt, **chat.pipe_kwargs).images[0]
            gen_data = disk.add_to_metadata(pipe=chat.pipe, model=chat.reg_entries.model, prompt=[prompt], kwargs=chat.pipe_kwargs)
            nfo(f"content = {content}")
            metadata.update(gen_data.get("parameters"))
            nfo(f"content type output {content}, {type(content)}")
            disk.write_to_disk(content, metadata)
            chat.destroy()
        else:  # history=history)
            async for chunk in chat.forward(tx_data=tx_data, mode_out=mode_out):
                async for c in chunk:
                    if isinstance(c, Prediction) and streaming:
                        if hasattr(c, "answer"):
                            if c.answer not in self.text:
                                self.insert(c.answer)
                        self.query_ancestor(Screen).ui["sl"].set_classes(["selectah"])
                    elif isinstance(c, ModelResponseStream):
                        self.insert(c["choices"][0]["delta"]["content"] if c["choices"][0]["delta"]["content"] is not None else " ")
