# #  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
# #  # # <!-- // /*  d a r k s h a p e s */ -->

from pytest import raises


def setUp(lookit_this):
    import networkx as nx
    from zodiac.graph import IntentProcessor

    proc_name = IntentProcessor()  # Replace with actual class name
    proc_name.intent_graph = nx.Graph(lookit_this)
    assert hasattr(proc_name.intent_graph, "size") and proc_name.intent_graph.size() > 0
    proc_name.set_path("mode_in", "mode_out")
    proc_name.set_registry_entries()
    assert isinstance(proc_name.coord_path, list) and len(proc_name.coord_path) > 1
    assert isinstance(proc_name.registry_entries, list) and len(proc_name.registry_entries) > 1
    return proc_name


def graph():  # :)
    from collections import namedtuple

    Entry = namedtuple("Entry", ["model", "etc"])
    graaph = {
        "mode_in": {
            "mode_out": {
                0: {
                    "entry": Entry("🤡1", ""),
                    "weight": 0.5,
                },
                1: {
                    "entry": Entry("🤡2", ""),
                    "weight": 1.2,
                },
            }
        }
    }
    return graaph  # 2 as


int_proc = setUp(lookit_this=graph())


def test_edit_weight():
    assert int_proc.intent_graph["mode_in"]["mode_out"][0]["weight"] == 0.5
    assert int_proc.intent_graph["mode_in"]["mode_out"][1]["weight"] == 1.2
    int_proc.edit_weight(0, "mode_in", "mode_out")
    int_proc.edit_weight(1, "mode_in", "mode_out")
    assert int_proc.intent_graph["mode_in"]["mode_out"][0]["weight"] == 0.6
    assert int_proc.intent_graph["mode_in"]["mode_out"][1]["weight"] == 1.1


def test_edit_weight_model_not_present_quiet_fail():
    int_proc.edit_weight("nonexistent", "mode_in", "mode_out")


def test_edit_weight_node_not_present():
    import networkx as nx

    int_proc.intent_graph.remove_node("mode_out")
    with raises(KeyError) as excinfo:
        assert int_proc.intent_graph["mode_in"]["mode_out"][0]["weight"] == 0.6

    with raises(nx.exception.NodeNotFound) as excinfo:
        int_proc.edit_weight(0, "mode_in", "mode_out")
        assert str(excinfo.value) == f"Failed to adjust weight of '🤡1' within registry contents '{[nbrdict for n, nbrdict in int_proc.intent_graph.adjacency()]}'. Model or registry entry not found."


def graaaaph():  # :)
    from collections import namedtuple

    Entry = namedtuple("Entry", ["model", "etc"])
    graaaph = {
        "mode_in": {
            "mode_out": {
                0: {
                    "entry": Entry("🤡3", ""),
                    "weight": 1.0,
                },
                1: {
                    "entry": Entry("🤡4", ""),
                    "weight": 0.0,
                },
            }
        }
    }
    return graaaph  # 3 as


def test_edit_weight_minmax():
    import gc

    gc.collect()
    int_proc_2 = setUp(lookit_this=graaaaph())
    assert int_proc_2.intent_graph["mode_in"]["mode_out"][0]["weight"] == 1.0
    assert int_proc_2.intent_graph["mode_in"]["mode_out"][1]["weight"] == 0.0
    int_proc_2.edit_weight(0, "mode_in", "mode_out")
    assert int_proc_2.intent_graph["mode_in"]["mode_out"][0]["weight"] == 0.9
    int_proc_2.edit_weight(1, "mode_in", "mode_out")
    assert int_proc_2.intent_graph["mode_in"]["mode_out"][1]["weight"] == 0.1
