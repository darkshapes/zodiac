#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=pointless-statement, unsubscriptable-object

from typing import Any, Optional
import dspy
# from pydantic import BaseModel, Field

from nnll.monitor.console import nfo
from zodiac.providers.registry_entry import RegistryEntry

ps_sysprompt = "Provide x for Y"
bqa_sysprompt = "Reply with short responses within 60-90 word/10k character code limits"
ps_infield_tag = "An image of x"
ps_outfield_tag = "The nature of the x in the image."
ps_edit_message = "Edited input image of the dog with a yellow hat."

is_msg: str = "Description x of the image to generate"
is_out: str = "An image matching the description x"


class I2ISignature(dspy.Signature):
    f"""{ps_sysprompt}"""
    # This is an example multimodal input signature
    image_input: dspy.Image = dspy.InputField(desc=ps_infield_tag)
    answer: str = dspy.OutputField(desc=ps_outfield_tag)
    image_output: dspy.Image = dspy.OutputField(desc=ps_edit_message)


class BasicImageSignature(dspy.Signature):
    message: str = dspy.InputField(desc=is_msg)
    image_output: dspy.Image = dspy.OutputField(desc=is_out)


class QASignature(dspy.Signature):
    f"""{bqa_sysprompt}"""

    message: str = dspy.InputField(desc="The message to respond to")
    # history: dspy.History = dspy.InputField()
    answer = dspy.OutputField(desc="Often between 60 and 90 words and limited to 10000 character code blocks")


# Don't capture user prompts: AVOID logging this class as much as possible
class VectorMachine(dspy.Module):
    """Base module for inference using async and `dspy.Predict` List-based memory\n
    Defaults to 5 question history, 4 max workers, and `HistorySignature` query"""

    def __init__(self, max_workers=4) -> None:
        """
        Instantiate the module, setup parameters, create async streaming generator.\n
        Does not load any models until forward pass
        :param signature: The format of messages sent to the model
        :param max_workers: Maximum number of async processes, based on system resources
        """
        from mir.mir_maid import MIRDatabase
        from nnll.tensor_pipe.construct_pipe import ConstructPipeline
        from zodiac.providers.constants import ChipType

        super().__init__()
        self.mir_db = MIRDatabase()
        self.factory = ConstructPipeline()
        self.device = getattr(ChipType, next(iter(ChipType._show_ready())), "CPU")
        self.max_workers = max_workers
        self.registry_entries = None
        self.pipe = None
        self.pipe_kwargs = None
        self.import_pkg = None
        self.streaming = True
        self.sig: dspy.Signature = QASignature
        self.recycle = True

    def active_models(self, registry_entries: RegistryEntry, sig: dspy.Signature, streaming: bool = True) -> Any:
        """Prepare model for iniference\n
        :param registry_entries: model info
        :param sig: Type of generation output desired
        :param streaming: output type flag, defaults to True
        :yield: responses in chunks or response as a single block
        """
        from zodiac.providers.constants import CueType, ChipType

        self.registry_entries = registry_entries
        self.sig = sig
        self.streaming = streaming
        model = self.registry_entries.model
        cuetype = self.registry_entries.cuetype
        lora = None
        if cuetype != CueType.HUB:
            api_kwargs = self.registry_entries.api_kwargs
            nfo(f"api_kwargs_passed = {api_kwargs}")
            dspy.settings.configure(lm=dspy.LM(model=model, **api_kwargs), async_max_workers=self.max_workers)
            if self.streaming:
                generator = dspy.asyncify(program=dspy.Predict(signature=self.sig))  # this should only be used in the case of text
                self.pipe = dspy.streamify(generator)
            else:
                self.pipe = dspy.Predict(signature=self.sig)
            return self.pipe
        else:
            from nnll.tensor_pipe import segments
            from nnll.configure.init_gpu import seed_planter

            mir_arch = self.registry_entries.mir
            series = mir_arch[0]
            arch_data = self.mir_db.database[series][mir_arch[1]]
            pkg_data = self.mir_db.database[series]["pkg"][0]
            for pkg in ChipType._show_pkgs():  # pylint:disable=protected-access
                init_modules = pkg_data.get(pkg.value[1].lower())
                if init_modules:
                    break
            self.pipe, model, self.import_pkg, self.pipe_kwargs = self.factory.create_pipeline(arch_data=arch_data, init_modules=init_modules)

            # lora=lora_opt)
            if lora is not None:
                lora_arch = self.mir_db.database[series].get(lora[1])
                lora_repo = next(iter(lora_arch["repo"]))  # <- user location here OR this
                scheduler = self.mir_db.database[series]["[init]"].get("scheduler")
                kwargs = {}
                if scheduler:
                    sched = self.mir_db.database[scheduler]["[init]"]
                    scheduler_kwargs = self.mir_db.database[series]["[init]"].get("scheduler_kwargs")
                    kwargs = {sched: sched, scheduler_kwargs: scheduler_kwargs}
                init_kwargs = lora_arch.get("init_kwargs")
                if lora:
                    self.pipe = self.factory.add_lora(self.pipe, lora_repo=lora_repo, init_kwargs=init_kwargs, **kwargs)

            noise_seed = seed_planter(device=self.device)
            user_set = {
                "output_type": "pil",
            }
            self.pipe_kwargs.update(user_set)

            if ChipType.MPS[0]:
                self.pipe.enable_attention_slicing()
            nfo(f"Pre-generator Model {model}  Pipe {self.pipe} Arguments {self.pipe_kwargs}")  # Lora {lora_opt}
            if "diffusers" in self.import_pkg:
                self.pipe.to(self.device)
                self.pipe = segments.add_generator(pipe=self.pipe, noise_seed=noise_seed)
            else:
                self.pipe = self.pipe[0]
                self.pipe.to(self.device)
            if "audiogen" in self.import_pkg:
                self.pipe_kwargs.update({"sample_rate": self.pipe.config.sampling_rate})
            elif "parler_tts" in self.import_pkg:
                self.pipe_kwargs.update({"sampling_rate": self.pipe.config.sampling_rate})
        self.recycle = True

        return self.pipe, self.import_pkg, self.pipe_kwargs

    # Reminder: Don't capture user prompts - this is the crucial stage
    async def forward(self, tx_data: dict[str | list[float]], mode_out: str = "text", metadata: Optional[dict] = None) -> Any:
        """
        Forward pass for multimodal process\n
        :param tx_data: prompt transmission values for all media formats
        :param mode_out: output type flag, defaults to "text"
        """
        yield self.pipe(message=tx_data["text"], stream=self.streaming)  # history=history)

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
