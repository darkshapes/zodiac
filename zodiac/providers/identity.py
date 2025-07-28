# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

from typing import Callable

from nnll.metadata.model_tags import ReadModelTags
from zodiac.providers.constants import MIR_DB, PkgType  # CueType,
import os
from pathlib import Path
from nnll.configure.constants import ExtensionType


class ModelIdentity:
    def __init__(self):
        self.mir_db = MIR_DB.database
        self.find_path = MIR_DB.find_path
        self.reader = ReadModelTags()

    async def tag_model(self, repo_id: str, base_model: str | None = None) -> tuple[dict | None]:
        """Retrieves model tags and associated data based on repository ID.\n
        :param repo_id: Unique identifier for the repository\n
        :param base_model: The original model source
        :return: tuple containing (mir_tag, mir_data) if found, otherwise tuple of None"""
        from nnll.mir.tag import class_to_mir_tag
        from nnll.mir.tag import make_mir_tag

        async def check_for_tag_with(query: str) -> tuple[list[str], dict] | None:
            """Run check on the provided id segment
            :param query: Segment to check
            :return: A list containing the MIR series and compatibility and the dict of pkg data beneath it, or None"""

            query = query.lower()
            query_trim = make_mir_tag(query.lower())[0]  # re.sub(PARAMETERS_SUFFIX, "", query.lower())
            query_base: str = lambda repo_name: os.path.basename(repo_name)
            query_class: str = lambda code_name: f"{code_name.replace('-', '').replace('.', '').split(':')[0]}"

            for field_name in ["pkg", "repo"]:
                queries = [query, query_trim]

                if r"/" in query:
                    queries.extend([query_base(item) for item in queries])
                queries.extend([item.title() for item in queries])
                queries.extend([f"{query_class(item)}" for item in queries])
                queries.extend([f"{query_class(item)}Pipeline" for item in queries])
                queries.extend([f"{query_class(item)}Multimodal" for item in queries])
                queries.extend([f"{query_class(item)}Text" for item in queries])
                queries.extend([f"{query_class(item)}Model" for item in queries])

                for tag_item in queries:
                    if field_name != "pkg":
                        if mir_tag := self.find_path(field=field_name, target=tag_item.lower()):
                            return mir_tag
                    else:
                        if mir_tag := class_to_mir_tag(MIR_DB, tag_item):
                            return mir_tag
                        else:
                            for series, comp in self.mir_db.items():
                                for comp_name, mir_data in comp.items():
                                    if pkg_data := mir_data.get("pkg"):
                                        for _, class_data in pkg_data.items():
                                            if tag_item in class_data.values():
                                                mir_tag = [series, comp_name]
                                                return

        maybe_matches = [repo_id]
        if base_model:
            base_title = str(base_model).title()
            maybe_matches.extend([base_model, base_title])
        for query in maybe_matches:
            mir_tag = await check_for_tag_with(query)
            if mir_tag and (mir_data := self.mir_db[mir_tag[0]].get(mir_tag[1])):
                return mir_tag, mir_data
            elif mir_tag:
                return mir_tag, self.mir_db[mir_tag[0]].get("*")
        return None, None

    async def find_model_type(self, repo_data: Callable) -> tuple[PkgType | None]:
        """Identifies the model in a repository by searching specific model files and folders.\n
        :param repo_data: A function that provides repository data for model searching.
        :return: A tuple containing the model_tag and thee detected model PkgType."""
        import os
        from nnll.model_detect.layer_sums import sum_layers_of
        from nnll.integrity.hashing import compute_b3_for, compute_hash_for
        from nnll.model_detect.layer_pattern import ExtractAndMatchMetadata

        pkg_type = None
        mir_tag = None
        metadata = None
        model_folders = ("unet" + os.sep, "unet.opt" + os.sep, "transformer" + os.sep, "transformer.opt", "dit_model", "dit_model.opt")
        model_files = (*ExtensionType.MODEL, "model-", ".fp16.", "diffusion_pytorch_model", "model.")
        search_types = (model_folders, model_files)
        for segment in search_types:
            for seg in segment:
                model_path = await self.get_model_path(repo_data, seg)
                if model_path and not any(x in model_path.suffix for x in [*ExtensionType.MEDIA]):
                    original_path = model_path
                    model_path = str(model_path.resolve()) if model_path.is_symlink() else str(model_path)
                    metadata = await self.get_model_metadata(model_path)
                    if metadata:
                        pkg_type = PkgType.LLAMA if self.reader.gguf_check(model_path) else await self.get_pkg_from_model(metadata, original_path)
                        metadata.pop("__metadata__", metadata)
                        hash_fields: dict = {"layer_b3": compute_b3_for, "layer_256": compute_hash_for}
                        for field, compute_function in hash_fields.items():
                            layer_info = await sum_layers_of(metadata, compute_function)
                            if mir_tag := self.find_path(field=field, target=layer_info):
                                print(f" {mir_tag} {compute_function} find_path")
                                return mir_tag, pkg_type
                        file_hash = await compute_hash_for(file_path_named=str(model_path))
                        if mir_tag := self.find_path(field="file_256", target=file_hash):
                            return mir_tag, pkg_type
                        match = ExtractAndMatchMetadata()
                        tensor_count = len(metadata)
                        for layer in metadata.keys():
                            for series, comp in self.mir_db.items():
                                for comp_name, mir_data in comp.items():
                                    if identifiers := mir_data.get("identifiers"):
                                        layer_check = any(match.is_pattern_in_layer(block_pattern=item, layer_element=layer) for item in identifiers if isinstance(item, str))
                                        if layer_check and [isinstance(item, int) and item == tensor_count for item in identifiers]:
                                            mir_tag = [series, comp_name]
                                        elif layer_check and [not isinstance(item, int) for item in identifiers]:
                                            mir_tag = [series, comp_name]
                        return mir_tag, pkg_type

        return mir_tag, pkg_type

    async def get_model_path(self, repo_data: Callable, query: str, match_attr: str | None = None, path_attr: str = "file_path"):
        """Returns the file path from a repository based on a query.\n
        :param repo: Repository object with revisions and files information.
        :param query: String to search for within the repository files.
        :param match_attr: Attribute to match the query against, defaults to path_attr.
        :param path_attr: Attribute containing the file path, defaults to "file_path".
        :return: The matched file path or None if no match found."""

        if not match_attr:
            match_attr = path_attr
        if hasattr(repo_data, "revisions") and repo_data.revisions:
            file_path = [getattr(info, path_attr, []) for info in next(iter(repo_data.revisions)).files if query in str(getattr(info, match_attr, []))]
            if file_path:
                return file_path[-1]
        return None

    async def get_model_metadata(self, file_path_named: str):
        metadata = self.reader.attempt_all_open(file_path_named, separate_desc=False)
        if metadata:
            return metadata
        return None

    async def get_pkg_from_model(self, metadata: dict, path: Path | str = None) -> PkgType | None:
        """Determine the package type based on metadata.
        :param metadata: Dictionary containing model metadata
        :return: Corresponding PkgType enum or None if not identifiable"""
        if metadata.get("__metadata__"):
            format = metadata["__metadata__"].get("format")
            if format:
                if format == "pt":
                    return PkgType.DIFFUSERS
                elif format == "mlx":
                    return PkgType.MLX_LM
            if not format and metadata.get("mflux_version"):
                return PkgType.MFLUX
            if not format and metadata.get("opset_import"):
                return PkgType.ONNX
        else:
            if path:
                suffix_types = {
                    tuple(ExtensionType.ONNX): PkgType.ONNX,
                    tuple(ExtensionType.SAFE): PkgType.DIFFUSERS,
                    tuple(ExtensionType.PICK): PkgType.TORCH,
                }
                return suffix_types.get(path.suffix)
            return None


# test_package: str = meta.get("library_name")
# if test_package and not package_name:
#     test_package = test_package.replace("-", "_")
#     test_package.upper()
#     if hasattr(PkgType, test_package.upper()):
#         package_name = getattr(PkgType, test_package.upper())


# mir_family = None

# if hasattr("meta", "base_model"):
#     mir_family = mir_db.find_path("repo", meta.base_model)
# if mir_family:
#     sub_module_name = mir_db.database[mir_family[0]][mir_family[1]]
# elif mir_tag:
#     sub_module_name = mir_db.database[mir_tag[0]][mir_tag[1]]

# if meta:
#     if hasattr(meta, "tags"):
#         tags.extend(meta.tags)
#     if hasattr(meta, "pipeline_tag"):
#         tags.append(meta.pipeline_tag)
#     test_package: str = meta.get("library_name")
#     if test_package and not package_name:
#         test_package = test_package.replace("-", "_")
#         test_package.upper()
#         if hasattr(PkgType, test_package.upper()):
#             package_name = getattr(PkgType, test_package.upper())

# if hasattr(repo, "revisions") and repo.revisions:
#     tokenizers = [info.file_path for info in next(iter(repo.revisions)).files if "tokenizer.json" in str(info.file_path)]
#     if tokenizers:
#         tokenizer_path = tokenizers[-1]
#         tokenizer = tokenizer_path


# fundamentally everyone has a need for trust, just like everyone has a need to remember things, aided by a photograph.
