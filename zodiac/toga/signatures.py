# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

import dspy
from typing import Callable
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
    def __init__(
        self,
        registry_entry: RegistryEntry,
        signature: dspy.Signature = QATask,
        max_workers: int = 8,
        cache: bool = False,
    ):
        super().__init__()
        program = dspy.Predict(signature=signature)
        self.registry_entry = registry_entry
        self.context_kwargs = {"async_max_workers": max_workers, "cache": cache}
        # aprogram = dspy.asyncify(program=program)
        streamify_arguments = {
            "stream_listeners": [
                dspy.streaming.StreamListener(signature_field_name="answer"),
            ],
            "status_message_provider": StreamActivity(),
            "include_final_prediction_in_output_stream": False,
        }
        self.aprogram = dspy.streamify(program, async_streaming=True, **streamify_arguments)

    async def forward(self, question: str):
        with dspy.context(
            lm=dspy.LM(
                self.registry_entry.model,
                **self.context_kwargs,
                **self.registry_entry.api_kwargs,
            )
        ):
            yield self.aprogram(question=question)  # history=history)


# with ThreadPoolExecutor(max_workers=5) as executor:
#     executor.map(worker, range(3))


# def wrap_program(program: dspy.Module, metric: Callable):
#     def wrapped_program(example):
#         with dspy.context(trace=[]):
#             prediction, trace, score = None, None, 0.0
#             try:
#                 prediction = program(**example.inputs())

# with dspy.context(lm=dspy.LM(registry_entry), callbacks=[]):
#     assert dspy.settings.lm.model == registry_entry


# async def read_output_stream():
#     output = stream_predict(question="why did a chicken cross the kitchen?")

#     return_value = None
#     async for chunk in output:
#         if isinstance(chunk, dspy.streaming.StreamResponse):
#             print(chunk)
#         elif isinstance(chunk, dspy.Prediction):
#             return_value = chunk
#     return return_value


# program_output = asyncio.run(read_output_stream())
# print("Final output: ", program_output)
