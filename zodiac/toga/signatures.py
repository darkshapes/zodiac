# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

import dspy
from zodiac.providers.registry_entry import RegistryEntry

from zodiac.providers.constants import CueType, ChipType, PkgType, MIR_DB

dspy.configure_cache(enable_disk_cache=False)


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


class QATask(dspy.Signature):
    """Reply with short responses within 60-90 word/10k character code limits"""

    question: str = dspy.InputField(desc="The question to respond to")
    answer = dspy.OutputField(desc="Often between 60 and 90 words and limited to 10000 character code blocks")


TARGET_LANGUAGE = "English"


class TranslateTask(dspy.Signature):
    f"""Translate from a language to {TARGET_LANGUAGE}"""

    message: dspy.Image | dspy.Audio | str = dspy.InputField(desc="The input to translate.")
    translation: dspy.Image | dspy.Audio | str = dspy.OutputField(desc="A translation of the input")


class VisionTask(dspy.Signature):
    """Describe the image in detail."""

    image: dspy.Image = dspy.InputField(desc="An image")
    description: str = dspy.OutputField(desc="A detailed description of the image.")


class TranscribeTask(dspy.Signature):
    """Transcribe spoken words into text"""

    message: dspy.Audio = dspy.InputField(desc="The speech to transcribe.")
    answer: str = dspy.OutputField(desc="A transcript of the recorded speech")


class GenerativeImageTask(dspy.Signature):
    message: str = dspy.InputField(desc="Description of the image to generate")
    image: dspy.Image = dspy.OutputField(desc="An image matching the description")


class GenerativeAudioTask(dspy.Signature):
    message: str = dspy.InputField(desc="Description of the audio to generate")
    audio: dspy.Audio = dspy.OutputField(desc="An audio file matching the description")


# cherry pick examples
# dspy.Adapter.format(demos=[{:,:}],signatures:,inputs:)


class QuestionAnswer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(QATask)

    def forward(self, question, **kwargs):
        self.predict(question=question, **kwargs)
        return self.predict(question=question, **kwargs)


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

    # from nnll.tensor_pipe import segments
    # from nnll.configure.init_gpu import seed_planter
    # mir_db = MIR_DB.database
    # mir_arch = registry_entries.mir
    # arch_data = mir_db[mir_arch[0][mir_arch[1]]]
    # pkg_data = mir_db[mir_arch[0]]["pkg"][0]
    # init_modules = find_package
    # self.pipe, model, self.import_pkg, self.pipe_kwargs = self.factory.create_pipeline(arch_data=registry_entry.mir, init_modules=init_modules)

    #     if lora is not None:
    #         lora_arch = self.mir_db.database[series].get(lora[1])
    #         lora_repo = next(iter(lora_arch["repo"]))  # <- user location here OR this
    #         scheduler = self.mir_db.database[series]["[init]"].get("scheduler")
    #         kwargs = {}
    #         if scheduler:
    #             sched = self.mir_db.database[scheduler]["[init]"]
    #             scheduler_kwargs = self.mir_db.database[series]["[init]"].get("scheduler_kwargs")
    #             kwargs = {sched: sched, scheduler_kwargs: scheduler_kwargs}
    #         init_kwargs = lora_arch.get("init_kwargs")
    #         if lora:
    #             self.pipe = self.factory.add_lora(self.pipe, lora_repo=lora_repo, init_kwargs=init_kwargs, **kwargs)

    #     noise_seed = seed_planter(device=self.device)
    #     user_set = {
    #         "output_type": "pil",
    #     }
    #     self.pipe_kwargs.update(user_set)

    #     if ChipType.MPS[0]:
    #         self.pipe.enable_attention_slicing()
    #     nfo(f"Pre-generator Model {model}  Pipe {self.pipe} Arguments {self.pipe_kwargs}")  # Lora {lora_opt}
    #     if "diffusers" in self.import_pkg:
    #         self.pipe.to(self.device)
    #         self.pipe = segments.add_generator(pipe=self.pipe, noise_seed=noise_seed)
    #     else:
    #         self.pipe = self.pipe[0]
    #         self.pipe.to(self.device)
    #     if "audiogen" in self.import_pkg:
    #         self.pipe_kwargs.update({"sample_rate": self.pipe.config.sampling_rate})
    #     elif "parler_tts" in self.import_pkg:
    #         self.pipe_kwargs.update({"sampling_rate": self.pipe.config.sampling_rate})


async def ready_predictor(registry_entry: RegistryEntry, async_stream: bool = True, dspy_stream: bool = True, max_workers: int = 8, cache: bool = True):
    if registry_entry.cuetype == CueType.HUB:
        device = getattr(ChipType, next(iter(ChipType._show_ready())), "CPU")

    else:
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


# import sounddevice as sd
