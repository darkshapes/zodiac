#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->
from unittest import TestCase
import pytest
from nnll.monitor.console import nfo
from zodiac.providers.pools import register_models
from zodiac.providers.constants import VALID_CONVERSIONS
from test_graph import mock_hub_data, mock_ollama_data, test_mocked_hub, test_mocked_ollama, test_mocked_hub, mock_ollama_show


# For some reason the graph holds states between tests, need to troubleshoot later


class TestFlow:
    # @pytest.fixture(scope="module")
    # def setUp(self):
    #     from zodiac.graph import IntentProcessor

    def test_flow_builder_edge_create_success(self, mock_ollama_data, mock_hub_data, mock_ollama_show, mode_in: str = "text", mode_out: str = "speech"):
        from pytest import raises
        from zodiac.providers.registry_entry import RegistryEntry
        from zodiac.providers.constants import CueType, PkgType
        from zodiac.graph import IntentProcessor

        self.graph = IntentProcessor()
        # graph.calc_graph()
        model_data = register_models()
        self.graph.calc_graph(model_data)
        model_data_len = 0
        for model in model_data:
            model_data_len += len(model.available_tasks)
        assert f"{self.graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {model_data_len} edges"
        self.graph.set_path(mode_in=mode_in, mode_out=mode_out)
        assert self.graph.coord_path == ["text", "speech"]
        self.graph.set_registry_entries()
        assert isinstance(self.graph.registry_entries, list)
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
                cuetype=CueType.HUB,
                timestamp=1741908821,
                mir=["info.artm.parler-tts", "large-v1"],
                api_kwargs={"module": "huggingface_hub", "api_kwargs": {"api_base": "http://127.0.0.1:8188"}, "prefix": ""},
                package=PkgType.TRANSFORMERS,
                tokenizer=None,
                available_tasks=[("text", "speech")],
            ),
            "weight": 1.0,
        }
        # registry entry should start the same as above
        assert next(iter(self.graph.registry_entries)) == expected

        expected["weight"] = 0.8
        self.graph.edit_weight(0, "text", "speech")
        assert next(iter(self.graph.registry_entries)) != expected
        expected["weight"] = 0.9
        assert next(iter(self.graph.registry_entries)) == expected

        self.graph.edit_weight(0, "text", "speech")
        expected["weight"] = 1.0
        assert next(iter(self.graph.registry_entries)) == expected
        self.graph = None
        import gc

        gc.collect()


class TestGraphSetup2(TestCase):
    def setUp(self):
        import gc

        gc.collect()
        from zodiac.graph import IntentProcessor

        self.graph = IntentProcessor()

    def test_flow_builder_edge_create_success(self, mode_in: str = "text", mode_out: str = "image"):
        # graph.calc_graph()
        import networkx as nx

        model_data = register_models()
        self.graph.calc_graph(model_data)
        assert self.graph.intent_graph.size() != 0 and self.graph.intent_graph.size() is not False
        model_data_len = 0
        for model in model_data:
            model_data_len += len(model.available_tasks)
        assert f"{self.graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {model_data_len} edges"
        assert not self.graph.coord_path
        self.graph.set_path(mode_in=mode_in, mode_out=mode_out)
        nfo(f"coord_path {self.graph.coord_path}")
        assert self.graph.coord_path == ["text", "image"]
        nfo(f"ckpts : {self.graph.registry_entries}")
        assert not self.graph.registry_entries
        self.graph.set_registry_entries()
        nfo(self.graph.registry_entries)
        assert isinstance(self.graph.registry_entries, list)
        nfo(self.graph.models)
        assert self.graph.models == [("CogView3-Plus-3B", 0)]
        self.graph = None
        import gc

        gc.collect()
