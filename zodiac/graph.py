#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=import-outside-toplevel


import sys
import os
import networkx as nx
# pylint:disable=import-outside-toplevel

from nnll_01 import debug_monitor, nfo, dbug
from nnll_15 import from_cache

sys.path.append(os.getcwd())


class IntentProcessor:
    intent_graph = None
    coord_path: list[str] | None = None
    ckpts: list = None
    models: list[tuple[str]] | None = None
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
        from nnll_15 import VALID_CONVERSIONS  # , RegistryEntry,

        self.intent_graph = intent_graph
        self.intent_graph.add_nodes_from(VALID_CONVERSIONS)

    @debug_monitor
    def calc_graph(self, registry_entries: list = from_cache()) -> None:
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
        nfo("Complete {self.intent_graph}")
        return self.intent_graph

    @debug_monitor
    def has_graph(self) -> None:
        """A check to verify the graph has been created"""
        try:
            assert self.intent_graph is not None
        except AssertionError as error_log:
            dbug(error_log)
            return False
        return True

    @debug_monitor
    def has_path(self) -> None:
        """A check to verify the path has been created"""
        try:
            assert self.coord_path is not None
        except AssertionError as error_log:
            dbug(error_log)
            return False
        return True

    @debug_monitor
    def has_ckpt(self) -> None:
        """A check to verify model checkpoints are available"""
        try:
            assert self.ckpts is not None
            assert len(self.ckpts) >= 1
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

    @debug_monitor
    def set_ckpts(self) -> None:
        """Populate models list for text fields and sort by weight\n"""
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
            # nfo("Graph status: ", self.ckpts)
            self.ckpts = sorted(self.ckpts, key=lambda x: x["weight"])
            # nfo("Model weight status: ", [x["weight"] for x in self.ckpts])

            for registry in self.ckpts:
                model = registry["entry"].model
                weight = registry.get("weight")
                if weight != 1.0:
                    self.models.insert(0, (f"*{os.path.basename(model)}", model))
                    nfo("Adjusted model :", f"*{os.path.basename(model)}", weight)
                else:
                    self.models.append((os.path.basename(model), model))
                    # nfo("model : ", model, weight)
            self.models = sorted(self.models, key=lambda x: "*" in x)

    @debug_monitor
    def edit_weight(self, selection: str, mode_in: str, mode_out: str) -> None:
        """Determine entry edge, determine index, then adjust weight\n
        :param selection: Text pattern from `models` class attribute to identify the model by
        :param mode_in: The conversion type, representing a source graph node
        :param mode_out: The target type, , representing a source graph node
        :raises ValueError: No models fit the request
        """
        reg_entries = [nbrdict for n, nbrdict in self.intent_graph.adjacency()]
        try:
            if not reg_entries[0].get(mode_out):  # if there is no model to get to `mode_out`
                raise ValueError("No models available.")
        except (IndexError, ValueError, nx.exception.NodeNotFound) as error_log:  # if there is no edge towards `mode_out`
            dbug(error_log)
            nfo(f"Failed to adjust weight of '{selection}' within registry contents '{reg_entries}'. Model or registry entry not found. ")
        else:
            index = [x for x in reg_entries[0][mode_out] if selection in reg_entries[0][mode_out][x].get("entry").model]
            try:
                model = reg_entries[0][mode_out][index[0]].get("entry").model
            except IndexError as error_log:
                dbug(error_log)
                nfo(f"Failed to locate index for '{selection}' within registry contents '{reg_entries}'.")
            else:
                weight = reg_entries[0][mode_out][index[0]].get("weight")
                nfo("Model pre-adjustment : ", model, index, weight)
                if weight < 1.0:
                    self.intent_graph[mode_in][mode_out][index[0]]["weight"] = round(weight + 0.1, 1)
                else:
                    self.intent_graph[mode_in][mode_out][index[0]]["weight"] = round(weight - 0.1, 1)
                nfo("Weight changed for: ", self.intent_graph[mode_in][mode_out][index[0]]["entry"].model, f"model # {index[0]}")
                dbug("Confirm :", self.intent_graph[mode_in][mode_out])

        finally:
            self.set_ckpts()
