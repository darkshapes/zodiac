#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=pointless-statement, unsubscriptable-object
import array
from typing import Any, Optional
import dspy
# from pydantic import BaseModel, Field

from nnll.monitor.file import debug_monitor, dbug, nfo
from mir.registry_entry import RegistryEntry
from mir.constants import LibType, has_api, LIBTYPE_CONFIG


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
class ChatMachineWithMemory(dspy.Module):
    """Base module for Q/A chats using async and `dspy.Predict` List-based memory
    Defaults to 5 question history, 4 max workers, and `HistorySignature` query"""

    def __init__(self, max_workers=4) -> None:
        """
        Instantiate the module, setup parameters, create async streaming generator.\n
        Does not load any models until forward pass
        :param signature: The format of messages sent to the model
        :param max_workers: Maximum number of async processes, based on system resources
        """
        from nnll.configure.init_gpu import first_available
        from mir.mir_maid import MIRDatabase
        from nnll.tensor_pipe.construct_pipe import ConstructPipeline

        super().__init__()
        self.mir_db = MIRDatabase()
        self.factory = ConstructPipeline()
        self.device = first_available()
        self.max_workers = max_workers
        self.reg_entries = None
        self.pipe = None
        self.pipe_kwargs = None
        self.import_pkg = None
        self.streaming = True
        self.sig: dspy.Signature = QASignature

    def __call__(self, reg_entries: RegistryEntry, sig: dspy.Signature, streaming: bool = True) -> Any:
        """Load model in preparation of
        :param model: path to model
        :param library: LibType of model origin
        :param streaming: output type flag, defaults to True
        :yield: responses in chunks or response as a single block
        """
        from httpx import ResponseNotRead

        print("run run run")
        self.reg_entries = reg_entries
        self.sig = sig
        model = self.reg_entries.model
        library = self.reg_entries.library
        lora = None
        if library != LibType.HUB:
            api_kwargs = self.reg_entries.api_kwargs
            nfo(f"api_kwargs_passed = {api_kwargs}")
            dspy.settings.configure(lm=dspy.LM(model=model, **api_kwargs), async_max_workers=self.max_workers)
            if self.streaming:
                generator = dspy.asyncify(program=dspy.Predict(signature=self.sig))  # this should only be used in the case of text
                self.pipe = dspy.streamify(generator)
            else:
                self.pipe = dspy.Predict(signature=self.sig)
            return self.pipe
        else:
            # api_kwargs = await get_api(model=model, library=library)
            # generator = dspy.asyncify(constructor)
            # self.completion = dspy.streamify(generator)
            from nnll.tensor_pipe import segments as techniques
            from nnll.configure.init_gpu import soft_random, seed_planter

            mir_arch = self.reg_entries.mir
            series = mir_arch[0]
            arch_data = self.mir_db.database[series][mir_arch[1]]
            init_modules = self.mir_db.database[series]["[init]"]
            self.pipe, model, self.import_pkg, self.pipe_kwargs = self.factory.create_pipeline(arch_data, init_modules)

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

            noise_seed = seed_planter(soft_random())
            user_set = {
                "output_type": "pil",
            }
            self.pipe_kwargs.update(user_set)
            nfo(f"Pre-generator Model {model}  Pipe {self.pipe} Arguments {self.pipe_kwargs}")  # Lora {lora_opt}
            if "diffusers" in self.import_pkg:
                self.pipe.to(self.device)
                self.pipe = techniques.add_generator(pipe=self.pipe, noise_seed=noise_seed)
            else:
                self.pipe = self.pipe[0]
                self.pipe.to(self.device)
            if "audiogen" in self.import_pkg:
                self.pipe_kwargs.update({"sample_rate": self.pipe.config.sampling_rate})
            elif "parler_tts" in self.import_pkg:
                self.pipe_kwargs.update({"sampling_rate": self.pipe.config.sampling_rate})

        return self.pipe, self.import_pkg, self.pipe_kwargs

    # Reminder: Don't capture user prompts - this is the crucial stage
    async def forward(self, tx_data: dict[str | list[float]], mode_out: str = "text", metadata: Optional[dict] = None) -> Any:
        """
        Forward pass for multimodal process\n
        :param tx_data: prompt transmission values for all media formats
        :param mode_out: output type flag, defaults to "text"
        """
        yield self.pipe(message=tx_data["text"], stream=self.streaming)  # history=history)
        # else:
        #     if metadata is None:
        #         metadata = {}
        #     # memory threshold formula function returns boolean value here
        #     prompt = tx_data.get("text", "")
        #     content = None
        #     nfo(f"content = {metadata}")

        #     content = self.pipe(prompt=prompt, **self.pipe_kwargs).images[0]
        #         # may also be video!!
        #     elif self.import_pkg.get("audiogen", 0):
        #         content = self.pipe.generate([prompt])
        #         # metadata = self.pipe.sample_rate
        #     elif self.import_pkg.get("parler_tts", 0):
        #         input_ids = self.pipe[1](prompt).input_ids.to(self.device)
        #         prompt_input_ids = self.pipe[1](prompt).input_ids.to(self.device)
        #         generation = self.pipe.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
        #         content = generation.cpu().numpy().squeeze()
        #         # metadata = self.pipe.sampling_rate
        #     gen_data = disk.add_to_metadata(pipe=self.pipe, model=self.reg_entries.model, prompt=[prompt], kwargs=self.pipe_kwargs)
        #     if content:
        #         nfo(f"content = {content}")
        #         metadata.update(gen_data.get("parameters"))
        #         nfo(f"content type output {content}, {type(content)}")
        #     disk.write_to_disk(content, metadata)
        #     # Uniqueness Tag
        # from nnll_61 import HyperChain
        # data_chain = HyperChain()
        # data_chain.add_block(f"{pipe}{model}{kwargs}")
