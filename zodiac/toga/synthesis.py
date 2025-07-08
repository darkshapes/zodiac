# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

from typing import Any, Dict
from array import array
from dspy import Module as dspy_Module


async def synthesize(chat: dspy_Module, tx_data: Dict[str, array], mode_out: str) -> Any:
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
    ```import pyperclip
    :param chat: Processing module for request
    :param tx_data: Prompt request
    :param out_type: Media type for this pass, defaults to 'text'
    """

    from litellm import ModelResponseStream
    from dspy import Prediction
    from dspy.utils.exceptions import AdapterParseError
    from nnll.metadata import save_generation as disk

    # nfo("sync")
    # nfo(f"chat registry entries : {chat.registry_entries}")
    streaming = mode_out == "text"
    if not streaming:
        metadata = {}
        prompt = tx_data["text"]
        content = chat.pipe(prompt=prompt, **chat.pipe_kwargs).images[0]
        gen_data = disk.add_to_metadata(pipe=chat.pipe, model=chat.registry_entries.model, prompt=[prompt], kwargs=chat.pipe_kwargs)
        # nfo(f"content = {content}")
        metadata.update(gen_data.get("parameters"))
        # nfo(f"content type output {content}, {type(content)}")
        disk.write_to_disk(content, metadata)
        # chat.destroy()
    else:  # history=history)
        async for chunk in chat(tx_data=tx_data, mode_out=mode_out):
            try:
                async for c in chunk:
                    if isinstance(c, Prediction) and streaming:
                        if hasattr(c, "answer"):
                            yield False
                    elif isinstance(c, ModelResponseStream):
                        yield c["choices"][0]["delta"]["content"] if c["choices"][0]["delta"]["content"] else str("")
            except (AdapterParseError, TypeError) as error_log:
                print(f"LM parse error {error_log}")
