#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=missing-module-docstring, disable=missing-class-docstring

from textual import events, on
from textual.app import App

# from nnll.monitor.file import nfo
from zodiac.main_screen import Fold  # pylint: disable=import-error

# from theme import fluoresce_theme


class Combo(App):
    SCREENS = {"fold": Fold}
    CSS_PATH = "combo.tcss"

    def on_mount(self) -> None:
        """Draw screen"""
        self.push_screen("fold")
        self.scroll_sensitivity_y = 1
        self.supports_smooth_scrolling = True
        self.theme = "flexoki"
