#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->
from unittest import TestCase
import pytest
from nnll.monitor.file import nfo
from mir.registry_entry import from_cache
from mir.constants import VALID_CONVERSIONS
from test_graph import mock_hub_data, mock_ollama_data, test_mocked_hub, test_mocked_ollama, test_mocked_hub


# For some reason the graph holds states between tests, need to troubleshoot later


class TestFlow:
    # @pytest.fixture(scope="module")
    # def setUp(self):
    #     from zodiac.graph import IntentProcessor

    def test_flow_builder_edge_create_success(self, mock_ollama_data, mock_hub_data, mode_in: str = "text", mode_out: str = "speech"):
        from pytest import raises
        from mir.registry_entry import RegistryEntry
        from mir.constants import LibType, PkgType
        from zodiac.graph import IntentProcessor

        self.graph = IntentProcessor()
        # graph.calc_graph()
        model_data = from_cache()
        self.graph.calc_graph(model_data)
        model_data_len = 0
        for model in model_data:
            model_data_len += len(model.available_tasks)
        assert f"{self.graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {model_data_len} edges"
        self.graph.set_path(mode_in=mode_in, mode_out=mode_out)
        assert self.graph.has_path() is True
        self.graph.set_reg_entries()
        assert self.graph.has_reg_entries() is True
        assert self.graph.models == [
            (
                "parler-tts-large-v1",
                0,
            )
        ]
        expected = {
            "entry": RegistryEntry(
                model="parler-tts/parler-tts-large-v1",
                size=9335526346,
                tags=["text-to-speech", "annotation", "text-to-speech"],
                library=LibType.HUB,
                timestamp=1741908821,
                mir=["info.art.parler-tts", "large-v1"],
                api_kwargs=None,
                package=PkgType.TRANSFORMERS,
                tokenizer=None,
                available_tasks=[("text", "speech")],
            ),
        }
        expected_true = expected
        expected.setdefault("weight", 1.0)
        # self.graph.edit_weight("parler", "text", "speech")
        assert next(iter(self.graph.reg_entries)) == expected_true
        expected_true["weight"] = 0.9
        expected_false = expected
        expected_false.setdefault("weight", 0.8)
        self.graph.edit_weight(0, "text", "speech")
        assert next(iter(self.graph.reg_entries)) == expected_true
        # with raises(AssertionError) as excinfo:
        self.graph.edit_weight(0, "text", "speech")
        expected_true["weight"] = 1.0
        assert next(iter(self.graph.reg_entries)) == expected_true
        # import re

        # nfo(f"{expected_true} == {expected_false}")
        # clean_text = re.sub(r"\x1b$$[0-?]*[ -/]*[@-~]", "", f"{excinfo.value}")
        # assert str(clean_text) == expected_false
        self.graph = None
        import gc

        gc.collect


class TestGraphSetup2(TestCase):
    def setUp(self):
        import gc

        gc.collect()
        from zodiac.graph import IntentProcessor

        self.graph = IntentProcessor()

    def test_flow_builder_edge_create_success(self, mode_in: str = "text", mode_out: str = "image"):
        # graph.calc_graph()
        model_data = from_cache()
        self.graph.calc_graph(model_data)
        assert self.graph.has_graph() is True
        model_data_len = 0
        for model in model_data:
            model_data_len += len(model.available_tasks)
        assert f"{self.graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {model_data_len} edges"
        assert self.graph.has_path() is False
        self.graph.set_path(mode_in=mode_in, mode_out=mode_out)
        nfo(f"coord_path {self.graph.coord_path}")
        assert self.graph.has_path() is True
        nfo(f"ckpts : {self.graph.reg_entries}")
        assert self.graph.has_reg_entries() is False
        self.graph.set_reg_entries()
        nfo(self.graph.reg_entries)
        assert self.graph.has_reg_entries() is True
        nfo(self.graph.models)
        assert self.graph.models == [("CogView3-Plus-3B", 0)]
        self.graph = None
        import gc

        gc.collect
