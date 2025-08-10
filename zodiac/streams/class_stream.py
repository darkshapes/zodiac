#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import List, Tuple, Callable, Union
from zodiac.providers.registry_entry import RegistryEntry
from zodiac.providers.constants import MIR_DB, VERSIONS_CONFIG, ChipType


async def best_package(mir_db_pkg: dict, ready_pkg_types: list[str]) -> tuple[str]:
    """Identify the best package based on model data and package sets.\n
    :param mir_db_pkg: Dictionary containing package data to match
    :param ready_pkg_types: List of priority package processors to evaluate
    :return: Tuple containing (class name, package type) if match found, otherwise None"""
    for processor in ready_pkg_types:
        for pkg_type in processor:
            if pkg_type.value[0]:  # Determine if the package is available
                package_name = pkg_type.value[1].lower()
                for index, data in mir_db_pkg.items():
                    if package_name in data:
                        class_name = mir_db_pkg[index][package_name]
                        return (class_name, pkg_type)


async def find_package(entry: RegistryEntry = None, base: bool = False, mir_entry: list[str] | None = None) -> Tuple[str]:
    """Look up class and package in MIR from RegistryEntry.\n
    :param entry: A RegistryEntry object containing MIR (Model Identifier Resource) details.
    :return: A tuple containing the class name of the package and its type if found; otherwise, None.
    :raises: AttributeError: If PkgType or ChipType classes are not properly defined."""
    import re

    mir_base = entry.mir[0] if not mir_entry else mir_entry[0]
    mir_comp = entry.mir[1] if not mir_entry else mir_entry[1]
    mir_ids = [mir_comp, "*"]
    suffixes = VERSIONS_CONFIG.get("suffixes")
    if suffixes:
        for compatibility, model_data in MIR_DB.database[mir_base].items():
            package_key = model_data.get("pkg")
            if package_key and (any(re.match(pattern, compatibility) for pattern in suffixes) or compatibility in mir_ids):
                main_gpu: List[str] = next(iter(ChipType._show_ready()))
                gpu_packages = getattr(ChipType, main_gpu)[2]
                cpu_packages = ChipType.CPU[2]
                if cpu_packages != gpu_packages:
                    package_sets = [gpu_packages, cpu_packages]
                else:
                    package_sets = [cpu_packages]  # Fallback to CPU packages if no match found in GPU packages
                package_data = await best_package(package_key, package_sets)
                if package_data:
                    return package_data
    return


async def stage_class(class_object: Callable) -> List[Tuple[Union[str, Callable]]]:
    """Returns a tuple of data for each sub-class of a module
    :param class_obj: The class item to inspect.
    ex:('diffusers', 'models.autoencoders.autoencoder_kl', 'AutoencoderKL', <class 'diffusers.models.autoencoders.autoencoder_kl.AutoencoderKL'>),"""
    import typing

    pipe_args = typing.get_type_hints(class_object.__init__).values()
    sub_classes = [
        (*pipe.__module__.split(".", 1), pipe.__name__, pipe)  #
        for pipe in pipe_args  #
        if "builtins" not in pipe.__module__ and "typing" not in pipe.__module__
    ]
    return sub_classes


# async def show_transformers_tasks(class_name: str) -> List[str]:
#     """Retrieves a list of task classes associated with a specified transformer class.\n
#     :param class_name: The name of the transformer class to inspect.
#     :param pkg_type: The dependency for the module
#     :return: A list of task classes associated with the specified transformer.
#     """
#     class_obj: Callable = make_callable(class_name, PkgType.TRANSFORMERS.value[1].lower())
#     class_module: Callable = make_callable(*class_obj.__module__.split(".", 1)[-1:], class_obj.__module__.split(".", 1)[0])
#     task_classes = getattr(class_module, "__all__")
#     return task_classes


# from mir.mappers import make_callable
# from zodiac.providers.constants import MIR_DB
# from zodiac.class_stream import lookup_package
# from zodiac.class_stream import trace_class

# model_data = lookup_package(entry)
# package_data = [content for content in model_data.get("pkg").values() if next(iter(content)) in ["diffusers", "transformers"]]
# class_data = trace_class(make_callable(package_data[0], "diffusers"))
# # [terminal_gen(data[3],getattr(PkgType,data[0].upper())) for data in class_data]
