#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Feed models to RegistryEntry class"""

# pylint:disable=protected-access, no-member
import asyncio
from typing import List, Dict, Optional, Any, Callable
from nnll.monitor.file import dbuq, debug_monitor
from zodiac.providers.registry_entry import RegistryEntry
from zodiac.providers.constants import CUETYPE_CONFIG, MIR_DB, CueType, PkgType


@debug_monitor
def hub_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:  # pylint:disable=unused-argument
    """Collect models from huggingface_hub\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from requests import HTTPError
    from huggingface_hub import scan_cache_dir, repocard, HFCacheInfo, CacheNotFound
    from huggingface_hub.errors import EntryNotFoundError, LocalEntryNotFoundError, OfflineModeIsEnabled

    try:
        model_data: HFCacheInfo = scan_cache_dir()
    except CacheNotFound:
        pass
    else:
        for repo in model_data.repos:
            meta = {}
            tags = []
            package_name = None
            mir_entry = None
            tokenizer = None
            mir_entry = mir_db.find_path("repo", repo.repo_id.lower())
            try:
                meta = repocard.RepoCard.load(repo.repo_id).data
            except (LocalEntryNotFoundError, EntryNotFoundError, HTTPError, OfflineModeIsEnabled):
                pass
            if meta:
                if hasattr(meta, "tags"):
                    tags.extend(meta.tags)
                if hasattr(meta, "pipeline_tag"):
                    tags.append(meta.pipeline_tag)
                test_package: str = meta.get("library_name")
                if test_package:
                    test_package = test_package.replace("-", "_")
                    test_package.upper()
                    if hasattr(PkgType, test_package.upper()):
                        package_name = getattr(PkgType, test_package.upper())
            if not package_name:
                try:
                    series = mir_entry[0]
                    compatibility = mir_entry[1]
                    module_name = mir_db.database.get(series)
                    if module_name:
                        sub_module_name = module_name.get(compatibility)
                        if sub_module_name:
                            pkg_num = sub_module_name.get("pkg")
                            if pkg_num:
                                pkg_id = next(iter(list(pkg_num.get(0, "diffusers"))))
                                if hasattr(PkgType, pkg_id.upper()):
                                    package_name = getattr(PkgType, pkg_id.get.upper())
                except (TypeError, KeyError, ValueError):
                    pass
            if hasattr(repo, "revisions") and repo.revisions:
                tokenizer_models = [info.file_path for info in next(iter(repo.revisions)).files if "tokenizer.json" in str(info.file_path)]
                tokenizer = tokenizer_models[-1] if tokenizer_models else None

            entry = RegistryEntry.create_entry(
                model=repo.repo_id,
                size=repo.size_on_disk,
                tags=tags,
                cuetype=CueType.HUB,
                mir=mir_entry,
                package=package_name,
                api_kwargs=None,  # api_data based on package_name (diffusers/mlx_audio)
                timestamp=int(repo.last_modified),
                tokenizer=tokenizer,
            )
            entries.append(entry)
        return entries


@debug_monitor
def ollama_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:
    """Collect models from Ollama\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from ollama import ListResponse, list as ollama_list

    config = api_data[CueType.OLLAMA.value[1]]
    model_data: ListResponse = ollama_list()
    for model in model_data.models:
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.OLLAMA.value[1]].get('prefix')}{model.model}",
            size=model.size.real,
            tags=[model.details.family],
            cuetype=CueType.OLLAMA,
            mir=[series for series, compatibility in mir_db.database.items() if model.details.family in str(compatibility)],
            package=CueType.OLLAMA,
            api_kwargs={**config["api_kwargs"]},
            timestamp=int(model.modified_at.timestamp()),
            tokenizer=model.model,
        )
        entries.append(entry)
    return entries


@debug_monitor
def cortex_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:  # pylint:disable=unused-argument
    """Collect models from Cortex\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    import requests

    config = api_data[CueType.CORTEX.value[1]]
    response: requests.models.Request = requests.get(api_data["CORTEX"]["api_kwargs"]["api_base"], timeout=(3, 3))
    model_data = response.json()
    for model in model_data["data"]:
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.CORTEX.value[1]].get('prefix')}/{model.get('model')}",
            size=model.get("size", 0),
            tags=[str(model.get("modalities", "text"))],
            cuetype=CueType.CORTEX,
            mir=None,
            package=None,
            api_kwargs={**config["api_kwargs"]},
        )
        entries.append(entry)
    return entries


@debug_monitor
def llamafile_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:  # pylint:disable=unused-argument
    """Collect models from Llamafile\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from openai import OpenAI

    model_data: OpenAI = OpenAI(base_url=api_data["LLAMAFILE"]["api_kwargs"]["api_base"], api_key="sk-no-key-required")
    config = api_data[CueType.LLAMAFILE.value[1]]
    for model in model_data.models.list().data:
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.LLAMAFILE.value[1]].get('prefix')}/{model.id}",
            size=0,
            tags=["text"],
            cuetype=CueType.LLAMAFILE,
            mir=None,
            package=None,
            api_kwargs={**config["api_kwargs"]},
            timestamp=int(model.created),
        )
        entries.append(entry)
    return entries


@debug_monitor
def vllm_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:  # pylint:disable=unused-argument
    """Collect models from VLLM\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from openai import OpenAI

    config = api_data[CueType.VLLM.value[1]]
    model_data = OpenAI(base_url=api_data["VLLM"]["api_kwargs"]["api_base"], api_key=api_data["VLLM"]["api_kwargs"]["api_key"])
    for model in model_data.models.list().data:
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.VLLM.value[1]].get('prefix')}{model['data'].get('id')}f",
            size=0,
            tags=["text"],
            cuetype=CueType.VLLM,
            mir=None,
            package=None,
            api_kwargs={**config["api_kwargs"]},
            timestamp=int(model.created),
        )
        entries.append(entry)
    return entries


@debug_monitor
def lm_studio_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:  # pylint:disable=unused-argument
    """Collect models from LM STUDIO\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from lmstudio import list_downloaded_models

    config = api_data[CueType.LM_STUDIO.value[1]]
    model_data = list_downloaded_models()
    for model in model_data:
        tags = []
        if hasattr(model._data, "vision"):
            tags.extend("vision", model._data.vision)
        if hasattr(model._data, "trained_for_tool_use"):
            tags.append(("tool", model._data.trained_for_tool_use))

        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.LM_STUDIO.value[1]].get('prefix')}{model.model_key}",
            size=model._data.size_bytes,
            tags=tags,
            cuetype=CueType.LM_STUDIO,
            mir=None,
            package=None,
            api_kwargs={**config["api_kwargs"]},
            timestamp=int(model.modified_at.timestamp()),
        )
        entries.append(entry)
    return entries


@CUETYPE_CONFIG.decorator
def register_models(data: Optional[Dict[str, Any]] = None) -> List[RegistryEntry]:
    """
    Retrieve models from ollama server, local huggingface hub cache, local lmstudio cache & vllm.
    我們不應該繼續為LMStudio編碼。 歡迎貢獻者來改進它。 LMStudio is not OSS, but contributions are welcome.
    """

    entries = []
    entry_map = {
        CueType.HUB.value: hub_pool,
        CueType.OLLAMA.value: ollama_pool,
        CueType.CORTEX.value: cortex_pool,
        CueType.LLAMAFILE.value: llamafile_pool,
        CueType.VLLM.value: vllm_pool,
        CueType.LM_STUDIO.value: lm_studio_pool,
    }
    for cue_type, provider in entry_map.items():
        print(cue_type, provider)
        if cue_type[0]:
            api_data = data
            entries = provider(api_data=api_data, mir_db=MIR_DB, entries=entries)
            dbuq(entries)

    return sorted(entries, key=lambda x: x.timestamp, reverse=True)
