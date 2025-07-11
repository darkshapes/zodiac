#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-error

from typing import Callable, Optional

from toga.sources import Source

from zodiac.providers.registry_entry import RegistryEntry


class TokenStream(Source):
    def __init__(self):
        self.tokenizer: Optional[str] = None
        self.message: Optional[str] = None

    async def set_tokenizer(self, registry_entry: RegistryEntry) -> Callable:
        """Pass message to model routine
        :param model: Path to model
        :param message: Text to encode
        :return: Token embeddings
        """
        self.tokenizer = str(registry_entry.tokenizer)

    async def token_count(self, message: str) -> Callable:
        """
        Return token count of message based on model\n
        :param model: Model path to lookup tokenizer for
        :param message: Message to tokenize
        :return: `int` Number of tokens needed to represent message
        """
        import os
        import warnings

        warnings.filterwarnings("ignore", category=DeprecationWarning)

        from litellm.utils import token_counter

        character_count = len(message)
        model_name = os.path.split(self.tokenizer)
        model_name = os.path.join(os.path.split(model_name[0])[-1], model_name[-1])
        return token_counter(model_name, text=message), character_count
