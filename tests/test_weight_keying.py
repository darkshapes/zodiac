def test_weight_key_error():
    import networkx as nx
    from nnll.monitor.console import nfo
    from zodiac.graph import IntentProcessor

    faux_int = IntentProcessor()
    faux_int.intent_graph = nx.MultiDiGraph()
    faux_intent_graph = faux_int.intent_graph

    class FauxEntry:
        model: str

    x = FauxEntry()
    x.model = "THUDM/CogView3-Plus-3B"
    y = FauxEntry()
    y.model = "microsoft/Phi-4-multimodal-instruct"
    z = FauxEntry()
    z.model = "shuttleai/shuttle-3.1-aesthetic"
    faux_intent_graph.add_node("image")
    faux_intent_graph.add_node("text")

    faux_int.intent_graph.add_edges_from([("image", "text", {"entry": x, "weight": 1.0})])
    faux_int.intent_graph.add_edges_from([("image", "text", {"entry": y, "weight": 1.0})])
    faux_int.intent_graph.add_edges_from([("image", "text", {"entry": z, "weight": 1.0})])
    nfo(faux_int.intent_graph.nodes)
    nfo(faux_int.intent_graph.edges.data())

    faux_int.edit_weight(edge_number=2, mode_in="image", mode_out="text")


# graph_edge[index]["weight"] = round(weight - 0.1, 1)
