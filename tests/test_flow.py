#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->
import pytest
from unittest import TestCase
from nnll.monitor.console import nfo
from zodiac.providers.constants import VALID_CONVERSIONS
from test_graph import mock_hub_data, mock_ollama_data


class TestGraph(TestCase):
    def setUp(self):
        from zodiac.graph import IntentProcessor

        self.graph = IntentProcessor()

    def test_flow_builder_fail_registry(self, mode_in: str = "text", image: str = "speech"):
        assert hasattr(self.graph.intent_graph, "size") and self.graph.intent_graph.size() == 0
        assert not self.graph.coord_path
        assert not self.graph.registry_entries
        assert not self.graph.models
        model_data = {"useless": "data"}
        self.graph.calc_graph(model_data)
        assert not self.graph.coord_path
        assert not self.graph.registry_entries
        assert not self.graph.models
        model_data_len = 0
        assert f"{self.graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {model_data_len} edges"
        # assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and 0 edges"
        import gc

        self.graph = None
        gc.collect()


class TestGraph_2(TestCase):
    def setUp(self):
        import gc

        gc.collect()
        from zodiac.graph import IntentProcessor

        self.graph = IntentProcessor()

    def test_flow_builder_fail_edge_create(self, mode_in: str = "text", mode_out: str = "image"):
        # graph.calc_graph()
        self.graph.calc_graph(registry_entries={"useless": "data"})
        assert hasattr(self.graph.intent_graph, "size") and self.graph.intent_graph.size() == 0
        assert f"{self.graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and 0 edges"
        assert not self.graph.coord_path
        self.graph.set_path(mode_in=mode_in, mode_out=mode_out)
        nfo(self.graph.coord_path)
        assert not self.graph.coord_path
        nfo(self.graph.registry_entries)
        assert not self.graph.registry_entries
        self.graph.set_registry_entries()
        nfo(self.graph.registry_entries)
        assert not self.graph.registry_entries
        nfo(self.graph.models)
        assert not self.graph.models
        self.graph.edit_weight("flux", "text", "image")
        self.graph = None
        import gc

        gc.collect()
