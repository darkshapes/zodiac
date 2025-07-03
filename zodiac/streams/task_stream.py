#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import List, Any
from toga.sources import Source
from zodiac.providers.registry_entry import RegistryEntry
from zodiac.streams.class_stream import find_package, show_transformer_tasks


flatten_map: List[Any] = lambda nested, unpack: [element for iterative in getattr(nested, unpack)() for element in iterative]
flatten_map.__annotations__ = {"nested": List[str], "unpack": str}


class TaskStream(Source):
    def __init__(self):
        self.basic_tasks = {
            "speech": ["Audio"],
            "image": ["ControlNet", "PAG"],
            "text": [
                "QuestionAnswering",
                "SequenceClassification",
            ],
        }
        self.exclusive_tasks = {
            ("image", "text"): ["Vision"],
            ("image", "image"): ["Img2Img", "Inpaint", "PAG"],
            ("text", "text"): ["Text", "CasualLM", "SequenceClassification", "QuestionAnswering"],
        }
        self.all_tasks = set().union(*self.basic_tasks.values()).union(*self.exclusive_tasks.values())

    async def set_filter_type(self, mode_in: str = "image", mode_out: str = "image") -> None:
        """Filter class items by modality
        :param mode_in: Input modality operation, defaults to "image"
        :param mode_out: Output modality operation, defaults to "image"
        """
        self.tasks = None
        self.exclude = None
        self.tasks = set()
        self.exclude = set()

        if (mode_in, mode_out) in self.exclusive_tasks:
            self.tasks = self.exclusive_tasks[(mode_in, mode_out)]
        else:
            if mode_in in self.basic_tasks:
                self.tasks.update(self.basic_tasks[mode_in])
            if mode_out in self.basic_tasks:
                self.tasks.update(self.basic_tasks[mode_out])
        self.exclude = self.all_tasks.difference(self.tasks)

    async def trace_tasks(self, entry: RegistryEntry) -> List[str]:
        """Trace tasks for a given model registry entry.\n
        :param entry: The object containing the model information.
        :return: A sorted list of tasks applicable to the model."""

        from mir.mappers import show_tasks_for
        from nnll.tensor_pipe.deconstructors import get_code_names

        snip_words: List[str] = ["Model", "PreTrained", "ForConditionalGeneration", "Pipeline", "For"]
        if entry.mir:
            package_bundle = await find_package(entry)
            if package_bundle:
                class_name = package_bundle[0]
                package_name = package_bundle[1].value[1].lower()
                if package_name == "transformers":
                    preformatted_task_data = await show_transformer_tasks(class_name)
                else:
                    code_name = get_code_names(class_name, package_name)
                    preformatted_task_data = show_tasks_for(code_name=code_name, class_name=class_name)
                    preformatted_task_data.sort()
                filtered_tasks = await self.filter_tasks(preformatted_task_data, snip_words)
                return filtered_tasks
        return None

    async def filter_tasks(self, preformatted_task_data: List[str], snip_words: List[str]) -> List[str]:
        """Processes preformatted task data by removing specified prefixes and keywords, then adds valid data to task_data.\n
        :param preformatted_task_data: A list of strings to be processed.
        :param snip_words: A list of prefixes or suffixes to be removed from each pipe.
        :return: A sorted list of unique task_data entries after processing.
        """
        import re

        task_data = set()
        for pipe in preformatted_task_data:
            pattern = "|".join(map(re.escape, snip_words))
            pipe = re.sub(pattern, "", pipe)
            if pipe:
                for task in self.tasks:
                    if task in pipe:
                        task_data.add(pipe)
        task_data = list(task_data)
        task_data.sort()
        return task_data

    def __len__(self):
        return len(list(self._task_data()))

    def __getitem__(self, index):
        return self._task_data()[index]

    def index(self, entry):
        return self._task_data().index(entry)

    async def clear(self):
        self._task_data = []
        self.notify("clear")
