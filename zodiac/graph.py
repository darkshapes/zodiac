#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-outside-toplevel


import sys
import os
import networkx as nx
from typing import Optional, Any
# pylint:disable=import-outside-toplevel

from nnll.monitor.file import debug_monitor, nfo, dbug
from mir.provider_pools import register_models  # leaving here for mocking

sys.path.append(os.getcwd())


class IntentProcessor:
    intent_graph: Optional[dict[nx.Graph]] = None
    coord_path: Optional[list[str]] = None
    registry_entries: Optional[list[dict[dict]]] = None
    models: Optional[list[tuple[str]]] = None
    weight_idx: Optional[list[str]] = None
    # additional_model_names: dict = None

    def __init__(self, intent_graph: nx.MultiDiGraph = nx.MultiDiGraph()) -> None:
        """
        Create instance of graph processor & initialize objectives for tracing paths\n
        :param nx_graph:Preassembled graph of models to substitute, default uses nx.MultiDiGraph()

        ========================================================\n
        ### GIVEN\n
        A : The list of `VALID CONVERSIONS` contains all of Zodiac's supported generative modalities\n
        B : The graph is populated directly from the contents of the list in A\n
        Thus: All possible node start and end points listed in A are included in graph B.\n
        Therefore : It is impossible to call a node that does not exist.\n
        """
        from mir.constants import VALID_CONVERSIONS  # , RegistryEntry,

        self.intent_graph = intent_graph
        self.intent_graph.add_nodes_from(VALID_CONVERSIONS)

    @debug_monitor
    def calc_graph(self, registry_entries: Optional[list] = None) -> None:
        """Generate graph of coordinate pairs from valid conversions\n
        Model libraries are auto-detected from cache loading\n
        :param registry_data: Registry function or method of calling registry, defaults to
        :return: Graph modeling all current ML/AI tasks appended with model data

        ========================================================\n
        ### GIVEN\n
        A : The set of all models M on the executing system\n
        B : P is the randomly distributed set of start and end points required to graph M\n
        Thus: Because of the randomness of B, the set P is unlikely to construct a complete graph attached all available points.\n
        Therefore : While we can trust a node exists, we **CANNOT** trust the system has an edge to reach it\n
        """
        if not registry_entries:
            registry_entries = register_models()
        nfo("Building graph...")
        if registry_entries is None:
            nfo("Registry error, graph attributes not applied.")
        elif len(self.intent_graph.edges) > 0:
            nfo("Edges already calculated")
            return self.intent_graph
        else:
            for model in registry_entries:
                try:
                    self.intent_graph.add_edges_from(model.available_tasks, entry=model, weight=1.0)
                except AttributeError as error_log:
                    dbug(error_log)
                    nfo("Error: Registry initialized but not populated with data. Graph could not create edges.")
        nfo(f"Complete {self.intent_graph}")
        return self.intent_graph

    @debug_monitor
    def has_graph(self) -> bool:
        """A check to verify the graph has been created"""
        try:
            assert self.intent_graph is not None
        except AssertionError as error_log:
            dbug(error_log)
            return False
        return True

    @debug_monitor
    def has_path(self) -> bool:
        """A check to verify the path has been created"""
        try:
            assert self.coord_path is not None
        except AssertionError as error_log:
            dbug(error_log)
            return False
        return True

    @debug_monitor
    def has_registry_entries(self) -> bool:
        """A check to verify model checkpoints are available"""
        try:
            assert self.registry_entries is not None
            assert len(self.registry_entries) >= 1
        except AssertionError as error_log:
            dbug(error_log)
            return False
        return True

    @debug_monitor
    def set_path(self, mode_in: str, mode_out: str) -> None:
        """Find a valid path from current state (mode_in) to designated state (mode_out)\n
        :param mode_in: Input prompt type or starting state/states
        :type mode_in: str
        :param mode_out: The user-selected ending-state
        :type mode_out: str
        """

        self.has_graph()
        if nx.has_path(self.intent_graph, mode_in, mode_out):  # Ensure path exists (otherwise 'bidirectional' may loop infinitely)
            # Self loops in the multidirected graph complete themselves
            # In practice, this means often the same model can be used to compute prompt input and response output
            # Unfortunately, this doesn't always work in all modalities, ex. Image to Image.
            # This condition is meant to solve the case of non-text self-loop edge being an incomplete transformation
            if mode_in == mode_out and mode_in != "text":  # Its not a great solution, but it works for the moment
                orig_mode_out = mode_out
                mode_out = "text"
                self.coord_path = nx.bidirectional_shortest_path(self.intent_graph, mode_in, mode_out)
                self.coord_path.append(orig_mode_out)
            else:
                self.coord_path = nx.bidirectional_shortest_path(self.intent_graph, mode_in, mode_out)
                if len(self.coord_path) == 1:
                    self.coord_path.append(mode_out)  # this behaviour likely to change in future
        else:
            nfo("No Path available...")

    @debug_monitor
    def set_registry_entries(self) -> None:
        """Populate models list for text fields
        Check if model has been adjusted, if so adjust list
        1.0 weight bottom, <1.0 weight top"""
        self.has_graph()
        self.has_path()
        try:
            self.registry_entries = self.pull_path_entries(self.intent_graph, self.coord_path)
        except KeyError as error_log:
            dbug(error_log)
            return ["", ""]
        idx = 0
        self.models = []
        if self.registry_entries:
            for edge, registry in enumerate(self.registry_entries):
                model = registry["entry"].model
                nfo(f"node {edge}")
                adj_model = (os.path.basename(model), edge)
                self.models.append(adj_model)
            self.weight_idx = self.weight_idx or []
            for model in self.weight_idx:
                if model in self.models:
                    self.models.remove(model)
                    adj_model = (f"*{model[0]}", model[1])
                    self.models.insert(idx, adj_model)
                    idx += 1

    @debug_monitor
    def edit_weight(self, selection: str, mode_in: str, mode_out: str) -> None:
        """Determine entry edge, determine index, then adjust weight\n
        :param selection: Text pattern from `models` class attribute to identify the model by
        :param mode_in: The conversion type, representing a source graph node
        :param mode_out: The target type, , representing a source graph node
        :raises ValueError: No models fit the request
        """
        from mir.mir_maid import MIRDatabase

        self.weight_idx = self.weight_idx or []
        try:
            if not nx.has_path(self.intent_graph, mode_in, mode_out):
                raise KeyError()
            target = os.path.basename(self.intent_graph[mode_in][mode_out][selection]["entry"].model)
        except KeyError as error_log:
            nfo(f"Failed to adjust weight of '{selection}' within registry contents '{self.intent_graph} {mode_in} {mode_out}'. Model or registry entry not found. ")
            dbug(error_log)
            return self.set_registry_entries()
        entries = []
        for index, reg in self.intent_graph[mode_in][mode_out].items():
            entries.append([reg["entry"].model, index, "", ""])
        nfo(f"graph weight : {entries} {mode_in} {mode_out} {target} \n")
        edge, _ = MIRDatabase.grade_char_match(entries, target)
        nfo(edge)
        entries = []
        if edge is None:
            self.set_registry_entries()
            return
        model = self.intent_graph[mode_in][mode_out][edge]["entry"].model
        weight = self.intent_graph[mode_in][mode_out][edge]["weight"]
        item = (os.path.basename(model), edge)
        nfo(f" model : {model}  weight: {weight} ")
        if weight < 1.0:
            self.intent_graph[mode_in][mode_out][edge]["weight"] = round(weight + 0.1, 1)
            self.models = [((f"*{os.path.basename(model)}", edge))]
            if item in self.weight_idx:
                self.weight_idx.remove(item)
        else:
            self.intent_graph[mode_in][mode_out][edge]["weight"] = round(weight - 0.1, 1)
            self.weight_idx.append(item)
        nfo(self.intent_graph[mode_in][mode_out][edge])
        self.set_registry_entries()

    @debug_monitor
    def pull_path_entries(self, nx_graph: nx.Graph, traced_path: list[tuple]) -> None:
        """Create operating instructions from user input
        Trace the next hop along the path, collect all compatible models
        Set current model based on weight and next available"""

        registry_entries = []
        if traced_path is not None and nx.has_path(nx_graph, traced_path[0], traced_path[1]):
            registry_entries = [  # ruff : noqa
                nx_graph[traced_path[i]][traced_path[i + 1]][hop]  #
                for i in range(len(traced_path) - 1)  #
                for hop in nx_graph[traced_path[i]][traced_path[i + 1]]  #
            ]
        return registry_entries
