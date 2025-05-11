#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->
import pytest
from nnll_01 import nfo
from nnll_15 import from_cache
from nnll_15.constants import VALID_CONVERSIONS
from zodiac.graph import IntentProcessor
from test_graph import mock_hub_data, mock_ollama_data, test_mocked_hub, test_mocked_ollama

graph = None
mock_edges = 6


def test_flow_builder_fail_registry(mode_in: str = "text", image: str = "text"):
    graph = IntentProcessor()
    assert graph.has_graph() is True
    assert graph.has_path() is False
    assert graph.has_ckpt() is False
    assert graph.models is None
    graph.calc_graph(registry_entries={"useless": "data"})
    assert graph.has_path() is False
    assert graph.has_ckpt() is False
    assert graph.models is None
    assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and 0 edges"


def test_flow_builder_fail_edge_create(mock_ollama_data, mock_hub_data, mode_in: str = "text", mode_out: str = "image"):
    graph = IntentProcessor()
    # graph.calc_graph()
    graph.calc_graph(registry_entries={"useless": "data"})
    assert graph.has_graph() is True
    assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and 0 edges"
    assert graph.has_path() is False
    graph.set_path(mode_in=mode_in, mode_out=mode_out)
    nfo(graph.coord_path)
    assert graph.has_path() is False
    nfo(graph.ckpts)
    assert graph.has_ckpt() is False
    graph.set_ckpts()
    nfo(graph.ckpts)
    assert graph.has_ckpt() is False
    assert graph.ckpts == []
    nfo(graph.models)
    assert graph.models is None
    graph.edit_weight("flux", "text", "image")


def test_flow_builder_edge_create_success(mock_ollama_data, mock_hub_data, mode_in: str = "text", mode_out: str = "image"):
    graph = IntentProcessor()
    # graph.calc_graph()
    graph.calc_graph(from_cache())
    assert graph.has_graph() is True
    assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {mock_edges} edges"
    assert graph.has_path() is False
    graph.set_path(mode_in=mode_in, mode_out=mode_out)
    nfo(f"coord_path {graph.coord_path}")
    assert graph.has_path() is True
    nfo(f"ckpts : {graph.ckpts}")
    assert graph.has_ckpt() is False
    graph.set_ckpts()
    nfo(graph.ckpts)
    assert graph.has_ckpt() is True
    nfo(graph.models)
    assert graph.models == [("CogView3-Plus-3B", "THUDM/CogView3-Plus-3B")]


def test_flow_builder_edge_create_success(mock_ollama_data, mock_hub_data, mode_in: str = "text", mode_out: str = "image"):
    from pytest import raises
    from nnll_15 import RegistryEntry
    from nnll_15.constants import LibType

    graph = IntentProcessor()
    # graph.calc_graph()
    graph.calc_graph(from_cache())
    assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {mock_edges} edges"
    graph.set_path(mode_in=mode_in, mode_out=mode_out)
    assert graph.has_path() is True
    graph.set_ckpts()
    assert graph.has_ckpt() is True
    assert graph.models == [("CogView3-Plus-3B", "THUDM/CogView3-Plus-3B")]
    expected = {
        "entry": RegistryEntry(model="THUDM/CogView3-Plus-3B", size=25560123724, tags=["text-to-image", "image-generation", "cogview"], library=LibType.HUB, timestamp=1741827083, available_tasks=[("text", "image"), ("image", "text")]),
    }
    expected_true = expected
    expected.setdefault("weight", 1.0)
    graph.edit_weight("cogv iew", "text", "image")
    assert next(iter(graph.ckpts)) == expected_true
    expected_true["weight"] = 0.9
    expected_false = expected
    expected_false.setdefault("weight", 0.8)
    graph.edit_weight("CogView", "text", "image")
    assert next(iter(graph.ckpts)) == expected_true
    # with raises(AssertionError) as excinfo:
    graph.edit_weight("CogView", "text", "image")

    # test fail case
    expected_true["weight"] = 1.0
    assert next(iter(graph.ckpts)) == expected_true
    # import re

    # nfo(f"{expected_true} == {expected_false}")
    # clean_text = re.sub(r"\x1b$$[0-?]*[ -/]*[@-~]", "", f"{excinfo.value}")
    # assert str(clean_text) == expected_false
