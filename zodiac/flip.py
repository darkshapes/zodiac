from textual.screen import Screen
from textual.reactive import reactive
from textual.widgets import ContentSwitcher
from nnll_01 import nfo


class Flip(ContentSwitcher):
    mode_in: reactive[str] = reactive("text")
    mode_out: reactive[str] = reactive("text")
    text_opt = ["message_panel", "response_panel"]
    speech_opt = ["voice_message", "voice_response"]

    def watch_mode_in(self, mode_in: str) -> None:
        """Textual API watch for variable changes\n
        :param mode_in: The value of the incoming intent type
        """
        if self.query_ancestor(Screen).is_ui_ready():
            if self.mode_in == "speech":
                self.current = self.speech_opt[0]
            else:
                self.current = self.text_opt[0]

    def watch_mode_out(self, mode_out: str) -> None:
        """Textual API watch for variable changes\n
        :param mode_out: The value of the outgoing intent type
        """
        if self.query_ancestor(Screen).is_ui_ready():
            if mode_out == "speech":
                self.current = self.speech_opt[1]
            else:
                self.current = self.text_opt[1]
