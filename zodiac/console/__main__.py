#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=missing-module-docstring, missing-class-docstring, import-error,import-outside-toplevel

from textual.app import App
from zodiac.console.main_screen import Fold


class Combo(App):
    SCREENS = {"fold": Fold}
    CSS_PATH = "combo.tcss"

    def on_mount(self) -> None:
        """Draw screen"""
        self.push_screen("fold")
        self.scroll_sensitivity_y = 1
        self.supports_smooth_scrolling = True
        self.theme = "flexoki"


def main() -> None:
    """Launch textual UI"""
    from nnll.monitor.console import nfo

    app = Combo(ansi_color=False)
    nfo("Launching...")
    app.run()  # also takes output_file as an optional argument


if __name__ == "__main__":
    main()
