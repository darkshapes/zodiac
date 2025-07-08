# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

from typing import Any, Dict
from array import array
from dspy import Module as dspy_Module


async def synthesize(chat: dspy_Module, tx_data: Dict[str, array]) -> Any:
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

    async for chunk in chat(tx_data=tx_data):
        try:
            async for c in chunk:
                if isinstance(c, Prediction):
                    if hasattr(c, "answer"):
                        yield ""
                elif isinstance(c, ModelResponseStream):
                    yield c["choices"][0]["delta"]["content"] if c["choices"][0]["delta"]["content"] else str("")
        except (AdapterParseError, TypeError) as error_log:
            print(f"LM parse error {error_log}")
