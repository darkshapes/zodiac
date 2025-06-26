#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-error

from typing import Callable


async def tk_count(model: str, message: str) -> Callable:
    """Pass message to model routine
    :param model: Path to model
    :param message: Text to encode
    :return: Token embeddings
    """
    return await litellm_counter(model, message)


async def litellm_counter(model: str, message: str) -> Callable:
    """
    Return token count of message based on model\n
    :param model: Model path to lookup tokenizer for
    :param message: Message to tokenize
    :return: `int` Number of tokens needed to represent message
    """
    from litellm.utils import token_counter
    import os

    model_name = os.path.split(model)
    model_name = os.path.join(os.path.split(model_name[0])[-1], model_name[-1])
    return token_counter(model_name, text=message)


async def ollama_counter(model: str, message: str) -> int:
    """
    Return token count of message based on ollama model\n
    :param model: Model to lookup tokenizer for
    :param message: Message to tokenize
    :return: `int` Number of tokens needed to represent message
    """
    from zodiac.providers.constants import CueType

    if not CueType.OLLAMA:
        return 0
    else:
        from ollama import embed

        response = embed(model, input=message)
        return len(response["embeddings"])


async def tiktoken_counter(model="cl100k_base", message: str = ""):
    """
    Return token count of gpt based on model\n
    :param model: Model path to lookup tokenizer for
    :param message: Message to tokenize
    :return: `int` Number of tokens needed to represent message
    """
    import tiktoken

    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(message))


async def cortex_counter(model: str, message: str) -> int:
    """
    Return token count of message based on cortex model\n
    :param model: Model to lookup tokenizer for
    :param message: Message to tokenize
    :return: `int` Number of tokens needed to represent message
    """
    from zodiac.providers.constants import CueType

    if not CueType.CORTEX:
        return 0
    else:
        import requests

        payload = {"input": message, "model": model, "encoding_format": "float"}
        headers = {"Content-Type": "application/json"}

        headers = {"Content-Type": "application/json"}

        response = requests.post("http://127.0.0.1:39281/v1/embeddings", json=payload, headers=headers, timeout=(1, 1))
        embedding = response.json()
        return len(next(iter(embedding["data"])).get("embedding"))


async def lmstudio_counter(model: str, message: str) -> int:
    """
    Return token count of message based on lm studio model\n
    :param model: Model to lookup tokenizer for
    :param message: Message to tokenize
    :return: `int` Number of tokens needed to represent message
    """
    from zodiac.providers.constants import CueType

    if not CueType.LM_STUDIO:
        return 0
    else:
        from lmstudio import llm

        model = llm()

        return len(model.tokenize(message))
