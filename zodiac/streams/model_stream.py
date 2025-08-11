#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from typing import List, Tuple

from toga.sources import Source

nfo = print


class ModelStream(Source):
    async def model_graph(self) -> None:
        """Build an intent graph from models using the IntentProcessor class"""
        from zodiac.graph import IntentProcessor

        self._graph = {}
        self._graph = IntentProcessor()
        await self._graph.calc_graph()

    async def show_edges(self, target: bool = False) -> List[str]:
        """Retrieve and sort edges from the intent graph.\n
        :param target: If True, sorts based on the second element of each edge pair; defaults to False.
        :return: A sorted list of unique elements from the edge pairs."""

        if self._graph.intent_graph:
            edge_pairs = list(self._graph.intent_graph.edges)
            if edge_pairs:
                pair = 0 if not target else 1
                seen = []
                for edge in edge_pairs:
                    if edge[pair] not in seen:
                        seen.append(edge[pair])
                seen.sort(key=len)
                return seen

    async def trace_models(self, mode_in: str, mode_out: str) -> List[Tuple[str, int]]:
        """Trace model path through input to output mode, then updates the internal model list..\n
        :param mode_in: The input mode for tracing.
        :param mode_out: The output mode for tracing.
        :return: A list of traced models."""

        from nnll.monitor.file import dbuq

        self._graph.set_path(mode_in=mode_in, mode_out=mode_out)
        self._graph.set_registry_entries()
        nfo(f"calculated : {self._graph.coord_path}")
        dbuq(f"calculated : {self._graph.coord_path} {self._graph.registry_entries}")
        self._models = self._graph.models
        return self._models

    async def chart_path(self) -> List[str]:
        """Return hop names of current path\n
        :return: List of [x,y,z] node names along the chosen path
        """
        return self._graph.coord_path

    def __len__(self):
        return len(list(self._models()))

    def __getitem__(self, index):
        return self._models()[index]

    def index(self, entry):
        return self._models().index(entry)

    async def clear(self):
        self._models = []
        self.notify("clear")
