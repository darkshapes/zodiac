# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->


# pylint:disable=no-name-in-module

import os
from enum import Enum
from typing import Annotated, Callable, List, Optional, Union

from nnll.configure.init_gpu import first_available
from nnll.mir.json_cache import TEMPLATE_PATH_NAMED, VERSIONS_PATH_NAMED, JSONCache
from nnll.mir.maid import MIRDatabase
from nnll.monitor.file import dbuq
from pydantic import BaseModel, Field
from transformers.pipelines import PIPELINE_REGISTRY

MIR_DB = MIRDatabase()
CUETYPE_PATH_NAMED = os.path.join(os.path.dirname(__file__), "cuetype.json")
CUETYPE_CONFIG = JSONCache(CUETYPE_PATH_NAMED)
TEMPLATE_CONFIG = JSONCache(TEMPLATE_PATH_NAMED)
VERSIONS_DATA = JSONCache(VERSIONS_PATH_NAMED)
VERSIONS_DATA._load_cache()
VERSIONS_CONFIG = VERSIONS_DATA._cache


def check_host(api_name: str, api_url: str) -> bool:
    """Perform network test to ensure a host server is running\n
    :param api_name: Type of host API
    :param api_url: The (default) configuration data for that API
    :return: Whether the server is up or not
    """

    from json.decoder import JSONDecodeError

    import httpcore
    import httpx
    import requests
    from openai import APIConnectionError, APIStatusError, APITimeoutError  # , JSONDecodeError,
    from urllib3.exceptions import MaxRetryError, NewConnectionError

    if api_name == "LM_STUDIO":
        from lmstudio import APIConnectionError, APIStatusError, APITimeoutError, JSONDecodeError
    try:
        dbuq(api_url)
        request = requests.get(api_url, timeout=(1, 1))
        if request is not None:
            dbuq(vars(request))
            if hasattr(request, "status_code"):
                status = request.status_code
                dbuq(status)
            if (hasattr(request, "ok") and request.ok) or (hasattr(request, "reason") and request.reason == "OK"):
                dbuq(f"Available {api_name}")
                return True
            elif hasattr(request, "json"):
                status = request.json()
                if status.get("result") == "OK":
                    dbuq(f"Available {api_name}")
                    return True
            request.raise_for_status()
            requests.HTTPError()
    except (
        APIConnectionError,
        APITimeoutError,
        APIStatusError,
        requests.exceptions.InvalidURL,
        requests.exceptions.ConnectionError,
        requests.adapters.ConnectionError,
        requests.HTTPError,
        httpcore.ConnectError,
        httpx.ConnectError,
        ConnectionRefusedError,
        MaxRetryError,
        NewConnectionError,
        TimeoutError,
        JSONDecodeError,
        OSError,
        RuntimeError,
        ConnectionError,
    ) as error_log:
        dbuq(error_log)
    return False


@CUETYPE_CONFIG.decorator
def has_api(api_name: str, data: dict = None) -> bool:
    """Check available modules, try to import dynamically.\n
    True for successful import, else False\n

    :param api_name: Constant name for API
    :param _data: filled by config decorator, ignore, defaults to None
    :return: Package availability or `check_host` for servers; boolean result
    :rtype: bool
    """
    from importlib import import_module
    from json.decoder import JSONDecodeError

    hosted_apis = ["OLLAMA", "LM_STUDIO", "LLAMAFILE", "VLLM"]  # , "CORTEX" ] #became jan
    try:
        api_data = data.get(api_name, {"module": api_name.lower()})  # pylint: disable=unsubscriptable-object
    except JSONDecodeError as error_log:
        dbuq(error_log)
        return False
    try:
        module = import_module(api_data.get("module"))
        if module:
            if api_name not in hosted_apis:
                return True
            else:
                dbuq(api_data.get("api_url"))
                url = api_data.get("api_url")
                if url:
                    return check_host(api_name, url)
    except (UnboundLocalError, ImportError, ModuleNotFoundError, JSONDecodeError) as error_log:
        dbuq(error_log)
    dbuq("|Ignorable| Source unavailable:", f"{api_name}")
    return False


show_all_docstring = ":param _show_all(): Show all POSSIBLE API types of a given class"
show_available_docstring = ":param _show_available(): Show all AVAILABLE API types of a given class"
check_type_docstring = ":param _check_type: Check for a SINGLE API availability"

base_enum_docstring = f"""{show_all_docstring}{show_available_docstring}{check_type_docstring}"""


class BaseEnum(Enum):
    f"""{base_enum_docstring}"""

    @classmethod
    def show_all(cls) -> List:
        """Show all POSSIBLE API types of a given class"""
        return [x for x, y in cls.__members__.items()]

    @classmethod
    def show_available(cls) -> bool:
        """Show all AVAILABLE API types of a given class"""
        return [library.value[1] for library in list(cls) if library.value[0] is True]

    @classmethod
    def check_type(cls, type_name: str) -> bool:
        """Check for a SINGLE API availability"""
        type_name = type_name.upper()
        return has_api(type_name)


class CueType(BaseEnum):
    f"""Model Provider constants\n
    Caches and servers\n
    <NAME: (Availability, IMPORT_NAME)>{base_enum_docstring}
    {base_enum_docstring}"""

    # Dfferentiation of boolean conditions
    # GIVEN : The state of all provider modules & servers are marked at launch

    HUB: tuple = (has_api("HUB"), "HUB")
    KAGGLE: tuple = (has_api("KAGGLE"), "KAGGLE")
    LLAMAFILE: tuple = (has_api("LLAMAFILE"), "LLAMAFILE")
    LM_STUDIO: tuple = (has_api("LM_STUDIO"), "LM_STUDIO")
    MLX_AUDIO: tuple = (has_api("MLX_AUDIO"), "MLX_AUDIO")
    OLLAMA: tuple = (has_api("OLLAMA"), "OLLAMA")
    VLLM: tuple = (has_api("VLLM"), "VLLM")


example_str = ("function_name", "import.function_name")


class PkgType(BaseEnum):
    """Package dependency constants
    Collected info from hub model tags and dependencies
    <NAME: (Availability, IMPORT_NAME, [Github repositories*]
    *if applicable, otherwise IMPORT_NAME is pip package
    NOTE: NAME is colloquial and does not always match IMPORT_NAME>"""

    AUDIOGEN: tuple = (has_api("AUDIOCRAFT"), "AUDIOCRAFT", ["exdysa/facebookresearch-audiocraft-revamp"])  # this fork supports mps
    BAGEL: tuple = (has_api("BAGEL"), "BAGEL", ["bytedance-seed/BAGEL"])
    BITNET: tuple = (has_api("BITNET"), "BITNET", ["microsoft/BitNet"])
    BITSANDBYTES: tuple = (has_api("BITSANDBYTES"), "BITSANDBYTES", [])  # bitsandbytes-foundation/bitsandbytes
    DFLOAT11: tuple = (has_api("DFLOAT11"), "DFLOAT11", ["LeanModels/DFloat11"])
    DIFFUSERS: tuple = (has_api("DIFFUSERS"), "DIFFUSERS", [])
    EXLLAMAV2: tuple = (has_api("EXLLAMAV2"), "EXLLAMAV2", [])  # turboderp-org/exllamav2
    F_LITE: tuple = (has_api("F_LITE"), "F_LITE", ["fal-ai/f-lite"])
    HIDIFFUSION: tuple = (has_api("HIDIFFUSION"), "HIDIFFUSION", ["megvii-research/HiDiffusion"])
    IMAGE_GEN_AUX: tuple = (has_api("IMAGE_GEN_AUX"), "IMAGE_GEN_AUX", ["huggingface/image_gen_aux"])
    JAX: tuple = (has_api("JAX"), "JAX", [])
    KERAS: tuple = (has_api("KERAS"), "KERAS", [])
    LLAMA: tuple = (has_api("LLAMA_CPP"), "LLAMA_CPP", [])
    LUMINA_MGPT: tuple = (has_api("INFERENCE_SOLVER"), "INFERENCE_SOLVER", ["Alpha-VLLM/Lumina-mGPT"])
    LUMINA_MGPT2: tuple = (has_api("INFERENCE_SOLVER"), "INFERENCE_SOLVER", ["Alpha-VLLM/Lumina-mGPT-2.0"])
    MFLUX: tuple = (has_api("MFLUX"), "MFLUX", [])  # "filipstrand/mflux"
    MLX_AUDIO: tuple = (CueType.check_type("MLX_AUDIO"), "MLX_AUDIO", [])  # Blaizzy/mlx-audio
    MLX_CHROMA: tuple = (has_api("CHROMA"), "CHROMA", ["exdysa/jack813-mlx-chroma"])
    MLX_LM: tuple = (has_api("MLX_LM"), "MLX_LM", [])  # "ml-explore/mlx-lm"
    MLX_VLM: tuple = (has_api("MLX_VLM"), "MLX_VLM", [])  # Blaizzy/mlx-vlm
    MLX: tuple = (has_api("MLX_LM"), "MLX", [])
    ONNX: tuple = (has_api("ONNX"), "ONNX", ["ONNX"])
    ORPHEUS_TTS: tuple = (has_api("ORPHEUS_TTS"), "ORPHEUS_TTS", ["canopyai/Orpheus-TTS"])
    OUTETTS: tuple = (has_api("OUTETTS"), "OUTETTS", ["edwko/OuteTTS"])
    PARLER_TTS: tuple = (has_api("PARLER_TTS"), "PARLER_TTS", ["huggingface/parler-tts"])
    PLEIAS: tuple = (has_api("PLEIAS"), "PLEIAS", ["exdysa/Pleias-Pleias-RAG-Library"])  # bypasses vllm for macos to avoid requiring gcc/AVIX
    SENTENCE_TRANSFORMERS: tuple = (has_api("SENTENCE_TRANSFORMERS"), "SENTENCE_TRANSFORMERS", [])  # UKPLab/sentence-transformers
    SHOW_O: tuple = (has_api("SHOW_O"), "SHOW_O", ["showlab/show-o"])
    SPANDREL_EXTRA_ARCHES: tuple = (has_api("SPANDREL_EXTRA_ARCHES"), "SPANDREL_EXTRA_ARCHES", [])
    SPANDREL: tuple = (has_api("SPANDREL"), "SPANDREL", [])
    SVDQUANT: tuple = (has_api("NUNCHAKU"), "NUNCHAKU", ["mit-han-lab/nunchaku"])
    TENSORFLOW: tuple = (has_api("TENSORFLOW"), "TENSORFLOW", [])
    TORCH: tuple = (has_api("TORCH"), "TORCH", [])  # Possible that torch is NOT needed (mlx_lm, or some other unforeseen future )
    TORCHAUDIO: tuple = (has_api("TORCHAUDIO"), "TORCHAUDIO", [])
    TORCHVISION: tuple = (has_api("TORCHVISION"), "TORCHVISION", [])
    TRANSFORMERS: tuple = (has_api("TRANSFORMERS"), "TRANSFORMERS", [])
    VLLM: tuple = (CueType.check_type("VLLM"), "VLLM", [])


class ChipType(Enum):
    f"""Device constants\n
    CUDA, MPS, XPU, MTIA [Supported PkgTypes]\n
    {base_enum_docstring}"""

    def __call__(cls):
        cls.initialie_device()

    @classmethod
    def initialize_device(cls) -> None:
        chip_types = [
            (
                "CUDA",
                [
                    PkgType.BAGEL,
                    PkgType.BITSANDBYTES,
                    PkgType.DFLOAT11,
                    PkgType.EXLLAMAV2,
                    PkgType.F_LITE,
                    PkgType.LUMINA_MGPT,
                    PkgType.ORPHEUS_TTS,
                    PkgType.OUTETTS,
                    PkgType.VLLM,
                ],
            ),
            ("MPS", [PkgType.MFLUX, PkgType.MLX_AUDIO, PkgType.MLX_LM, PkgType.BAGEL]),
            ("XPU", []),
            ("MTIA", []),
        ]
        cls._device = first_available(assign=True, init=True, clean=True)  # pylint:disable=no-member, protected-access
        if hasattr(cls._device, "type"):
            gpu = cls._device.type
        else:
            gpu = ""
        for name, pkg_type in chip_types:
            setattr(cls, name, (name.lower() in gpu, name, pkg_type))
        setattr(
            cls,
            "CPU",
            (
                True,
                "CPU",
                [
                    PkgType.AUDIOGEN,
                    PkgType.PARLER_TTS,
                    PkgType.LLAMA,
                    PkgType.HIDIFFUSION,
                    PkgType.SENTENCE_TRANSFORMERS,
                    PkgType.DIFFUSERS,
                    PkgType.TRANSFORMERS,
                    PkgType.TORCH,
                ],
            ),
        )

    @classmethod
    def _show_all(cls) -> List[str]:
        """Show all POSSIBLE processor types"""
        atypes = [atype for atype in cls.__dict__ if "_" not in atype]
        return atypes

    @classmethod
    def _show_ready(cls, api_name: Optional[str] = None) -> Union[List[str], bool]:
        """Show all READY devices.\n
        If api_name is provided, checks if the specific API is ready.
        :param api_name: Boolean check for the specific API by name, defaults to None
        :return: `bool` or list of ready devices
        """
        atypes = cls._show_all()
        if api_name:
            return api_name.upper() in [x for x in atypes if getattr(cls, x)[0]]
        return [getattr(cls, x) for x in atypes if getattr(cls, x)[0] is True]

    @classmethod
    def _show_pkgs(cls) -> Union[List[PkgType], str]:
        """Return compatible PkgTypes for all available chipsets\n
        If no chipsets are detected, returns onlyCPU compatibility options\n
        :return: `PkgType`s for the available processors including CPU
        """
        pkg_names = getattr(cls, "CPU")[-1]
        atypes = cls._show_ready()
        available = [pkg[1] for pkg in atypes if pkg[0] is True]
        priority = next(iter(available), "CPU") if available else "CPU"
        if priority not in [pkg[1] for pkg in cls._show_all() if not pkg[2]] and priority != "CPU":
            pkg_names = atypes[0][2] + pkg_names
        return pkg_names


ChipType.initialize_device()


# class PipeType(Enum):
#     MFLUX: tuple = (ChipType._show_ready("mps"), PkgType.check_type("MFLUX"), {"mir_tag": "flux"})  # pylint:disable=protected-access
# MFLUX: tuple = ("MPS" in ChipType._show_ready("mps"), PkgType.MFLUX, {"mir_tag": "flux"})  # pylint:disable=protected-access


# Experimental way to abstract/declarify complex task names
class GenTypeC(BaseModel):
    """
    Generative inference types in ***C***-dimensional order\n
    ***Comprehensiveness***, sorted from 'most involved' to 'least involved'\n
    The terms define 'artistic' and ambiguous operations\n

    :param clone: Copying identity, voice, exact mirror
    :param sync: Tone, tempo, color, quality, genre, scale, mood
    :param translate: A range of comprehensible approximations\n
    """

    clone: Annotated[Callable | None, Field(default=None)]
    sync: Annotated[Callable | None, Field(default=None)]
    translate: Annotated[Callable | None, Field(default=None)]


class GenTypeCText(BaseModel):
    """
    Generative inference types in ***C***-dimensional order for text operations\n
    ***Comprehensiveness***, sorted from 'most involved' to 'least involved'\n
    The terms define 'concrete' and more rigid operations\n

    :param research: Quoting, paraphrasing, and deriving from sources
    :param chain_of_thought: A performance of processing step-by-step (similar to `reasoning`)
    :param question_answer: Basic, straightforward responses\n
    """

    research: Annotated[Optional[Callable | None], Field(default=None, examples=example_str)]
    chain_of_thought: Annotated[Optional[Callable | None], Field(default=None, examples=example_str)]
    question_answer: Annotated[Optional[Callable | None], Field(default=None, examples=example_str)]


class GenTypeE(BaseModel):
    """
    Generative inference operation types in ***E***-dimensional order \n
    ***Equivalence***, lists sorted from 'highly-similar' to 'loosely correlated.'"\n
    :param universal: Affecting all conversions
    :param text: Text-only conversions\n

    ***multimedia generation***
    ```
    Y-axis: Detail (Most involved to least involved)
    │
    │                             clone
    │                 sync
    │ translate
    │
    +───────────────────────────────────────> X-axis: Equivalence (Loosely correlated to highly similar)
    ```
    ***text generation***
    ```
    Y-axis: Detail (Most involved to least involved)
    │
    │                           research
    │             chain-of-thought
    │ question/answer
    │
    +───────────────────────────────────────> X-axis:  Equivalence (Loosely correlated to highly similar)
    ```

    This is essentially the translation operation of C types, and the mapping of them to E \n

    An abstract generalization of the set of all multimodal generative synthesis processes\n
    The sum of each coordinate pair reflects effective compute use\n
    In this way, both C types and their similarity are translatable, but not 1:1 identical\n
    Text is allowed to perform all 6 core operations. Other media perform only 3.\n
    """

    # note: `sync` may have better terms, such as 'harmonize' or 'attune'. `sync` was chosen because it is shorter

    universal: GenTypeC = GenTypeC(clone=None, sync=None, translate=None)
    text: GenTypeCText = GenTypeCText(research=None, chain_of_thought=None, question_answer=None)


# Here, a case could be made that tasks could be determined by filters, rather than graphing
# This is valid but, it offers no guarantees for difficult logic conditions that can be easily verified by graph algorithms
# Using graphs also allows us to offload the logic elsewhere

VALID_CONVERSIONS = ["text", "image", "music", "speech", "audio", "video", "3d", "vector_graphic", "upscale_image"]
VALID_JUNCTIONS = [""]

# note : decide on a way to keep paired tuples and sets together inside config dict

tasks = PIPELINE_REGISTRY.get_supported_tasks() + ["translation_XX_to_YY"]

VALID_TASKS = {  # normalized to lowercase
    CueType.VLLM: {
        ("text", "text"): ["text"],
        ("image", "text"): ["vision"],
    },
    CueType.OLLAMA: {
        ("text", "text"): ["mllama"],
        ("image", "text"): ["llava", "vllm"],
    },
    CueType.LLAMAFILE: {
        ("text", "text"): ["text"],
    },
    CueType.LM_STUDIO: {
        # ("image", "text"): [("vision", True)],
        ("text", "text"): ["llm"],
    },
    CueType.HUB: {
        ("image", "image"): [
            "image-to-image",
            "inpaint",
            "inpainting",
            "depth-to-image",
            "i2i",
            "image-to-image",
            "any-to-any",
        ],
        ("text", "image"): [
            "kolors",
            "kolorspipeline",
            "image-generation",
            "any-to-any",
            "text-to-image",
        ],
        ("image", "text"): [
            "image-classification",
            "image-to-text",
            "image-text-to-text",
            "visual-question-answering",
            "image-captioning",
            "image-segmentation",
            "depth-estimation",
            "image-feature-extraction",
            "mask-generation",
            "object-detection",
            "visual-question-answering",
            "keypoint-detection",
            "vllm",
            "vqa",
            "vision",
            "zero-shot-object-detection",
            "zero-shot-image-classification",
            "timm",
            "zero-shot image classification",
            "any-to-any",
            "vidore",
        ],
        ("image", "video"): ["image-to-video", "i2v", "reference-to-video", "refernce-to-video"],
        ("video", "text"): ["video-classification"],
        ("text", "video"): ["video generation", "t2v", "text-to-video"],
        ("text", "text"): [
            "any-to-any",
            "named entity recognition",
            "entity typing",
            "relation classification",
            "question answering",
            "fill-mask",
            "chat",
            "conversational",
            "text-generation",
            "causal-lm",
            "text2text-generation",
            "document-question-answering",
            "feature-extraction",
            "question-answering",
            "sentiment-analysis",
            "summarization",
            "table-question-answering",
            "text-classification",
            "token-classification",
            "translation",
            "zero-shot-classification",
            "translation_xx_to_yy",
            "t2t",
            "chatglm",
            "exbert",
        ],
        ("text", "audio"): ["text-to-audio", "t2a", "any-to-any", "musicgen", "audiocraft", "audiogen", "audioldmpipeline", "audioldm2pipeline"],
        ("audio", "text"): ["zero-shot-audio-classification", "audio-classification", "a2t", "audio-text-to-text", "any-to-any"],
        ("text", "speech"): [
            "text-to-speech",
            "tts",
            "any-to-any",
            "annotation",
        ],
        ("speech", "text"): [
            "speech-to-text",
            "speech",
            "speech-translation",
            "speech-summarization",
            "automatic-speech-recognition",
            "dictation",
            "stt",
            "any-to-any",
            "hf-asr-leaderboard",
        ],
    },
    CueType.KAGGLE: {
        ("text", "text"): ["text"],
    },
    # CueType.CORTEX: {
    #     ("text", "text"): ["text"],
    # },
}
