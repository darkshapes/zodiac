#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-error


import warnings
from pathlib import Path
from typing import Callable, Optional

warnings.filterwarnings("ignore", category=DeprecationWarning)

from litellm.utils import create_tokenizer, token_counter
from toga.sources import Source
from zodiac.providers.registry_entry import RegistryEntry


class TokenStream(Source):
    def __init__(self):
        self.tokenizer: Optional[str] = None
        self.message: Optional[str] = None
        self.tokenizer_args = {}

    async def set_tokenizer(self, registry_entry: RegistryEntry) -> Callable:
        """Pass message to model routine
        :param model: Path to model
        :param message: Text to encode
        :return: Token embeddings for the model
        """
        import os
        import json

        if registry_entry.tokenizer:
            with open(str(registry_entry.tokenizer), encoding="UTF-8") as file_obj:
                tokenizer_json = json.load(file_obj)
                tokenizer_data = json.dumps(tokenizer_json)
                self.tokenizer_args = {"custom_tokenizer": create_tokenizer(tokenizer_data)}
        else:
            # model_name = os.path.split(registry_entry.model)
            # model_name = os.path.join(os.path.split(model_name[0])[-1], model_name[-1])
            # self.status_log.registry_entry.model
            self.tokenizer_args = {"model": registry_entry.model}

    async def token_count(
        self,
        message: str,
    ) -> Callable:
        """
        Return token count of message based on model\n
        :param model: Model path to lookup tokenizer for
        :param message: Message to tokenize
        :return: `int` Number of tokens needed to represent message
        """
        import warnings

        warnings.filterwarnings("ignore", category=DeprecationWarning)
        character_count = len(message)
        return token_counter(text=message, **self.tokenizer_args), character_count
