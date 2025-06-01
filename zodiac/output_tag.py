#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from textual.reactive import reactive
from textual.screen import Screen
from nnll.monitor.file import debug_monitor
from zodiac.carousel import Carousel


class OutputTag(Carousel):
    """Populate Output types list"""

    target_options: reactive[set] = reactive({})

    def on_mount(self) -> None:
        scrn = self.query_ancestor(Screen)
        if scrn.int_proc.has_graph():
            graph_edges = scrn.int_proc.intent_graph.edges

            self.target_options = sorted({edge[0] for edge in graph_edges}, key=len)
            self.add_columns("0", "1", "2")
            self.add_rows([self.up.strip(), row.strip(), self.dwn.strip()] for row in self.target_options)
            self.cursor_foreground_priority = "css"
            self.cursor_background_priority = "css"

    @debug_monitor
    def skip_to(self, name="text") -> None:
        """Jump current tag to an index # and change panel context if required\n
        :param id_name: Name of the panel to switch to
        :param top: Whether or not the request comes from in or out tag
        """

        self.scroll_to(x=1, y=self.target_options.index(name), force=True, immediate=True, on_complete=self.refresh)
