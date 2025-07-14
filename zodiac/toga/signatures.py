# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

import dspy
from zodiac.providers.registry_entry import RegistryEntry

dspy.configure_cache(enable_disk_cache=False)


class QATask(dspy.Signature):
    """Reply with short responses within 60-90 word/10k character code limits"""

    question: str = dspy.InputField(desc="The question to respond to")
    answer = dspy.OutputField(desc="Often between 60 and 90 words and limited to 10000 character code blocks")


class StreamActivity(dspy.streaming.StatusMessageProvider):
    def lm_start_status_message(self, instance, inputs):
        return "Processing..."

    def module_start_status_message(self, instance, inputs):
        return "Module started."

    def lm_end_status_message(self, outputs):
        return "Done."

    def tool_start_status_message(self, instance, inputs):
        return "Tool started..."

    def tool_end_status_message(self, outputs):
        return "Tool finished."


class Predictor(dspy.Module):
    def __init__(self):
        super().__init__
        self.program = dspy.Predict(signature=QATask)

    def __call__(self, question: str):
        from litellm.exceptions import APIConnectionError
        from litellm.llms.ollama.common_utils import OllamaError
        from httpx import ConnectError
        from dspy.utils.exceptions import AdapterParseError
        from aiohttp.client_exceptions import ClientConnectorError

        try:
            return self.program(question=question)
        except (ClientConnectorError, ConnectError, AdapterParseError, APIConnectionError, OllamaError, OSError):
            pass


async def ready_predictor(registry_entry: RegistryEntry, async_stream: bool = True, dspy_stream: bool = True, max_workers: int = 8, cache: bool = True):
    lm_kwargs = {"async_max_workers": max_workers, "cache": cache}
    lm_model = dspy.LM(
        registry_entry.model,
        **registry_entry.api_kwargs,
        **lm_kwargs,
    )
    stream_listeners = [dspy.streaming.StreamListener(signature_field_name="answer")]
    context_kwargs = {"lm": lm_model}  # , "adapter": dspy.ChatAdapter()}
    predictor_kwargs = {
        "status_message_provider": StreamActivity(),
        "async_streaming": async_stream,
        "include_final_prediction_in_output_stream": False,
    }
    if dspy_stream:
        predictor_kwargs["stream_listeners"] = stream_listeners

    return context_kwargs, predictor_kwargs
