# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

import dspy
from zodiac.providers.registry_entry import RegistryEntry


class QATask(dspy.Signature):
    """Reply with short responses within 60-90 word/10k character code limits"""

    question: str = dspy.InputField(desc="The question to respond to")
    answer = dspy.OutputField(desc="Often between 60 and 90 words and limited to 10000 character code blocks")


class StreamActivity(dspy.streaming.StatusMessageProvider):
    def lm_start_status_message(self, instance, inputs):
        return "Processing.."

    def module_start_status_message(self, instance, inputs):
        return "Preparing..."

    def module_end_status_message(self, outputs):
        return "Completed."

    def lm_end_status_message(self, outputs):
        return "Done."

    def tool_start_status_message(self, instance, inputs):
        return "Tool start..."

    def tool_end_status_message(self, outputs):
        return "Tool end."


class Predictor(dspy.Module):
    def __init__(self):
        self.program = dspy.Predict(signature=QATask)

    def __call__(self, question: str):
        return self.program(question=question)


async def ready_predictor(registry_entry: RegistryEntry, max_workers: int = 8, cache: bool = False):
    lm_kwargs = {"async_max_workers": max_workers, "cache": cache}
    lm_model = dspy.LM(
        registry_entry.model,
        **registry_entry.api_kwargs,
        **lm_kwargs,
    )
    context_kwargs = {"lm": lm_model, "adapter": dspy.ChatAdapter()}
    predictor_kwargs = {
        "stream_listeners": [
            dspy.streaming.StreamListener(signature_field_name="answer"),
        ],
        "status_message_provider": StreamActivity(),
        "async_streaming": True,
        "include_final_prediction_in_output_stream": False,
    }

    return context_kwargs, predictor_kwargs
