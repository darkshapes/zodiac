#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# import pytest
# from unittest.mock import patch
# import pytest_asyncio
import asyncio
from zodiac.streams.task_stream import TaskStream
from zodiac.providers.constants import CueType

# class CueType:
#     def __init__(self, id_name):
#         setattr(self, id_name.upper(), (True, id_name.upper()))


# cuetype = CueType("HUB")


# @pytest_asyncio.fixture(loop_scope="module")
# async def mock_cuetype():
#     with patch("", autospec=True) as mocked:
#         mocked.HUB = (True, "HUB")
#         yield mocked


class RegistryEntryVoice:
    def __init__(self):
        self.cuetype = CueType.HUB
        self.model = "UsefulSensors/moonshine"
        self.size = 247038024
        self.tags = ["automatic-speech-recognition"]
        self.timestamp = 1749921961
        self.mir = ["info.ststm.moonshine", "tiny"]  # ["info.ststm.moonshine","tiny"] #needs to be populated from config file
        self.available_tasks = [("speech", "text")]


class RegistryEntryImg:
    def __init__(self):
        self.cuetype = CueType.HUB
        self.model = "stability-ai/stable-diffusion-xl-1.0-base"
        self.mir = ["info.unet.stable-diffusion-xl", "base"]
        self.available_tasks = [("text", "image"), ("image", "image")]


class RegistryEntryText:
    def __init__(self):
        self.cuetype = CueType.HUB
        self.mir = ["info.vit.blip-vqa", "base"]


def test_trace_tasks():
    entry = RegistryEntryImg()
    task_stream = TaskStream()
    loop = asyncio.get_event_loop()

    loop.run_until_complete(task_stream.set_filter_type("text", "image"))
    result = loop.run_until_complete(task_stream.trace_tasks(entry))
    # print(f"{result}")
    # assert result not in ["ControlNet", "ControlNetImg2Img", "ControlNetInpaint", "ControlNetPAG", "ControlNetPAGImg2Img", "ControlNetUnion", "ControlNetUnionImg2Img", "ControlNetUnionInpaint", "Img2Img", "Inpaint", "PAGImg2Img", "PAGInpaint"]
    assert len(result) == 11


def test_trace_mode_tasks():
    entry = RegistryEntryImg()
    task_stream = TaskStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task_stream.set_filter_type("image", "image"))
    result = loop.run_until_complete(task_stream.trace_tasks(entry))
    assert (
        len(result) == 11
    )  # == ["ControlNet", "ControlNetImg2Img", "ControlNetInpaint", "ControlNetPAG", "ControlNetPAGImg2Img", "ControlNetUnion", "ControlNetUnionImg2Img", "ControlNetUnionInpaint", "Img2Img", "Inpaint", "PAGImg2Img", "PAGInpaint"]


def test_trace_tf_tasks():
    entry = RegistryEntryVoice()
    task_stream = TaskStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task_stream.set_filter_type("text", None))
    result = loop.run_until_complete(task_stream.trace_tasks(entry))
    assert result != ["ForConditionalGeneration"]
    assert result != [""]
    assert result == []


def test_trace_text_tasks():
    entry = RegistryEntryText()
    task_stream = TaskStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task_stream.set_filter_type("text", None))
    result = loop.run_until_complete(task_stream.trace_tasks(entry))
    assert result == ["BlipQuestionAnswering"]
