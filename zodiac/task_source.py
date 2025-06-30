#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import List, Optional, Dict
from toga.sources import Source
from zodiac.providers.constants import CueType
from zodiac.providers.registry_entry import RegistryEntry


class TaskSource(Source):
    def __init__(self):
        from mir.mir_maid import MIRDatabase

        self.mode_types = {
            ("image", "image"): ["Img2Img", "Inpaint", "ControlNet"],
            ("text", None): ["ForConditionalGeneration"],
            # Add more modes here as needed
        }
        self.mir_db = MIRDatabase()
        self.package_name: Optional[str] = None
        self.class_name: Optional[str] = None
        self.model_mode: Optional[List[str]] = None
        self.exclude: Optional[List[str]] = None

    async def flatten_list(self, nested_list: List[str]) -> List[str]:
        flat_list = []
        for i in nested_list:
            if isinstance(i, list):
                flat_list.extend(await self.flatten_list(i))
            else:
                flat_list.append(i)
        return flat_list

    async def set_filter_type(self, mode_in: Optional[str] = "image", mode_out: Optional[str] = "image") -> None:
        """Filter class items by modality\n
        :param mode_in: Input modality operation, defaults to "image"
        :param mode_out: Output modality operation, defaults to "image"
        """
        model_mode = (mode_in, mode_out)
        if model_mode in self.mode_types:
            self.model_mode = self.mode_types[model_mode]
            self.exclude = None
        else:
            self.model_mode = None
            self.exclude = await self.flatten_list(self.mode_types.values())

    async def trace_tasks(self, entry: RegistryEntry) -> List[str]:
        """Trace tasks for a given model registry entry.\n
        :param entry: The object containing the model information.
        :return: A sorted list of tasks applicable to the model."""

        from mir.inspectors import show_tasks_for
        from nnll.tensor_pipe.deconstructors import get_code_names

        snips: Dict[str, List[str]] = {"transformers": ["Model", "ForConditionalGeneration"], "diffusers": ["Pipeline"]}

        if entry.cuetype == CueType.HUB and entry.mir:
            print(entry.mir)
            model_data = self.mir_db.database[entry.mir[0]][entry.mir[1]]
            package_data = [content for content in model_data.get("pkg").values() if next(iter(content)) in ["diffusers", "transformers"]]
            print(package_data)
            if package_data:
                self.package_name = next(iter(package_data[0]))
                self.class_name = package_data[0][self.package_name]
                code_name = get_code_names(self.class_name, self.package_name)
                if self.package_name == "transformers":
                    preformatted_task_data = show_tasks_for(code_name=code_name)
                else:
                    preformatted_task_data = show_tasks_for(code_name=code_name, class_name=self.class_name)
                    preformatted_task_data.sort()
                snip_words = snips.get(self.package_name)
                class_prefix = self.class_name.replace(snip_words[0], "")
                snip_words.append(class_prefix)
                filtered_tasks = await self.filter_tasks(preformatted_task_data, snip_words)
                return filtered_tasks
        return

    async def filter_tasks(self, preformatted_task_data: List[str], snip_words: List[str]) -> List[str]:
        """Processes preformatted task data by removing specified prefixes and keywords, then adds valid data to task_data.\n
        :param preformatted_task_data: A list of strings to be processed.
        :param snip_words: A list of prefixes or suffixes to be removed from each pipe.
        :return: A sorted list of unique task_data entries after processing.
        """
        import re

        self._task_data = set()
        for pipe in preformatted_task_data:
            pattern = "|".join(map(re.escape, snip_words))
            pipe = re.sub(pattern, "", pipe)
            if pipe:
                if self.model_mode and any(x for x in self.model_mode if x in pipe):
                    self._task_data.add(pipe)
                elif self.exclude and not any(x for x in self.exclude if x in pipe):
                    self._task_data.add(pipe)
        self._task_data = list(self._task_data)
        self._task_data.sort()
        return self._task_data

    def __len__(self):
        return len(list(self._task_data()))

    def __getitem__(self, index):
        return self._task_data()[index]

    def index(self, entry):
        return self._task_data().index(entry)

    async def clear(self):
        self._task_data = []
        self.notify("clear")
