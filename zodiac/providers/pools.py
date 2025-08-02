#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Feed models to RegistryEntry class"""

# pylint:disable=protected-access, no-member
from typing import Any, Callable, Dict, List, Optional

from nnll.model_detect.identity import ModelIdentity

from zodiac.providers.constants import CUETYPE_CONFIG, MIR_DB, CueType, PkgType
from zodiac.providers.registry_entry import RegistryEntry

nfo = print


async def hub_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> list[RegistryEntry] | None:
    """Build a registry of models from the local Huggingface Hub cache\n
    :param mir_db: An existing instance of the MIR database
    :param api_data: Dictionary of service data pertaining to providers
    :param entries: Previous registry entries to append
    :return: A list of RegistryEntry elements, or None"""

    from huggingface_hub import CacheNotFound, HFCacheInfo, repocard, scan_cache_dir
    from huggingface_hub.errors import EntryNotFoundError, LocalEntryNotFoundError, OfflineModeIsEnabled
    from requests import HTTPError

    async def generate_cache_data() -> HFCacheInfo:
        try:
            cache_dir = scan_cache_dir()
        except CacheNotFound:
            nfo("Cache error")
            yield None, None
        for repo in cache_dir.repos:
            try:
                meta = repocard.RepoCard.load(repo.repo_id)
            except (LocalEntryNotFoundError, EntryNotFoundError, HTTPError, OfflineModeIsEnabled) as error_log:
                nfo(f"Pooling error: '{error_log}'")
                yield None, None
            yield repo, meta

    model_id = ModelIdentity()

    async for repo, meta in generate_cache_data():
        if repo:
            tags = []
            tokenizer = None
            pkg_type = None
            mir_tags = None
            base_model = meta.base_model if hasattr("meta", "base_model") else None

            if meta:
                if hasattr(meta, "tags"):
                    tags.extend(meta.tags)
                if hasattr(meta, "pipeline_tag"):
                    tags.append(meta.pipeline_tag)
                if hasattr(meta, "get"):
                    library_name: str = meta.get("library_name")
                    if library_name:
                        library_name = library_name.replace("-", "_")
                        if pkg_type := library_name.upper():
                            if hasattr(PkgType, pkg_type):
                                pkg_type = getattr(PkgType, pkg_type)
            tokenizer = await model_id.get_cache_path(file_name="tokenizer.json", repo_obj=repo)
            if mir_tags := await model_id.label_model(repo_id=repo.repo_id, base_model=base_model, cue_type=CueType.HUB.value[1]):
                nfo(mir_tags)
                for mir_entry in mir_tags:
                    entry = RegistryEntry.create_entry(
                        model=repo.repo_id,
                        size=repo.size_on_disk,
                        # path=model_path,
                        tags=tags,
                        mir=mir_entry,
                        mir_data=mir_db.database[mir_entry[0]][mir_entry[1]],
                        model_family=base_model,
                        cuetype=CueType.HUB,
                        package=pkg_type,
                        api_kwargs=api_data[CueType.HUB.value[1]],  # api_data based on package_name (diffusers/mlx_audio)
                        timestamp=int(repo.last_modified),
                        tokenizer=tokenizer,
                    )
                    entries.append(entry)
            else:
                entry = RegistryEntry.create_entry(
                    model=repo.repo_id,
                    size=repo.size_on_disk,
                    # path=model_path,
                    tags=tags,
                    mir=None,
                    mir_data=None,
                    model_family=base_model,
                    cuetype=CueType.HUB,
                    package=pkg_type,
                    api_kwargs=api_data[CueType.HUB.value[1]],  # api_data based on package_name (diffusers/mlx_audio)
                    timestamp=int(repo.last_modified),
                    tokenizer=tokenizer,
                )
                nfo(f"mir tag not found for {repo.repo_id}") if not mir_tags else nfo(mir_tags)
                entries.append(entry)
    return entries


async def ollama_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> list[RegistryEntry] | None:
    """Build a registry of models from local Ollama service\n
    :param mir_db: An existing instance of the MIR database
    :param api_data: Dictionary of service data pertaining to providers
    :param entries: Previous registry entries to append
    :return: A list of RegistryEntry elements, or None"""

    async def generate_cache_data() -> tuple:
        from ollama import ListResponse, show, list as ollama_list

        cache_dir: ListResponse = ollama_list()
        for model in cache_dir.models:
            gguf_data = show(model.model)
            yield model, gguf_data

    mir_data = None
    model_id = ModelIdentity()
    entries = [] if not entries else entries
    config = api_data[CueType.OLLAMA.value[1]]
    async for model, gguf_data in generate_cache_data():
        base_model = gguf_data.modelinfo.get("general.architecture")
        gguf_data = (gguf_data.modelfile,)
        if hasattr(model, "family") and model.details.family != base_model:
            base_model = model.details.family
        if mir_tag := await model_id.label_model(repo_id=model.model, base_model=base_model, cue_type=CueType.OLLAMA.value[1], repo_obj=gguf_data):
            mir_tag = mir_tag[0]
            mir_data = mir_db.database[mir_tag[0]][mir_tag[1]]
        nfo(f"no tag for {model.model}") if not mir_tag else nfo(f"{mir_tag}")
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.OLLAMA.value[1]].get('prefix')}{model.model}",
            size=model.size.real,
            tags=[model.details.family],
            mir=mir_tag,
            mir_data=mir_data,
            model_family=[base_model],
            cuetype=CueType.OLLAMA,
            package=PkgType.LLAMA,
            api_kwargs=config["api_kwargs"],
            timestamp=int(model.modified_at.timestamp()),
            tokenizer=None,
        )
        entries.append(entry)
    return entries


async def vllm_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> list[RegistryEntry] | None:
    """Build a registry of models from local VLLM service\n
    :param mir_db: An existing instance of the MIR database
    :param api_data: Dictionary of service data pertaining to providers
    :param entries: Previous registry entries to append
    :return: A list of RegistryEntry elements, or None"""

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
            if mir_tag := await model_id.label_model(id_name, None, CueType.VLLM.value[1]):
                mir_tag = mir_tag[0]
                mir_data = mir_db.database[mir_tag[0]][mir_tag[1]]
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.VLLM.value[1]].get('prefix')}{id_name}",
            size=model._data.size_bytes,
            tags=["text"],
            mir=mir_tag,
            mir_data=mir_data,
            cuetype=CueType.VLLM,
            api_kwargs={**config["api_kwargs"]},
            timestamp=int(model.modified_at.timestamp()),
        )
        entries.append(entry)
    return entries


async def llamafile_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> list[RegistryEntry] | None:
    """Build a registry of models from a local Llamafile server\n
    :param mir_db: An existing instance of the MIR database
    :param api_data: Dictionary of service data pertaining to providers
    :param entries: Previous registry entries to append
    :return: A list of RegistryEntry elements, or None"""
    from openai import OpenAI

    mir_data = None
    mir_tag = None
    model_id = ModelIdentity()
    entries = [] if not entries else entries
    cache_dir: OpenAI = OpenAI(base_url=api_data["LLAMAFILE"]["api_kwargs"]["api_base"], api_key="sk-no-key-required")
    config = api_data[CueType.LLAMAFILE.value[1]]
    for model in cache_dir.models.list().data:
        if hasattr(model, id):
            if mir_tag := await model_id.label_model(model.id, CueType.LLAMAFILE.value[1]):
                mir_tag = mir_tag[0]
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


async def lm_studio_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> list[RegistryEntry] | None:
    """Build a registry of models from local LM Studio service\n
    :param mir_db: An existing instance of the MIR database
    :param api_data: Dictionary of service data pertaining to providers
    :param entries: Previous registry entries to append
    :return: A list of RegistryEntry elements, or None"""

    from lmstudio import LMStudioClient

    model_id = ModelIdentity()
    entries = [] if not entries else entries
    client = LMStudioClient()
    models = client.list_models()
    config = api_data[CueType.LM_STUDIO.value[1]]
    for model in models:
        tags = []
        if hasattr(model, "vision"):
            tags.extend(["vision", model.vision])
        if hasattr(model, "tool_use"):
            tags.append(["tool", model.tool_use])
        mir_data = None
        mir_tag = None
        if hasattr(model, "architecture"):
            if mir_tag := await model_id.label_model(model.architecture, None, CueType.LM_STUDIO.value[1]):
                mir_tag = mir_tag[0]
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


async def register_models(data: Optional[Dict[str, Any]] = None) -> list[RegistryEntry] | None:
    """Retrieve models from ollama server, local huggingface hub cache, local lmstudio cache & vllm.\n
    我們不應該繼續為LMStudio編碼。 歡迎貢獻者來改進它。 LMStudio is not OSS, but contributions are welcome."""

    @CUETYPE_CONFIG.decorator
    async def read_cuetype(data: Optional[Dict[str, Any]] = None) -> dict:
        return data

    if not data:
        data = await read_cuetype()

    async def entry_generator():
        entry_map = {
            CueType.HUB.value: hub_pool,
            CueType.OLLAMA.value: ollama_pool,
            CueType.LLAMAFILE.value: llamafile_pool,
            CueType.VLLM.value: vllm_pool,
            CueType.LM_STUDIO.value: lm_studio_pool,
        }
        for cue_type, pool in entry_map.items():
            yield cue_type, pool

    entries = []
    async for cue_type, provider in entry_generator():
        if cue_type[0]:
            api_data = data
            entries = await provider(api_data=api_data, mir_db=MIR_DB, entries=entries)

    return sorted(entries, key=lambda x: x.timestamp, reverse=True)


def generate_pool():
    import asyncio
    from time import perf_counter
    from nnll.monitor.console import nfo

    start = perf_counter()
    models = asyncio.run(register_models())
    nfo(f'Complete. Time: {perf_counter() - start}"')
    return models


if __name__ == "__main__":
    import asyncio

    models = asyncio.run(register_models())
    nfo(models)
