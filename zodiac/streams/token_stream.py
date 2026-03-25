#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-error

from typing import Callable, Optional

import tiktoken
from toga.sources import Source
from zodiac.providers.registry_entry import RegistryEntry


async def tiktoken_counter(model="cl100k_base", message: str = ""):
    """
    Return token count of gpt based on model\n
    :param model: Model path to lookup tokenizer for
    :param message: Message to tokenize
    :return: `int` Number of tokens needed to represent message
    """

    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(message))


class TokenStream(Source):
    def __init__(self):
        self.tokenizer: Optional[str] = None
        self.message: Optional[str] = None
        self.tokenizer_args = {}

    async def set_tokenizer(self, registry_entry: RegistryEntry) -> Callable:
        """Pass message to model routine\n
        :param model: Path to model
        :param message: Text to encode
        :return: Token embeddings for the model"""

        self.tokenizer_args = {}  # Disabled until suitable replacement is found

    async def token_count(
        self,
        message: str,
    ) -> Callable:
        """Return token count of message based on model\n
        :param model: Model path to lookup tokenizer for
        :param message: Message to tokenize
        :return: `int` Number of tokens needed to represent message"""
        import warnings

        warnings.filterwarnings("ignore", category=DeprecationWarning)
        character_count = len(message)
        return tiktoken_counter(text=message, **self.tokenizer_args), character_count
