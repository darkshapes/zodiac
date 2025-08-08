#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import List, Any, Set
from toga.sources import Source
from zodiac.providers.registry_entry import RegistryEntry

nfo = print

flatten_map: List[Any] = lambda nested, unpack: [element for iterative in getattr(nested, unpack)() for element in iterative]
flatten_map.__annotations__ = {"nested": List[str], "unpack": str}


class TaskStream(Source):
    def __init__(self) -> None:
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
            ("image", "image"): ["Img2Img", "Inpaint", "PAG", "Vision"],
            ("text", "text"): ["Text", "CasualLM", "SequenceClassification", "QuestionAnswering"],
        }
        self.all_tasks = set().union(*self.basic_tasks.values()).union(*self.exclusive_tasks.values())

    async def set_filter_type(self, mode_in: str = "image", mode_out: str = "image") -> None:
        """Filter class items by modality
        :param mode_in: Input modality operation, defaults to "image"
        :param mode_out: Output modality operation, defaults to "image"""

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

    async def filter_tasks(self, registry_entry: RegistryEntry) -> List[str]:
        """Processes preformatted task data by removing specified prefixes and keywords, then adds valid data to task_data.\n
        :param preformatted_task_data: A list of strings to be processed.
        :param snip_words: A list of prefixes or suffixes to be removed from each pipe.
        :return: A sorted list of unique task_data entries after processing."""
        import re

        if registry_entry.package == "mflux":
            return registry_entry.tasks
        task_names = registry_entry.tasks
        snip_words: Set[str] = {"Model", "PreTrained", "ForConditionalGeneration", "Pipeline", "For"}
        class_snippets = snip_words | self.all_tasks
        if task_names:
            for task_class in task_names:
                for snip in class_snippets:
                    subtracted_name = task_class.replace(snip, "")
                    snip_words.add(subtracted_name)
                task_data = set()
                for pipe in task_names:
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
