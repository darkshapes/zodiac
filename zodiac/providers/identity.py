# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

from typing import Callable

from nnll.configure.constants import PARAMETERS_SUFFIX, BREAKING_SUFFIX

from zodiac.providers.constants import MIR_DB, PkgType  # CueType,
from zodiac.streams.class_stream import find_package
import re
import os


class ModelIdentity:
    def __init__(self):
        self.mir_db = MIR_DB.database
        self.find_path = MIR_DB.find_path

    def tag_model(self, repo_id: str, base_model: str | None = None) -> tuple[dict | None]:
        """Retrieves model tags and associated data based on repository ID.\n
        :param repo_id: Unique identifier for the repository\n
        :param base_model: The original model source
        :return: Tuple containing (mir_tag, mir_data) if found, otherwise None"""

        from nnll.mir.tag import class_to_mir_tag
        from nnll.mir.tag import make_mir_tag

        print(repo_id)
        try:

            def check_for_tag_with(query: str) -> tuple[list[str], dict] | None:
                """Run check on the provided id segment
                :param query: Segment to check
                :return: A list containing the MIR series and compatibility and the dict of pkg data beneath it, or None"""

                query_trim = make_mir_tag(query)[0]  # re.sub(PARAMETERS_SUFFIX, "", query.lower())
                query_base: str = lambda repo_name: os.path.basename(repo_name)
                query_class: str = lambda code_name: f"{code_name.title().replace('-', '').replace('.', '').split(':')[0]}Model"
                query_text_class: str = lambda code_name: f"{code_name.title().replace('-', '').replace('.', '').split(':')[0]}TextModel"
                query_multimodal_class: str = lambda code_name: f"{code_name.title().replace('-', '').replace('.', '').split(':')[0]}MultimodalModel"

                try:
                    for field_name in ["repo", "pkg"]:
                        queries = [query, query_trim]

                        print(queries)
                        if r"/" in query:
                            queries.extend([query_base(item) for item in queries])
                        queries.extend([query_class(item) for item in queries])
                        queries.extend([item.title() for item in queries])
                        queries.extend([query_text_class(item) for item in queries])
                        queries.extend([query_multimodal_class(item) for item in queries])
                        for tag_item in queries:
                            if field_name != "pkg":
                                print(queries)
                                mir_tag = self.find_path(field=field_name, target=query.lower())
                                if mir_tag:
                                    return mir_tag
                            else:
                                print(tag_item)
                                mir_tag = class_to_mir_tag(MIR_DB, tag_item)
                                if mir_tag:
                                    return mir_tag
                                elif "Model" in tag_item:
                                    for series, comp in self.mir_db.items():
                                        for comp_name, mir_data in comp.items():
                                            if mir_data.get("pkg"):
                                                pkg_data = mir_data["pkg"]
                                                for i, class_data in pkg_data.items():
                                                    # if isinstance(class_data, list):
                                                    #     print(f"{series, comp_name, class_data, type(class_data)}")
                                                    if tag_item in class_data.values():
                                                        return [series, comp_name]

                except Exception as error_log:
                    print(error_log)

            maybe_matches = [repo_id]
            if base_model:
                base_title = str(base_model).title()
                maybe_matches.extend([base_model, base_title])
            for query in maybe_matches:
                mir_tag = check_for_tag_with(query)
                if mir_tag and (mir_data := self.mir_db[mir_tag[0]].get(mir_tag[1])):
                    return mir_tag, mir_data
                elif mir_tag:
                    return mir_tag, self.mir_db[mir_tag[0]].get("*")

            # print(f"Query '{repo_id}' not found when searched {len(self.mir_db)}'{base_model}' options\n")
            return None, None
        except Exception as error_log:
            print(error_log)

    def find_model_type(self, repo_data: Callable):
        """Identifies the model in a repository by searching specific model files and folders.\n
        :param repo_data: A function that provides repository data for model searching.
        :return: A tuple containing the tokenizer path and the detected model path."""
        import os
        from nnll.model_detect.layer_sums import sum_layers_of
        from nnll.integrity.hashing import compute_hash_for, compute_b3_for

        pkg_type = None
        mir_tag = None
        mir_data = None

        model_folders = ("unet" + os.sep, "unet.opt" + os.sep, "transformer" + os.sep, "transformer.opt", "dit_model", "dit_model.opt")
        model_files = (".gguf", ".onnx.", ".safetensors", "model-", ".fp16.", "diffusion_pytorch_model")
        search_types = (model_folders, model_files)

        for segment in search_types:
            for seg in segment:
                model_path = self.get_model_path(repo_data, seg)
                if model_path:
                    metadata = self.get_model_metadata(model_path)
                    if metadata:
                        pkg_type = self.get_pkg_from_metadata(metadata)
                        metadata.pop("__metadata__", metadata)
                        # layer_b3 = sum_layers_of(metadata, compute_b3_for)
                        # layer_256 = sum_layers_of(metadata, compute_hash_for)
                        # for layer in metadata.keys():
                        #     mir_tag = MIR_DB.find_path("identifiers", layer)
                        #     mir_data = self.mir_db[mir_tag[0]].get(mir_tag[1])
                        #     if mir_data:
                        #         return mir_tag, mir_data, pkg_type, metadata

                    return mir_tag, None, pkg_type  # , model_path) (tokenizer, pkg_type,

    def get_model_path(self, repo_data: Callable, query: str, match_attr: str | None = None, path_attr: str = "file_path"):
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

    def get_model_metadata(self, file_path_named: str):
        from nnll.metadata.model_tags import ReadModelTags

        reader = ReadModelTags()
        metadata = reader.attempt_all_open(file_path_named, separate_desc=False)
        if metadata:
            return metadata
        return None

    def get_pkg_from_metadata(self, metadata: dict):
        format = metadata.get("format")
        if format:
            if format == "pt":
                pkg_type = PkgType.DIFFUSERS
            elif format == "mlx":
                pkg_type = PkgType.MLX_LM
        if not format and metadata.get("mflux_version"):
            pkg_type = PkgType.MFLUX
        if not format and metadata.get("opset_import"):
            pkg_type = PkgType.ONNX
        return pkg_type


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
