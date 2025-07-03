import pytest
import pytest_asyncio
from unittest.mock import patch
from typing import List
from enum import Enum


class MockPackage(Enum):
    MFLUX = (False, "MFLUX")
    TRANSFORMERS = (True, "TRANSFORMERS")
    DIFFUSERS = (True, "DIFFUSERS")
    VLLM = (True, "VLLM")


@pytest.fixture
def mock_package_available():
    with patch("zodiac.streams.class_stream.PkgType") as mock_pkg_type:
        mock_pkg_type.return_value = MockPackage
        yield mock_pkg_type


@pytest.fixture
def mock_cpu_available():
    class MockDevice(Enum):
        """"""

    with patch("zodiac.streams.class_stream.ChipType") as mock_chip_type:
        mock_chip_type._show_ready.return_value = ["CPU"]
        mock_chip_type.CPU = (True, "CPU", [MockPackage.TRANSFORMERS, MockPackage.DIFFUSERS])
        mock_chip_type.MPS = (False, "MFLUX", [MockPackage.MFLUX])
        yield mock_chip_type


@pytest.fixture
def mock_gpu_available():
    class MockDevice(Enum):
        """"""

    with patch("zodiac.streams.class_stream.ChipType") as mock_chip_type:
        mock_chip_type._show_ready.return_value = ["CUDA"]
        mock_chip_type.MPS = (False, "MFLUX", [MockPackage.MFLUX])
        mock_chip_type.CPU = (True, "CUDA", [MockPackage.VLLM, MockPackage.TRANSFORMERS, MockPackage.DIFFUSERS])
        yield mock_chip_type


# @patch("zodiac.streams.class_stream.has_api", return_value=True)
async def test_lookup(mock_cpu_available, mock_package_available):
    from zodiac.streams.class_stream import find_package
    # from zodiac.task_stream import ChipType, PkgType

    class Entry:
        mir: List[str] = ["info.dit.flux-1-dev", "base"]

    entry = Entry()

    with patch(
        "zodiac.streams.class_stream.MIR_DB.database",
        new={
            "info.dit.flux-1-dev": {"base": {"pkg": {0: {"diffusers": "FluxPipeline"}, 1: {"mflux": "Flux1"}}}},
            "info.vit.blip-vqa": {"base": {"pkg": {0: {"transformers": "BlipModel"}}}},
        },
    ):
        result = await find_package(entry)
        assert result == ("FluxPipeline", MockPackage.DIFFUSERS)


# @patch("zodiac.providers.constants.has_api", return_value=True)
async def test_lookup_transformers(mock_cpu_available, mock_package_available):
    from zodiac.streams.class_stream import find_package

    class Entry:
        mir: List[str] = ["info.vit.blip-vqa", "base"]

    entry = Entry()
    with patch("zodiac.streams.class_stream.MIR_DB.database", new={"info.vit.blip-vqa": {"base": {"pkg": {0: {"transformers": "BlipModel"}}}}}):
        result = await find_package(entry)
        assert result == ("BlipModel", MockPackage.TRANSFORMERS)  # This should pass with correct mock data


async def test_lookup_with_reverse_position(mock_cpu_available, mock_package_available):
    from zodiac.streams.class_stream import find_package
    # from zodiac.streams.class_stream import ChipType, PkgType

    class Entry:
        mir: List[str] = ["info.dit.flux-1-dev", "base"]

    entry = Entry()

    with patch(
        "zodiac.streams.class_stream.MIR_DB.database",
        new={
            "info.vit.blip-vqa": {"base": {"pkg": {0: {"transformers": "BlipModel"}}}},
            "info.dit.flux-1-dev": {"base": {"pkg": {0: {"diffusers": "FluxPipeline"}, 1: {"mflux": "Flux1"}}}},
        },
    ):
        result = await find_package(entry)
        assert result == ("FluxPipeline", MockPackage.DIFFUSERS)


# def test_lookup_with_reverse_position(mock_cpu_available, mock_package_available):
#     from zodiac.streams.class_stream import find_package
#     # from zodiac.task_stream import ChipType, PkgType

#     class Entry:
#         mir: List[str] = ["info.dit.flux-1-dev", "base"]

#     entry = Entry()

#     with patch(
#         "zodiac.task_stream.MIR_DB.database",
#         new={
#             "info.vit.blip-vqa": {"base": {"pkg": {0: {"transformers": "BlipModel"}}}},
#             "info.dit.flux-1-dev": {"base": {"pkg": {0: {"diffusers": "FluxPipeline"}, 1: {"mflux": "Flux1"}}}},
#         },
#     ):
#         result = find_package(entry)
#         assert result == ("FluxPipeline", MockPackage.DIFFUSERS)
