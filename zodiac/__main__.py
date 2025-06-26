#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=missing-module-docstring, missing-class-docstring,disable=import-error

from textual.app import App
from zodiac.main_screen import Fold


class Combo(App):
    SCREENS = {"fold": Fold}
    CSS_PATH = "combo.tcss"

    def on_mount(self) -> None:
        """Draw screen"""
        self.push_screen("fold")
        self.scroll_sensitivity_y = 1
        self.supports_smooth_scrolling = True
        self.theme = "flexoki"
