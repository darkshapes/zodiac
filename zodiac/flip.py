#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from textual.screen import Screen
from textual.reactive import reactive
from textual.widgets import ContentSwitcher
# from nnll_01 import nfo


class Flip(ContentSwitcher):
    """Swap panel top/bottom content"""

    mode_in: reactive[str] = reactive("text")
    mode_out: reactive[str] = reactive("text")
    text_opt = ["message_panel", "response_panel"]
    speech_opt = ["voice_message", "voice_response"]

    def watch_mode_in(self, mode_in: str) -> None:
        """Textual API watch for variable changes\n
        :param mode_in: The value of the incoming intent type
        """
        fold_screen = self.query_ancestor(Screen)
        if fold_screen.is_ui_ready():
            if mode_in == "speech":
                fold_screen.ui["ms"].current = self.speech_opt[0]
            else:
                fold_screen.ui["ms"].current = self.text_opt[0]

    def watch_mode_out(self, mode_out: str) -> None:
        """Textual API watch for variable changes\n
        :param mode_out: The value of the outgoing intent type
        """
        fold_screen = self.query_ancestor(Screen)
        if fold_screen.is_ui_ready():
            if mode_out == "speech":
                fold_screen.ui["rs"].current = self.speech_opt[1]
            else:
                fold_screen.ui["rs"].current = self.text_opt[1]
