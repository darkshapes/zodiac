#  # # <!-- // /*  SPDX-License-Identifier: blessing) */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=missing-module-docstring, disable=missing-class-docstring

from textual import work, events, on
from textual.app import App
from textual.binding import Binding
from textual.reactive import reactive

# from nnll_01 import info_message as nfo
from zodiac.main_screen import Fold  # pylint: disable=import-error

# from theme import fluoresce_theme


class Combo(App):
    SCREENS = {"fold": Fold}
    CSS_PATH = "combo.tcss"
    BINDINGS = [Binding("escape", "safe_exit", "◼︎ / ⏏︎")]  # Cancel response

    safety: reactive[int] = reactive(1)

    def on_mount(self) -> None:
        """Draw screen"""
        self.push_screen("fold")
        self.scroll_sensitivity_y = 1
        self.supports_smooth_scrolling = True
        self.theme = "flexoki"

    @work(exit_on_error=True)
    @on(events.Key)
    async def _on_key(self, event: events.Key) -> None:
        """Window for triggering key bindings"""
        if event.key not in ["escape", "ctrl+left_square_brace"]:
            self.safety += 1
        else:
            self.safety -= 1
            if self.safety < 0:
                event.prevent_default()

                await self.app.action_quit()
