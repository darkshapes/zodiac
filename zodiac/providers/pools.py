#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Feed models to RegistryEntry class"""

# pylint:disable=protected-access, no-member
from typing import Any, Callable, Dict, List, Optional

from nnll.model_detect.identity import ModelIdentity
from nnll.mir.json_cache import MODES_PATH_NAMED, JSONCache
from zodiac.providers.constants import CUETYPE_CONFIG, MIR_DB, CueType, PkgType, VALID_TASKS
from zodiac.providers.registry_entry import RegistryEntry
from nnll.monitor.file import dbuq

nfo = print

MODE_DATA = JSONCache(MODES_PATH_NAMED)


@MODE_DATA.decorator
async def add_mode_types(mir_tag: list[str], data: dict | None = None) -> dict[str, list[str] | str]:
    """Add mode‑related metadata for a given MIR tag.\n
    :param mir_tag: List of tag components that identify a model in the MIR database.
    :param data: Dictionary containing MIR entries; defaults to ``None``.
    :returns: Mapping with keys extracted from ``data`` for the fused tag."""

    fused_tag = ".".join(mir_tag)

    mir_details = {
        "mode": data.get(fused_tag, {}).get("pipeline_tag"),
        "pkg_type": data.get(fused_tag, {}).get("library_type"),
        "tags": data.get(fused_tag, {}).get("tags"),
    }
    return mir_details


async def add_pkg_types(pkg_data: dict, mode: str, mir_tag: list[str]) -> dict[int | str, Any]:
    """Augment package data with additional entries based on pipeline class and mode.\n
    :param pkg_data: Existing package mapping where keys are indices and values are package specs.
    :param mode: The pipeline mode extracted from MIR metadata.
    :returns: Updated ``pkg_data`` with GPU-specific packages"""
    package_name = pkg_data.get(next(iter(pkg_data)))
    class_name = package_name.get(next(iter(package_name)))
    class_name = list(class_name)[0]
    if class_name == "FluxPipeline" and PkgType.MFLUX.value[0]:
        alias = "schnell" if "schnell" in mir_tag[0] else "dev"
        class_data = {
            f"{PkgType.MFLUX.value[1].lower()}": {"flux.flux.Flux1": {"alias": alias}},
        }
        pkg_data.setdefault(len(pkg_data), class_data)
    if class_name == "ChromaPipeline" and PkgType.MLX_CHROMA.value[0]:
        pkg_data.setdefault(len(pkg_data), {PkgType.MLX_CHROMA.value[1].lower(): "ChromaPipeline"})
    if mode in VALID_TASKS[CueType.HUB][("text", "text")] and PkgType.MLX_LM.value[0]:
        pkg_data.setdefault(len(pkg_data), {PkgType.MLX_LM.value[1].lower(): "load"})
    if mode in VALID_TASKS[CueType.HUB][("image", "text")] and PkgType.MLX_VLM.value[0]:
        pkg_data.setdefault(len(pkg_data), {PkgType.MLX_LM.value[1].lower(): "load"})
    return pkg_data


async def generate_entry(mir_tag: List[str], mir_db: dict, model_tags: list[str] | None = None, pkg_data: dict | None = None) -> dict[str, list[str] | str]:
    """Create a registry entry dictionary from MIR information.\n
    :param mir_tag: The hierarchical tag identifying a model in the MIR database.
    :param mir_db: The MIR database instance providing access to stored metadata.
    :param model_tags:  Additional tags to attach to the model; defaults to ``None``.
    :param pkg_data: Existing package data; defaults to ``None``.
    :returns: Mapping of values for registry construction."""
    from zodiac.streams.class_stream import ancestor_data

    fused_tag = ".".join(mir_tag)
    mir_info = mir_db.database.get(mir_tag[0], {}).get(mir_tag[1])
    modalities = await add_mode_types(fused_tag)
    mode_data = modalities.get("mode")
    if tags := modalities.get("tags"):
        model_tags = tags if not model_tags else model_tags + tags
    if not mir_info:
        mir_info = {}
    else:
        pkg_data = mir_info.get("pkg")
        pkg_data: dict = await add_pkg_types(pkg_data, mode_data, mir_tag)
    pipe_data = mir_info.get("pipe_names")
    if not pipe_data:
        pipe_data: list[dict] = await ancestor_data(mir_tag, field_name="pipe_names")
        pipe_data: dict | None = next(iter(pipe_data), {})
    task_data = mir_info.get("tasks")
    if not task_data:
        task_data: list[dict] = await ancestor_data(mir_tag, field_name="tasks")
    entry_data = {
        "mir": mir_tag,
        "tasks": task_data,
        "modules": pkg_data,
        "pipe": pipe_data,
        "mode": mode_data,
        "tags": model_tags,
    }

    return entry_data


async def hub_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> list[RegistryEntry] | None:
    """Build a registry of models from the local Huggingface Hub cache\n
    :param mir_db: An existing instance of the MIR database
    :param api_data: Dictionary of service data pertaining to providers
    :param entries: Previous registry entries to append
    :return: A list of RegistryEntry elements, or None"""

    from huggingface_hub import CacheNotFound, repocard, scan_cache_dir
    from huggingface_hub.errors import EntryNotFoundError, LocalEntryNotFoundError, OfflineModeIsEnabled
    from requests import HTTPError

    entry_data = {}

    async def generate_cache_data() -> Any:
        try:
            cache_dir = scan_cache_dir()
        except CacheNotFound:
            nfo("Cache error")
            yield None, None
        else:
            for repo in cache_dir.repos:
                try:
                    card = repocard.RepoCard.load(repo.repo_id)
                except (LocalEntryNotFoundError, EntryNotFoundError, HTTPError, OfflineModeIsEnabled) as error_log:
                    nfo(f"Pooling error: '{error_log}'")
                    yield None, None
                yield repo, card

    model_id = ModelIdentity()

    async for repo, card in generate_cache_data():
        if repo:
            tags = []
            base_model = None
            tokenizer = None
            pkg_type = None
            mir_tags = None
            card_data = getattr(card, "data", None)
            if card_data:
                base_model = card_data.get("base_model")
                if isinstance(base_model, str):
                    base_model = [base_model]
                pipeline_tag = card_data.get("pipeline_tag")
                if tags:
                    tags.append(pipeline_tag)
                else:
                    tags = [pipeline_tag]
                if pkg_name := card_data.get("library_name"):
                    if hasattr(PkgType, pkg_name := pkg_name.replace("-", "_").upper()):
                        pkg_type = getattr(PkgType, pkg_name)
            tokenizer = await model_id.get_cache_path(file_name="tokenizer.json", repo_obj=repo)
            mir_tags = await model_id.label_model(
                repo_id=repo.repo_id,
                base_model=base_model if isinstance(base_model, str) or base_model is None else base_model[0],
                cue_type=CueType.HUB.value[1],
            )
            tags = card_data.get("tags", []) if card_data else None

            if mir_tags:
                if isinstance(mir_tags, list) and isinstance(mir_tags[0], list):
                    mir_bundle = mir_tags if len(mir_tags) > 1 else None
                    dbuq(mir_tags)
                    mir_tag = next(iter(mir_id for mir_id in mir_tags if any(arch for arch in [".dit.", "unet"] if arch in mir_id[0])), mir_tags[0])
                else:
                    mir_bundle = None
                    mir_tag = mir_tags
                base_model = base_model.append(mir_tag[0]) if base_model else [mir_tag[0]]
                entry_data = await generate_entry(mir_tag=mir_tag, mir_db=mir_db, model_tags=tags)
                entry_data.setdefault("bundle", mir_bundle)
            else:
                mir_tags = [[]]
                entry_data = {
                    "tags": [],
                }
            entry = RegistryEntry.create_entry(
                model=repo.repo_id,
                size=repo.size_on_disk,
                cuetype=CueType.HUB,
                package=pkg_type,
                model_family=base_model if base_model else [mir_tag[0]],
                path=str(repo.repo_path),
                api_kwargs=api_data[CueType.HUB.value[1]],  # api_data based on package_name (diffusers/mlx_audio)
                timestamp=int(repo.last_modified),
                tokenizer=tokenizer,
                **entry_data,
            )
            nfo(mir_tags or f"mir tag not found for {repo.repo_id}")
            entries.append(entry)
    return entries


async def ollama_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> list[RegistryEntry] | None:
    """Build a registry of models from local Ollama service\n
    :param mir_db: An existing instance of the MIR database
    :param api_data: Dictionary of service data pertaining to providers
    :param entries: Previous registry entries to append
    :return: A list of RegistryEntry elements, or None"""

    async def generate_cache_data() -> Any:
        from ollama import ListResponse, show, list as ollama_list

        cache_dir: ListResponse = ollama_list()
        if cache_dir:
            for model in cache_dir.models:
                gguf_data = show(model.model)
                yield model, gguf_data

    entry_data = {}
    model_id = ModelIdentity()
    entries = [] if not entries else entries
    config = api_data[CueType.OLLAMA.value[1]]
    async for model, gguf_data in generate_cache_data():
        base_model = gguf_data.modelinfo.get("general.architecture")
        gguf_data = (gguf_data.modelfile,)
        if hasattr(model, "family") and model.details.family != base_model:
            base_model = model.details.family
        if mir_tag := await model_id.label_model(repo_id=model.model, base_model=base_model, cue_type=CueType.OLLAMA.value[1], repo_obj=gguf_data):
            entry_data = await generate_entry(mir_tag=mir_tag[0], mir_db=mir_db, model_tags=[model.details.family])
        nfo(f"no tag for {model.model}") if not mir_tag else nfo(f"{mir_tag}")
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.OLLAMA.value[1]].get('prefix')}{model.model}",
            size=model.size.real,
            model_family=[base_model],
            cuetype=CueType.OLLAMA,
            package=PkgType.LLAMA,
            api_kwargs=config["api_kwargs"],
            timestamp=int(model.modified_at.timestamp()),
            tokenizer=None,
            **entry_data,
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

    entry_data = {}
    model_id = ModelIdentity()
    entries = [] if not entries else entries
    config = api_data[CueType.VLLM.value[1]]
    cache_dir = OpenAI(base_url=api_data["VLLM"]["api_kwargs"]["api_base"], api_key=api_data["VLLM"]["api_kwargs"]["api_key"])
    for model in cache_dir.models.list().data:
        id_name = model["data"].get("id")
        mir_tag = None
        if id_name:
            if mir_tag := await model_id.label_model(repo_id=id_name, base_model=None, cue_type=CueType.VLLM.value[1]):
                entry_data = await generate_entry(mir_tag=mir_tag[0], mir_db=mir_db, tags=["text"])
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.VLLM.value[1]].get('prefix')}{id_name}",
            size=model._data.size_bytes,
            cuetype=CueType.VLLM,
            api_kwargs={**config["api_kwargs"]},
            timestamp=int(model.modified_at.timestamp()),
            **entry_data,
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

    entry_data = {}
    mir_tag = None
    model_id = ModelIdentity()
    entries = [] if not entries else entries
    cache_dir: OpenAI = OpenAI(base_url=api_data["LLAMAFILE"]["api_kwargs"]["api_base"], api_key="sk-no-key-required")
    config = api_data[CueType.LLAMAFILE.value[1]]
    for model in cache_dir.models.list().data:
        if hasattr(model, id):
            if mir_tag := await model_id.label_model(model.id, CueType.LLAMAFILE.value[1]):
                entry_data = await generate_entry(mir_tag=mir_tag[0], mir_db=mir_db, tags=["text"])
        entry = RegistryEntry.create_entry(model=f"{api_data[CueType.LLAMAFILE.value[1]].get('prefix')}{model.id}", size=0, cuetype=CueType.LLAMAFILE, api_kwargs=config["api_kwargs"], timestamp=int(model.created), **entry_data)
        entries.append(entry)
    return entries


async def lm_studio_pool(mir_db: Callable, api_data: Dict[str, Any], entries: List[RegistryEntry]) -> list[RegistryEntry] | None:
    """Build a registry of models from local LM Studio service\n
    :param mir_db: An existing instance of the MIR database
    :param api_data: Dictionary of service data pertaining to providers
    :param entries: Previous registry entries to append
    :return: A list of RegistryEntry elements, or None"""

    from lmstudio import LMStudioClient

    entry_data = {}
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
        mir_tag = None
        if hasattr(model, "architecture"):
            if mir_tag := await model_id.label_model(model.architecture, None, CueType.LM_STUDIO.value[1]):
                entry_data = await generate_entry(mir_tag=mir_tag[0], mir_db=mir_db, tags=tags)
        entry = RegistryEntry.create_entry(
            model=f"{api_data[CueType.LM_STUDIO.value[1]].get('prefix')}{model.model_key}",
            size=model._data.size_bytes,
            cuetype=CueType.LM_STUDIO,
            api_kwargs={**config["api_kwargs"]},
            timestamp=int(model.modified_at.timestamp()),
            **entry_data,
        )
        entries.append(entry)
    return entries


async def register_models(data: Optional[Dict[str, Any]] = None) -> list[RegistryEntry] | None:
    """Retrieve models from ollama server, local huggingface hub cache, local lmstudio cache & vllm.\n
    :param: data: Testing -  Override for API CueType data dictionary
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
    nfo(f'Complete. Time: {perf_counter() - start}" Registered: {len(models)}')
    return models


if __name__ == "__main__":
    import asyncio
    from nnll.monitor.file import dbuq

    models = asyncio.run(register_models())
    dbuq(models)
    from pprint import pprint

    pprint(models)
