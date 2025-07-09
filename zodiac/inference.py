#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=pointless-statement, unsubscriptable-object

from typing import Any, Optional, Callable, Dict, Union, List
import dspy

# from pydantic import BaseModel, Field
from zodiac.providers.registry_entry import RegistryEntry
from zodiac.toga.signatures import QATask

# from pydantic import BaseModel
# from zodiac.providers.constants import ChipType, MIR_DB as mir_db


class InferenceProcessor(dspy.Module):
    """Base module for inference using async and `dspy.Predict` List-based memory\n
    Defaults to 5 question history, 4 max workers, and `HistorySignature` query"""

    streaming: bool = True
    max_workers: int = 4
    pipe: Callable = None
    pipe_kwargs = Dict[str, Union[str, bool, int, float]]
    registry_entries: RegistryEntry = None
    import_pkg: str = None
    recycle: bool = True

    def __init__(self) -> None:
        """
        Instantiate the module, setup parameters, create async streaming generator.\n
        Does not load any models until forward pass
        :param signature: The format of messages sent to the model
        :param max_workers: Maximum number of async processes, based on system resources
        """
        from zodiac.providers.constants import ChipType

        super().__init__()
        if not dspy.settings.async_max_workers:
            dspy.settings.configure(async_max_workers=self.max_workers)
        elif dspy.settings.async_max_workers != self.max_workers:
            dspy.settings.async_max_workers = self.max_workers
        self.device = getattr(ChipType, next(iter(ChipType._show_ready())), "CPU")
        self.sig: dspy.Signature = QATask

    def ready(self, registry_entries: RegistryEntry, sig: dspy.Signature = QATask, streaming: bool = streaming) -> Any:
        """Prepare model for iniference\n
        :param registry_entries: model info
        :param sig: Type of generation output desired
        :param streaming: output type flag, defaults to True
        :yield: responses in chunks or response as a single block"""

        self.registry_entries = registry_entries
        self.sig = sig
        self.streaming = streaming
        self.lm = dspy.LM(model=self.registry_entries.model, **self.registry_entries.api_kwargs)
        if self.streaming:
            generator = dspy.asyncify(program=dspy.Predict(signature=self.sig))  # this should only be used in the case of text
            self.pipe = dspy.streamify(generator)
        else:
            self.pipe = dspy.Predict(signature=self.sig)

        self.recycle = True

        return self.pipe, self.import_pkg, self.pipe_kwargs

    # Reminder: Don't capture user prompts - this is the crucial stage
    async def forward(self, prompts: Dict[str, List[float]], metadata: Optional[dict] = None) -> Any:
        """Forward pass for multimodal process\n
        :param prompts: prompt transmission values for all media formats
        :param metadata: Additional metadata to tag the generation with, defaults to None
        ```
        name    [ medium : data ]
                ,-text     String
                ⏐-image    List
        tx_data-⏐-speech   List
                ⏐-video    List
                '-music    List
        ```
        """

        with dspy.context(lm=self.lm, async_max_workers=self.max_workers):
            try:
                yield self.pipe(message=prompts["text"], stream=self.streaming)  # history=history)
            except GeneratorExit:
                pass

    def destroy(self, recycle: bool = True):
        """殺死他們。 殺死你的敵人。 征服他們的精神。 把他們的頭骨粉碎在你的腳下。
        Slay them. Slay your enemies. Crush their skulls beneath your feet.\n
        :param recycle: Please keep cache clean, thank you, defaults to True"""
        from nnll.configure.init_gpu import first_available
        import gc

        self.pipe.unload_lora_weights()
        # del self.pipe.unet
        if self.pipe:
            del self.pipe
        self.pipe = None
        first_available(clean=True)
        self.recycle = recycle
        gc.collect()

    # nfo("sync")
    # nfo(f"chat registry entries : {chat.registry_entries}")
    # if not streaming:
    #     metadata = {}
    #     prompt = tx_data["text"]
    #     content = chat.pipe(prompt=prompt, **chat.pipe_kwargs).images[0]
    #     gen_data = disk.add_to_metadata(pipe=chat.pipe, model=chat.registry_entries.model, prompt=[prompt], kwargs=chat.pipe_kwargs)
    #     # nfo(f"content = {content}")
    #     metadata.update(gen_data.get("parameters"))
    #     # nfo(f"content type output {content}, {type(content)}")
    #     disk.write_to_disk(content, metadata)
    #     # chat.destroy()
    # else:  # history=history)
    # from nnll.tensor_pipe.construct_pipe import ConstructPipeline
    # self.factory = ConstructPipeline()


# pipe_2 =
#  else:
#             from nnll.tensor_pipe import segments
#             from nnll.configure.init_gpu import seed_planter

#             mir_arch = self.registry_entries.mir
#             series = mir_arch[0]
#             arch_data = self.mir_db.database[series][mir_arch[1]]
#             pkg_data = self.mir_db.database[series]["pkg"][0]
#             for pkg in ChipType._show_pkgs():  # pylint:disable=protected-access
#                 init_modules = pkg_data.get(pkg.value[1].lower())
#                 if init_modules:
#                     break
#             self.pipe, model, self.import_pkg, self.pipe_kwargs = self.factory.create_pipeline(arch_data=arch_data, init_modules=init_modules)

#             if lora is not None:
#                 lora_arch = self.mir_db.database[series].get(lora[1])
#                 lora_repo = next(iter(lora_arch["repo"]))  # <- user location here OR this
#                 scheduler = self.mir_db.database[series]["[init]"].get("scheduler")
#                 kwargs = {}
#                 if scheduler:
#                     sched = self.mir_db.database[scheduler]["[init]"]
#                     scheduler_kwargs = self.mir_db.database[series]["[init]"].get("scheduler_kwargs")
#                     kwargs = {sched: sched, scheduler_kwargs: scheduler_kwargs}
#                 init_kwargs = lora_arch.get("init_kwargs")
#                 if lora:
#                     self.pipe = self.factory.add_lora(self.pipe, lora_repo=lora_repo, init_kwargs=init_kwargs, **kwargs)

#             noise_seed = seed_planter(device=self.device)
#             user_set = {
#                 "output_type": "pil",
#             }
#             self.pipe_kwargs.update(user_set)

#             if ChipType.MPS[0]:
#                 self.pipe.enable_attention_slicing()
#             nfo(f"Pre-generator Model {model}  Pipe {self.pipe} Arguments {self.pipe_kwargs}")  # Lora {lora_opt}
#             if "diffusers" in self.import_pkg:
#                 self.pipe.to(self.device)
#                 self.pipe = segments.add_generator(pipe=self.pipe, noise_seed=noise_seed)
#             else:
#                 self.pipe = self.pipe[0]
#                 self.pipe.to(self.device)
#             if "audiogen" in self.import_pkg:
#                 self.pipe_kwargs.update({"sample_rate": self.pipe.config.sampling_rate})
#             elif "parler_tts" in self.import_pkg:
#                 self.pipe_kwargs.update({"sampling_rate": self.pipe.config.sampling_rate})

# class InferenceProcessor(BaseModel):
#     """Base module for inference\n"""
#     registry_entry: RegistryEntry = None
#     recycle: bool = True

#     def __init__(self, sig: dspy.Signature, streaming: bool = True, max_workers: int = 8) -> None:
#         """Instantiate the module, setup parameters, create async streaming generator.\n
#         Does not load any models until forward pass\n
#         :param signature: The format of messages sent to the model
#         :param max_workers: Maximum number of async processes, based on system resources
#         """
#         super().__init__()
#         if not dspy.settings.async_max_workers:
#             dspy.settings.configure(async_max_workers=self.max_workers)
#         elif dspy.settings.async_max_workers != self.max_workers:
#             dspy.settings.async_max_workers = self.max_workers
#         self.device = getattr(ChipType, next(iter(ChipType._show_ready())), "CPU")
#         self.sig = sig
#         self.streaming = streaming

#     # Reminder: Don't capture user prompts - this is the crucial stage
#     async def forward(self, prompts: dict[str | list[float]], metadata: Optional[dict] = None) -> Any:
#         """Forward pass for processing\n
#         :param registry_entries: Model sequence to run
#         :param prompts: prompt Transmission values for all media formats
#         :param metadata: Additional metadata to embed into the generation"""
#         self.lm = dspy.LM(model=self.registry_entry.model, **self.registry_entry.api_kwargs)

#         with dspy.context(lm=self.lm, async_max_workers=self.max_workers):
#             try:
#                 yield self.pipe(message=prompts["text"], stream=self.streaming)  # history=history)
#             except GeneratorExit:
#                 pass

#     def destroy(self, recycle: bool = True):
#         """殺死他們。 殺死你的敵人。 征服他們的精神。 把他們的頭骨粉碎在你的腳下。
#         Slay them. Slay your enemies. Crush their skulls beneath your feet.\n
#         :param recycle: Please keep cache clean, thank you, defaults to True"""
#         from nnll.configure.init_gpu import first_available
#         import gc

#         self.pipe.unload_lora_weights()
#         # del self.pipe.unet
#         if self.pipe:
#             del self.pipe
#         self.pipe = None
#         first_available(clean=True)
#         self.recycle = recycle
#         gc.collect()


# class TextProcessor(InferenceProcessor, dspy.Module):


#     pipe: Callable = None
#     pipe_kwargs = Dict[str, Union[str, bool, int, float]]
# class ImageProcessor(dspy.Module):
#     """    using async and `dspy.Predict` List-based memory
#     Defaults to 5 question history, 4 max workers, and `HistorySignature` query
#     """
#         from zodiac.providers.constants import CueType
#                 if self.registry_entries.cuetype != CueType.HUB:


#     def active_models(self, registry_entries: RegistryEntry, ) -> Any:
#         """Prepare model for iniference\n
#         :param registry_entries: model info
#         :param sig: Type of generation output desired
#         :param streaming: output type flag, defaults to True
#         :yield: responses in chunks or response as a single block
#         """
#         from zodiac.providers.constants import CueType, ChipType

#         self.registry_entries = registry_entries
#         self.sig = sig
#         self.streaming = streaming
#         lora = None
#         if self.registry_entries.cuetype != CueType.HUB:
#             self.lm = dspy.LM(model=self.registry_entries.model, **self.registry_entries.api_kwargs)

#         else:
#             from nnll.tensor_pipe import segments
#             from nnll.configure.init_gpu import seed_planter

#             mir_arch = self.registry_entries.mir
#             series = mir_arch[0]
#             arch_data = self.mir_db.database[series][mir_arch[1]]
#             pkg_data = self.mir_db.database[series]["pkg"][0]
#             for pkg in ChipType._show_pkgs():  # pylint:disable=protected-access
#                 init_modules = pkg_data.get(pkg.value[1].lower())
#                 if init_modules:
#                     break
#             self.pipe, model, self.import_pkg, self.pipe_kwargs = self.factory.create_pipeline(arch_data=arch_data, init_modules=init_modules)

#             if lora is not None:
#                 lora_arch = self.mir_db.database[series].get(lora[1])
#                 lora_repo = next(iter(lora_arch["repo"]))  # <- user location here OR this
#                 scheduler = self.mir_db.database[series]["[init]"].get("scheduler")
#                 kwargs = {}
#                 if scheduler:
#                     sched = self.mir_db.database[scheduler]["[init]"]
#                     scheduler_kwargs = self.mir_db.database[series]["[init]"].get("scheduler_kwargs")
#                     kwargs = {sched: sched, scheduler_kwargs: scheduler_kwargs}
#                 init_kwargs = lora_arch.get("init_kwargs")
#                 if lora:
#                     self.pipe = self.factory.add_lora(self.pipe, lora_repo=lora_repo, init_kwargs=init_kwargs, **kwargs)

#             noise_seed = seed_planter(device=self.device)
#             user_set = {
#                 "output_type": "pil",
#             }
#             self.pipe_kwargs.update(user_set)

#             if ChipType.MPS[0]:
#                 self.pipe.enable_attention_slicing()
#             nfo(f"Pre-generator Model {model}  Pipe {self.pipe} Arguments {self.pipe_kwargs}")  # Lora {lora_opt}
#             if "diffusers" in self.import_pkg:
#                 self.pipe.to(self.device)
#                 self.pipe = segments.add_generator(pipe=self.pipe, noise_seed=noise_seed)
#             else:
#                 self.pipe = self.pipe[0]
#                 self.pipe.to(self.device)
#             if "audiogen" in self.import_pkg:
#                 self.pipe_kwargs.update({"sample_rate": self.pipe.config.sampling_rate})
#             elif "parler_tts" in self.import_pkg:
#                 self.pipe_kwargs.update({"sampling_rate": self.pipe.config.sampling_rate})
#         self.recycle = True

#         return self.pipe, self.import_pkg, self.pipe_kwargs


# from nnll.tensor_pipe.construct_pipe import ConstructPipeline
# self.factory = ConstructPipeline()

# async def send_to_clipboard_and_paste(stream):
#     keyboard = Controller()

#     async def copy_to_clipboard(text):
#         """Asynchronously copy text to the clipboard."""
#         pyperclip.copy(text)
#         await asyncio.sleep(0.1)  # Allow time for the clipboard to update

#     async def simulate_paste():
#         """Simulate a paste action (Ctrl+V)."""
#         with keyboard.pressed(Key.ctrl):
#             keyboard.press("v")
#             keyboard.release("v")
#         await asyncio.sleep(0.5)  # Wait for paste to complete

#     for text in stream:
#         print(f"Copying to clipboard: {text}")
#         await copy_to_clipboard(text)
#         print("Simulating paste action...")
#         await simulate_paste()


# # Entry point
# async def main():
#     stream = text_stream()
#     await send_to_clipboard_and_paste(stream)


# # Run the async loop
# if __name__ == "__main__":
#     asyncio.run(main())
