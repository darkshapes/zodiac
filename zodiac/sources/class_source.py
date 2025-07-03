#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

import sys
from typing import List, Tuple, Callable, Union
from mir.mappers import make_callable
from zodiac.providers.constants import PkgType
from zodiac.providers.registry_entry import RegistryEntry
from zodiac.providers.constants import MIR_DB, ChipType


async def find_package(entry: RegistryEntry) -> Tuple[str]:
    """Look up class and package in MIR from RegistryEntry.\n
    :param entry: A RegistryEntry object containing MIR (Model Identifier Resource) details.
    :return: A tuple containing the class name of the package and its type if found; otherwise, None.
    :raises: AttributeError: If PkgType or ChipType classes are not properly defined."""

    model_data = MIR_DB.database[entry.mir[0]][entry.mir[1]].get("pkg")
    if model_data:
        main_gpu: List[str] = next(iter(ChipType._show_ready()))
        gpu_packages = getattr(ChipType, main_gpu)[2]
        cpu_packages = ChipType.CPU[2]
        if cpu_packages != gpu_packages:
            package_sets = [gpu_packages, cpu_packages]
        else:
            package_sets = [cpu_packages]  # Fallback to CPU packages if no match found in GPU packages
        for processor in package_sets:
            for package_type in processor:
                if package_type.value[0]:  # Determine if the package is available
                    package_name = package_type.value[1].lower()  # is
                    for index, data in model_data.items():
                        if package_name in data:
                            class_name = model_data[index][package_name]
                            return (class_name, package_type)


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


async def show_transformer_tasks(class_name: str) -> List[str]:
    """Retrieves a list of task classes associated with a specified transformer class.\n
    :param class_name: The name of the transformer class to inspect.
    :param pkg_type: The dependency for the module
    :return: A list of task classes associated with the specified transformer.
    """
    class_obj: Callable = make_callable(class_name, PkgType.TRANSFORMERS.value[1].lower())
    class_module: Callable = make_callable(*class_obj.__module__.split(".", 1)[-1:], class_obj.__module__.split(".", 1)[0])
    task_classes = getattr(class_module, "__all__")
    return task_classes


# from mir.mappers import make_callable
# from zodiac.providers.constants import MIR_DB
# from zodiac.class_source import lookup_package
# from zodiac.class_source import trace_class

# model_data = lookup_package(entry)
# package_data = [content for content in model_data.get("pkg").values() if next(iter(content)) in ["diffusers", "transformers"]]
# class_data = trace_class(make_callable(package_data[0], "diffusers"))
# # [terminal_gen(data[3],getattr(PkgType,data[0].upper())) for data in class_data]
