#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import List, Tuple, Callable, Union, Any, Generator
from zodiac.providers.registry_entry import RegistryEntry
from zodiac.providers.constants import MIR_DB, VERSIONS_CONFIG, ChipType


async def ancestor_data(mir_tag_or_registry_entry: RegistryEntry | list, field_name: str = "pkg") -> Generator:
    """Trace lineage of a model for the specified field \n
    :param registry_entry: RegistryEntry for the model that needs to be traced
    :param field_name: The name of the database field containing the data sought
    :return: A generator populated with matching data fields"""
    mir_db = MIR_DB.database
    if isinstance(mir_tag_or_registry_entry, RegistryEntry):
        mir_prefix = mir_tag_or_registry_entry.mir[0]
    else:
        mir_prefix = mir_tag_or_registry_entry[0]
    base_fields = [
        "diffusers",
        "*",
    ]  # "prior"
    return [mir_db[mir_prefix][x].get(field_name) for x in base_fields if mir_db[mir_prefix].get(x, {}).get(field_name, {})]


async def best_package(pkg_data: RegistryEntry | dict[int | str, Any], ready_list: list[tuple[ChipType]] = ChipType._show_ready()) -> tuple[str]:
    """Identify the best package based on model data and package sets.\n
    :param mir_db_pkg: Dictionary containing package data to match
    :param ready_pkg_types: List of priority package processors to evaluate
    :return: Tuple containing (class name, package type) if match found, otherwise None"""

    if isinstance(pkg_data, RegistryEntry):
        pkg_loop: list = await ancestor_data(pkg_data)
        print(pkg_loop)
        pkg_loop.insert(0, pkg_data.modules | pkg_loop[0])

    else:
        pkg_loop = [pkg_data]  # normalize to list
    print(pkg_loop)
    for processor in ready_list:
        for pkg_type in processor[2]:
            if pkg_type.value[0]:  # Determine if the package is available
                package_name = pkg_type.value[1].lower()
                for index, data in next(iter(pkg_loop)).items():
                    if package_name in data:
                        class_name = data[package_name]
                        return (index, class_name, pkg_type)


async def find_package(entry: RegistryEntry = None, mir_entry: list[str] | None = None) -> Tuple[str]:
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
            if package_key and (any(re.match(pattern, compatibility) for pattern in suffixes) or compatibility in mir_ids):  # Fallback to CPU packages if no match found in GPU packages
                package_data = await best_package(package_key)
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
