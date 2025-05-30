#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->
import pytest
from unittest import TestCase
from nnll_01 import nfo
from nnll_15 import from_cache
from nnll_15.constants import VALID_CONVERSIONS
from test_graph import mock_hub_data, mock_ollama_data


class TestGraph(TestCase):
    def setUp(self):
        from zodiac.graph import IntentProcessor

        self.graph = IntentProcessor()

    def test_flow_builder_fail_registry(self, mode_in: str = "text", image: str = "speech"):
        assert self.graph.has_graph() is True
        assert self.graph.has_path() is False
        assert self.graph.has_reg_entries() is False
        assert self.graph.models is None
        model_data = registry_entries = {"useless": "data"}
        self.graph.calc_graph(model_data)
        assert self.graph.has_path() is False
        assert self.graph.has_reg_entries() is False
        assert self.graph.models is None
        model_data_len = 0
        assert f"{self.graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {model_data_len} edges"
        # assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and 0 edges"
        import gc

        self.graph = None
        gc.collect


class TestGraph_2(TestCase):
    def setUp(self):
        import gc

        gc.collect()
        from zodiac.graph import IntentProcessor

        self.graph = IntentProcessor()

    def test_flow_builder_fail_edge_create(self, mode_in: str = "text", mode_out: str = "image"):
        # graph.calc_graph()
        self.graph.calc_graph(registry_entries={"useless": "data"})
        assert self.graph.has_graph() is True
        assert f"{self.graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and 0 edges"
        assert self.graph.has_path() is False
        self.graph.set_path(mode_in=mode_in, mode_out=mode_out)
        nfo(self.graph.coord_path)
        assert self.graph.has_path() is False
        nfo(self.graph.reg_entries)
        assert self.graph.has_reg_entries() is False
        self.graph.set_reg_entries()
        nfo(self.graph.reg_entries)
        assert self.graph.has_reg_entries() is False
        assert self.graph.reg_entries == []
        nfo(self.graph.models)
        assert self.graph.models is None
        self.graph.edit_weight("flux", "text", "image")
        self.graph = None
        import gc

        gc.collect
