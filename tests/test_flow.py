#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->
import pytest
from unittest import TestCase
from nnll.monitor.console import nfo
from zodiac.providers.constants import VALID_CONVERSIONS
from test_graph import mock_hub_data, mock_ollama_data


@pytest.mark.asyncio(loop_scope="session")
async def test_flow_builder_fail_registry(mode_in: str = "text", image: str = "speech"):
    from zodiac.graph import IntentProcessor

    graph = IntentProcessor()
    assert hasattr(graph.intent_graph, "size") and graph.intent_graph.size() == 0
    assert not graph.coord_path
    assert not graph.registry_entries
    assert not graph.models
    model_data = {"useless": "data"}
    await graph.calc_graph(model_data)
    assert not graph.coord_path
    assert not graph.registry_entries
    assert not graph.models
    model_data_len = 0
    assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and {model_data_len} edges"
    # assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and 0 edges"
    import gc

    gc.collect()
    return graph


@pytest.mark.asyncio(loop_scope="session")
async def test_flow_builder_fail_edge_create(mode_in: str = "text", mode_out: str = "image"):
    import gc

    gc.collect()
    from zodiac.graph import IntentProcessor

    graph = IntentProcessor()
    await graph.calc_graph(registry_entries={"useless": "data"})
    assert hasattr(graph.intent_graph, "size") and graph.intent_graph.size() == 0
    assert f"{graph.intent_graph}" == f"MultiDiGraph with {len(VALID_CONVERSIONS)} nodes and 0 edges"
    assert not graph.coord_path
    graph.set_path(mode_in=mode_in, mode_out=mode_out)
    nfo(graph.coord_path)
    assert not graph.coord_path
    nfo(graph.registry_entries)
    assert not graph.registry_entries
    graph.set_registry_entries()
    nfo(graph.registry_entries)
    assert not graph.registry_entries
    nfo(graph.models)
    assert not graph.models
    graph.edit_weight("flux", "text", "image")
    import gc

    gc.collect()
    return graph
