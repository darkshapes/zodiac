#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Feed models to RegistryEntry class"""

# pylint:disable=protected-access, no-member
from typing import Any, Callable, Dict, List, Optional

from nnll.configure.constants import ExtensionType
from zodiac.providers.constants import CUETYPE_CONFIG, MIR_DB, CueType, PkgType
from zodiac.providers.identity import ModelIdentity
from zodiac.providers.registry_entry import RegistryEntry


def hub_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> List[RegistryEntry | None]:  # pylint:disable=unused-argument
    """Collect models from huggingface_hub\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: List of additional registry entries"""
    from huggingface_hub import CacheNotFound, HFCacheInfo, repocard, scan_cache_dir
    from huggingface_hub.errors import EntryNotFoundError, LocalEntryNotFoundError, OfflineModeIsEnabled
    from requests import HTTPError

    model_id = ModelIdentity()
    try:
        cache_dir: HFCacheInfo = scan_cache_dir()
    except CacheNotFound:
        print("Cache error")
        return entries
    for repo in cache_dir.repos:
        meta = {}
        tags = []
        model_path = None
        tokenizer = None
        pkg_type = None
        mir_data = None
        mir_tag = None
        try:
            meta = repocard.RepoCard.load(repo.repo_id).data
        except (LocalEntryNotFoundError, EntryNotFoundError, HTTPError, OfflineModeIsEnabled) as error_log:
            print(f"Pooling error: '{error_log}'")
            return entries
        base_model = meta.base_model if hasattr("meta", "base_model") else None
        try:
            mir_tag, mir_data = model_id.tag_model(repo.repo_id, base_model)
            print(mir_tag)
        except Exception as error_log:
            print(error_log)
        print(mir_tag)
        if meta:
            if hasattr(meta, "tags"):
                tags.extend(meta.tags)
            if hasattr(meta, "pipeline_tag"):
                tags.append(meta.pipeline_tag)
            library_name: str = meta.get("library_name")
            if library_name:
                library_name = library_name.replace("-", "_")
                pkg_type = library_name.upper()
        tokenizer = model_id.get_model_path(repo, "tokenizer.json")
        if pkg_type and hasattr(PkgType, pkg_type):
            pkg_type = getattr(PkgType, pkg_type)
        entry = RegistryEntry.create_entry(
            model=repo.repo_id,
            size=repo.size_on_disk,
            path=model_path,
            tags=tags,
            mir=mir_tag,
            mir_data=mir_data,
            model_family=base_model,
            cuetype=CueType.HUB,
            package=pkg_type,
            api_kwargs=api_data[CueType.HUB.value[1]],  # api_data based on package_name (diffusers/mlx_audio)
            timestamp=int(repo.last_modified),
            tokenizer=tokenizer,
        )
        entries.append(entry)
    return entries


def ollama_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:
    """Collect models from Ollama\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from ollama import ListResponse, show
    from ollama import list as ollama_list

    model_id = ModelIdentity()
    entries = [] if not entries else entries
    config = api_data[CueType.OLLAMA.value[1]]
    cache_dir: ListResponse = ollama_list()
    for model in cache_dir.models:
        gguf_data = show(model.model)
        gguf_arch = gguf_data.modelinfo.get("general.architecture")
        if hasattr(model, "family") and model.details.family != gguf_arch:
            gguf_arch = model.details.family
        mir_tag = None
        mir_data = None
        try:
            mir_tag, mir_data = model_id.tag_model(gguf_arch, model.model)
            print(mir_tag)
        except Exception as error_log:
            print(error_log)
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.OLLAMA.value[1]].get('prefix')}{model.model}",
            size=model.size.real,
            tags=[model.details.family],
            mir=mir_tag,
            mir_data=mir_data,
            model_family=[gguf_arch],
            cuetype=CueType.OLLAMA,
            package=CueType.OLLAMA,
            api_kwargs=config["api_kwargs"],
            timestamp=int(model.modified_at.timestamp()),
            tokenizer=None,
        )
        entries.append(entry)
    return entries


def llamafile_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:  # pylint:disable=unused-argument
    """Collect models from Llamafile\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from openai import OpenAI

    model_id = ModelIdentity()
    entries = [] if not entries else entries
    cache_dir: OpenAI = OpenAI(base_url=api_data["LLAMAFILE"]["api_kwargs"]["api_base"], api_key="sk-no-key-required")
    config = api_data[CueType.LLAMAFILE.value[1]]
    for model in cache_dir.models.list().data:
        if hasattr(model, id):
            mir_tag = model_id.tag_model(model.id)
        if mir_tag:
            mir_data = mir_db.database[mir_tag[0]][mir_tag[1]]
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.LLAMAFILE.value[1]].get('prefix')}{model.id}",
            size=0,
            tags=["text"],
            mir=mir_tag,
            mir_data=mir_data,
            cuetype=CueType.LLAMAFILE,
            api_kwargs=config["api_kwargs"],
            timestamp=int(model.created),
        )
        entries.append(entry)
    return entries


def vllm_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:  # pylint:disable=unused-argument
    """Collect models from VLLM\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from openai import OpenAI

    model_id = ModelIdentity()
    entries = [] if not entries else entries
    config = api_data[CueType.VLLM.value[1]]
    cache_dir = OpenAI(base_url=api_data["VLLM"]["api_kwargs"]["api_base"], api_key=api_data["VLLM"]["api_kwargs"]["api_key"])
    for model in cache_dir.models.list().data:
        id_name = model["data"].get("id")
        mir_data = None
        mir_tag = None
        if id_name:
            mir_tag = mir_tag = model_id.tag_model(id_name)
        if mir_tag:
            mir_data = mir_db.database[mir_tag[0]][mir_tag[1]]
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.VLLM.value[1]].get('prefix')}{id_name}",
            size=0,
            tags=["text"],
            mir=mir_tag,
            mir_data=mir_data,
            cuetype=CueType.VLLM,
            package=PkgType.VLLM,
            api_kwargs=config["api_kwargs"],
            timestamp=int(model.created),
        )
        entries.append(entry)
    return entries


def lm_studio_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> None:  # pylint:disable=unused-argument
    """Collect models from LM STUDIO\n
    :param mir_db: MIR information
    :param api_data: API information
    :param entries: Cumulative registry data
    :return: `dict` of additional registry entries"""
    from lmstudio import list_downloaded_models

    model_id = ModelIdentity()
    entries = [] if not entries else entries
    config = api_data[CueType.LM_STUDIO.value[1]]
    cache_dir = list_downloaded_models()
    for model in cache_dir:
        tags = []

        if hasattr(model._data, "vision"):
            tags.extend("vision", model._data.vision)
        if hasattr(model._data, "trained_for_tool_use"):
            tags.append(("tool", model._data.trained_for_tool_use))
        mir_data = None
        mir_tag = None
        if hasattr(model, "architecture"):
            mir_tag = mir_tag = model_id.tag_model(model.architecture)
        if mir_tag:
            mir_data = mir_db.database[mir_tag[0]][mir_tag[1]]
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.LM_STUDIO.value[1]].get('prefix')}{model.model_key}",
            size=model._data.size_bytes,
            tags=tags,
            mir=mir_tag,
            mir_data=mir_data,
            cuetype=CueType.LM_STUDIO,
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
        CueType.LLAMAFILE.value: llamafile_pool,
        CueType.VLLM.value: vllm_pool,
        CueType.LM_STUDIO.value: lm_studio_pool,
    }
    for cue_type, provider in entry_map.items():
        if cue_type[0]:
            api_data = data
            entries = provider(api_data=api_data, mir_db=MIR_DB, entries=entries)
            # dbuq(entries)
    print(entries)
    return sorted(entries, key=lambda x: x.timestamp, reverse=True)
