#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Register model types"""

# pylint: disable=line-too-long, import-outside-toplevel, protected-access, unsubscriptable-object

from pathlib import Path
from typing import List, Optional, Tuple, Union, Iterable

from nnll.monitor.file import dbuq
from pydantic import BaseModel, computed_field

from zodiac.providers.constants import VALID_CONVERSIONS, VALID_TASKS, CueType, PkgType


class RegistryEntry(BaseModel):
    """Validate Hub / Ollama / LMStudio model input"""

    cuetype: CueType

    model: str
    size: int
    tags: List[str]
    timestamp: int
    api_kwargs: Optional[dict] = None
    keys: Iterable = (None,)
    mir: Optional[List[str]] = None
    model_family: Optional[List[str]] = None
    modules: Optional[dict[str, dict]] = None
    package: Optional[Union[PkgType, CueType]] = None
    path: Optional[str] = None
    pipe: Optional[dict[str, Union[List[List[str]], List[str], str]]] = (None,)
    tasks: Optional[List[Union[str, List[str]]]] = (None,)
    tokenizer: Optional[Path] = None

    @computed_field
    @property
    def available_tasks(self) -> List[Tuple]:
        """Filter tag tasks into edge coordinates for graphing"""
        # This is a best effort at parsing tags; it is not perfect, and there is room for improvement
        # particularly: Tokenizers, being locatable here, should be assigned to their model entry
        # the logistics of how this occurs have been difficult to implement
        # additionally, tag recognition of tasks needs cleaner, which requires practical testing to solve
        import re

        default_task = None
        processed_tasks = []
        dbuq(self.model)
        if self.mir:
            arch = self.mir[0].split(".")[1]
            if arch in ["detr", "vit"]:
                processed_tasks = [("image", "text")]
            elif arch in ["controlnet", "unet", "dit"]:
                processed_tasks = [("text", "image")]
                processed_tasks = [("image", "image")]
        if self.cuetype in [x for x in list(CueType) if x != CueType.HUB]:  # Literal list of CueType, must use list()
            default_task = ("text", "text")  # usually these are txt gen libraries
        elif self.cuetype == CueType.HUB:
            dbuq(self.cuetype)  # pair tags from the hub such 'x-to-y' such as 'text-to-text' etc
            pattern = re.compile(r"(\w+)-to-(\w+)")
            for tag in self.tags:
                match = pattern.search(tag)
                if match and all(group in VALID_CONVERSIONS for group in match.groups()) and (match.group(1), match.group(2)) not in processed_tasks:
                    processed_tasks.append((match.group(1), match.group(2)))
        for tag in self.tags:  # when pair-tagged elements are not available, potential to duplicate HUB tags here
            for (graph_src, graph_dest), tags in VALID_TASKS[self.cuetype].items():
                if tag in tags and (graph_src, graph_dest) not in processed_tasks:
                    processed_tasks.append((graph_src, graph_dest))
        if default_task and default_task not in processed_tasks:
            processed_tasks.append(default_task)
        return processed_tasks

    @classmethod
    def create_entry(
        cls,
        cuetype: CueType,
        model: str,
        size: int,
        tags: List[str],
        api_kwargs: dict = None,
        keys: type[dict.keys] = None,
        mir: Optional[List[str]] = None,
        model_family: Optional[List[str]] = None,
        modules: Optional[dict[str, dict]] = None,
        package: Optional[Union[PkgType, CueType]] = None,
        path: Optional[str] = None,
        pipe: Optional[dict[str, Union[List[List[str]], List[str], str]]] = None,
        tasks: Optional[List[Union[str, List[str]]]] = None,
        timestamp: Optional[int] = None,
        tokenizer=Optional[str],
    ):
        """API specific data to call models\n
        :param cuetype: Provider to trigger loading
        :param model:Cache location for model
        :param size: File size (usually in bytes)
        :param tags: List of available machine tasks for model
        :param api_kwargs: Localhost server defaults, defaults to None
        :param keys: List of available data buckets inside the MIR tree, defaults to None
        :param mir: MIR information, defaults to None
        :param model_family: Compatibility information for the model, defaults to None
        :param modules: List of packages that can support the model, defaults to None
        :param path: Location of the model on disk, defaults to None
        :param pipe: List of components to build the execution for the model, defaults to None
        :param package: Package name and availability, defaults to None
        :param tasks: Available methods to run the model
        :param timestamp: Download time of model, defaults to None
        :param tokenizer: Tokenizer configuration location, defaults to None
        :return: An instance of RegistryEntry with the provided values
        """
        from datetime import datetime

        entry = cls(
            api_kwargs=api_kwargs,
            cuetype=cuetype,
            keys=keys,
            mir=mir,
            model_family=model_family,
            model=model,
            modules=modules,
            package=package,
            path=path,
            pipe=pipe,
            size=size,
            tags=tags,
            tasks=tasks,
            timestamp=timestamp or int(datetime.now().timestamp()),  # Default to current time if not provided
            tokenizer=tokenizer,
        )
        dbuq(entry)
        return entry
