#  # # <!-- // /*  SPDX-License-Identifier: blessing) */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-outside-toplevel


import sys
import os


# pylint:disable=import-outside-toplevel
sys.path.append(os.getcwd())

import networkx as nx
from nnll_01 import debug_monitor, info_message as nfo, debug_message as dbug

# from nnll_15.constants import ModeType
from nnll_15 import RegistryEntry


class IntentProcessor:
    intent_graph: nx.Graph = None
    coord_path: list[str] = None
    ckpts: list[dict[RegistryEntry]] = None
    models: list[tuple[str]] = None
    # additional_model_names: dict = None

    def __init__(self) -> None:
        """
        Create instance of graph processor & initialize objectives for tracing paths
        """

    @debug_monitor
    def calc_graph(self) -> None:
        """Generate graph of coordinate pairs from valid conversions\n
        Model libraries are auto-detected from cache loading\n
        :param nx_graph: Preassembled graph of models to label
        :return: Graph modeling all current ML/AI tasks appended with model data"""
        from nnll_15 import VALID_CONVERSIONS, from_cache

        self.intent_graph = nx.MultiDiGraph()
        self.intent_graph.add_nodes_from(VALID_CONVERSIONS)
        registry_entries = from_cache()
        if registry_entries:
            for model in registry_entries:
                self.intent_graph.add_edges_from(model.available_tasks, entry=model, weight=1.0)
        else:
            nfo("Registry error, graph attributes not applied")
        return self.intent_graph

    @debug_monitor
    def has_graph(self) -> None:
        """Verify the graph has been created"""
        try:
            assert self.intent_graph is not None
        except AssertionError as error_log:
            dbug(error_log)
            return False
        return True

    @debug_monitor
    def has_path(self) -> None:
        """Verify the path has been created"""
        try:
            assert self.coord_path is not None
        except AssertionError as error_log:
            dbug(error_log)
            return False
        return True

    @debug_monitor
    def has_ckpt(self) -> None:
        """Verify the model checkpoints are known"""
        try:
            assert self.ckpts is not None
        except AssertionError as error_log:
            dbug(error_log)
            return False
        return True

    @debug_monitor
    def set_path(self, mode_in: str, mode_out: str) -> None:
        """
        Find a valid path from current state (mode_in) to designated state (mode_out)\n
        :param mode_in: Input prompt type or starting state/states
        :param mode_out: The user-selected ending-state
        :return: An iterator for the edges forming a way towards the mode out, or Note
        """

        self.has_graph()
        if nx.has_path(self.intent_graph, mode_in, mode_out):  # Ensure path exists (otherwise 'bidirectional' may loop infinitely)
            if mode_in == mode_out and mode_in != "text":
                orig_mode_out = mode_out  # Solve case of non-text self-loop edge being incomplete transformation
                mode_out = "text"
                self.coord_path = nx.bidirectional_shortest_path(self.intent_graph, mode_in, mode_out)
                self.coord_path.append(orig_mode_out)
            else:
                self.coord_path = nx.bidirectional_shortest_path(self.intent_graph, mode_in, mode_out)
                if len(self.coord_path) == 1:
                    self.coord_path.append(mode_out)  # this behaviour likely to change in future

    @debug_monitor
    def set_ckpts(self) -> None:
        from nnll_05 import pull_path_entries

        self.has_graph()
        self.has_path()
        try:
            self.ckpts = pull_path_entries(self.intent_graph, self.coord_path)
        except KeyError as error_log:
            dbug(error_log)
            return ["", ""]
        if len(self.ckpts) != 0:
            self.models = []
            nfo(self.ckpts)
            self.ckpts = sorted(self.ckpts, key=lambda x: x["weight"])
            nfo([x["weight"] for x in self.ckpts])
            for registry in self.ckpts:
                model = registry["entry"].model
                weight = registry.get("weight")
                if weight != 1.0:
                    self.models.insert(0, (f"*{os.path.basename(model)}", model))
                    nfo("adjusted model :", f"*{os.path.basename(model)}", weight)
                else:
                    self.models.append((os.path.basename(model), model))
                    # nfo("model : ", model, weight)
            self.models = sorted(self.models, key=lambda x: "*" in x)

    @debug_monitor
    def edit_weight(self, selection: str, mode_in: str, mode_out: str) -> None:
        """Determine entry edge, determine index, then adjust weight"""
        reg_entries = [nbrdict for n, nbrdict in self.intent_graph.adjacency()]
        if not reg_entries[0].get(mode_out):
            raise ValueError("No models available.")
        index = [x for x in reg_entries[0][mode_out] if selection in reg_entries[0][mode_out][x].get("entry").model]
        model = reg_entries[0][mode_out][index[0]].get("entry").model
        weight = reg_entries[0][mode_out][index[0]].get("weight")
        nfo(model, index, weight)
        if weight < 1.0:
            self.intent_graph[mode_in][mode_out][index[0]]["weight"] = weight + 0.1
        else:
            self.intent_graph[mode_in][mode_out][index[0]]["weight"] = weight - 0.1
        nfo("Weight changed for: ", self.intent_graph[mode_in][mode_out][index[0]]["entry"].model, f"model # {index[0]}")
        self.set_ckpts()
        dbug("Confirm :", self.intent_graph[mode_in][mode_out])
