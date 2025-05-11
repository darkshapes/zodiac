# #  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
# #  # # <!-- // /*  d a r k s h a p e s */ -->

from pytest import raises


def setUp(lookit_this):
    import networkx as nx
    from zodiac.graph import IntentProcessor

    proc_name = IntentProcessor()  # Replace with actual class name
    proc_name.intent_graph = nx.Graph(lookit_this)
    assert proc_name.has_graph() is True
    proc_name.set_path("mode_in", "mode_out")
    proc_name.set_ckpts()
    assert proc_name.has_path() is True
    assert proc_name.has_ckpt() is True
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
    int_proc.edit_weight("🤡1", "mode_in", "mode_out")
    assert int_proc.intent_graph["mode_in"]["mode_out"][0]["weight"] == 0.6, "Weight not updated correctly"
    int_proc.edit_weight("🤡2", "mode_in", "mode_out")
    assert int_proc.intent_graph["mode_in"]["mode_out"][1]["weight"] == 1.1, "Weight not decreased correctly"


def test_edit_weight_model_not_present():
    with raises(IndexError) as excinfo:
        int_proc.edit_weight("nonexistent", "mode_in", "mode_out")
    assert str(excinfo.value) == "list index out of range"


def test_edit_weight_node_not_present():
    int_proc.intent_graph.remove_node("mode_out")
    with raises(ValueError) as excinfo:
        int_proc.edit_weight("🤡1", "mode_in", "mode_out")
    assert str(excinfo.value) == "No models available.", "ValueError message mismatch"


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

    int_proc_2.edit_weight("🤡3", "mode_in", "mode_out")
    assert int_proc_2.intent_graph["mode_in"]["mode_out"][0]["weight"] == 0.9, "Weight not updated correctly"
    int_proc_2.edit_weight("🤡4", "mode_in", "mode_out")
    assert int_proc_2.intent_graph["mode_in"]["mode_out"][1]["weight"] == 0.1, "Weight not decreased correctly"
