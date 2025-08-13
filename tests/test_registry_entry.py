import pytest
from datetime import datetime
from zodiac.providers.constants import CueType
from zodiac.providers.registry_entry import RegistryEntry


@pytest.fixture
def registry_entry_ollama():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=["mllama", "llava", "text"],
        cuetype=CueType.OLLAMA,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


@pytest.fixture
def registry_entry_hub():
    return RegistryEntry(
        model="🤡",
        size=512,
        tags=["text-generation", "image-to-text", "text-to-speech", "text"],
        cuetype=CueType.HUB,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


def test_ollama_available_tasks(registry_entry_ollama: RegistryEntry):
    assert registry_entry_ollama.available_tasks == [("text", "text"),("image", "text")]


def test_hub_available_tasks(registry_entry_hub: RegistryEntry):  # ensure that the system does not duplicate entries
    expected_tasks = [("text", "text"), ("text", "text"), ("image", "text"), ("text", "speech")]
    assert set(registry_entry_hub.available_tasks) == set(expected_tasks)
    assert registry_entry_hub.available_tasks.count(("text", "text")) == 1


@pytest.fixture
def hub_xlate():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=["speech-translation"],
        cuetype=CueType.HUB,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


@pytest.fixture
def hub_sum():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=["speech-summarization"],
        cuetype=CueType.HUB,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


@pytest.fixture
def hub_asr():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=["automatic-speech-recognition"],
        cuetype=CueType.HUB,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


@pytest.fixture
def hub_tts():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=[
            "text-to-speech",
        ],
        cuetype=CueType.HUB,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


def test_hub_xlate(hub_xlate):
    expected_tasks = [
        ("speech", "text"),
    ]
    assert set(hub_xlate.available_tasks) == set(expected_tasks)


def test_hub_sum(hub_sum):
    expected_tasks = [
        ("speech", "text"),
    ]

    assert set(hub_sum.available_tasks) == set(expected_tasks)


def test_hub_asr(hub_asr):
    expected_tasks = [
        ("speech", "text"),
    ]
    assert set(hub_asr.available_tasks) == set(expected_tasks)


def test_hub_tts(hub_tts):
    expected_tasks = [
        ("text", "speech"),
    ]

    assert set(hub_tts.available_tasks) == set(expected_tasks)


@pytest.fixture
def registry_entry_hub_extra():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=["speech-translation", "speech-summarization", "automatic-speech-recognition", "text-to-speech", "video generation"],
        cuetype=CueType.HUB,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


def test_hub_extra_tasks(registry_entry_hub_extra: RegistryEntry):  # ensure that the system does not duplicate entries
    expected_tasks = [
        ("speech", "text"),
        ("text", "speech"),
        ("text", "video"),
    ]
    assert set(registry_entry_hub_extra.available_tasks) == set(expected_tasks)


# @pytest.fixture
# def registry_entry_cortex():
#     return RegistryEntry(
#         model="🤡",
#         size=1024,
#         tags=["speech-translation", "speech-summarization", "automatic-speech-recognition", "text-to-speech", "video generation"],
#         # cuetype=CueType.CORTEX,
#         mir=None,
#         api_kwargs=None,
#         timestamp=int(datetime.now().timestamp()),
#     )


# def test_cortex_tasks(registry_entry_cortex: RegistryEntry):  # ensure that the system does not duplicate entries
#     expected_tasks = [
#         ("text", "text"),
#     ]
#     assert set(registry_entry_cortex.available_tasks) == set(expected_tasks)


@pytest.fixture
def registry_entry_vllm():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=["text", "vision"],
        cuetype=CueType.VLLM,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


def test_vllm_tasks(registry_entry_vllm: RegistryEntry):  # ensure that the system does not duplicate entries
    expected_tasks = [
        ("text", "text"),
        ("image", "text"),
    ]
    assert set(registry_entry_vllm.available_tasks) == set(expected_tasks)


@pytest.fixture
def registry_entry_llamafile():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=[],
        cuetype=CueType.LLAMAFILE,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


def test_llamafile_tasks(registry_entry_llamafile: RegistryEntry):  # ensure that the system does not duplicate entries
    expected_tasks = [
        ("text", "text"),
    ]
    assert set(registry_entry_llamafile.available_tasks) == set(expected_tasks)


@pytest.fixture
def registry_entry_lm_studio():
    return RegistryEntry(
        model="🤡",
        size=1024,
        tags=["text", "llm"],
        cuetype=CueType.LM_STUDIO,
        mir=None,
        api_kwargs=None,
        timestamp=int(datetime.now().timestamp()),
    )


def test_lm_studio_tasks(registry_entry_lm_studio: RegistryEntry):  # ensure that the system does not duplicate entries
    expected_tasks = [
        ("text", "text"),
    ]
    assert set(registry_entry_lm_studio.available_tasks) == set(expected_tasks)
    assert registry_entry_lm_studio.available_tasks.count(("text", "text")) == 1
