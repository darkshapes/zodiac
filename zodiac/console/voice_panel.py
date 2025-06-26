#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# import array

from textual import work
from textual.reactive import reactive
from textual_plotext import PlotextPlot
from zodiac.audio_machine import AudioMachine


class VoicePanel(PlotextPlot):  # (PlotWidget)
    """Create an unselectable display element"""

    snd = AudioMachine()
    ALLOW_SELECT = False
    sample_len: reactive[str] = reactive(snd.sample_length, recompose=True)

    def on_mount(self) -> None:
        self.can_focus = True
        self.blur()
        # self.theme = "flexoki"

    async def graph_audio(self) -> None:
        """Draw audio waveform"""
        self.clear_audio()
        self.audio = self.snd.record_audio()
        self.plt.frame(0)
        self.plt.canvas_color((0, 0, 0))
        self.can_focus = True
        self.plt.xfrequency("0", "0")
        self.plt.yfrequency("0", "0")
        self.plt.scatter(self.audio[:, 0], marker="braille", color=(128, 0, 255))

    async def replay(self) -> None:
        self.snd.play_audio()

    async def clear_audio(self) -> None:
        self.snd.erase_audio()
        self.plt.clear_data()

    # from textual_plot import PlotWidget, HiResMode
    # to use PlotWidget
    # self.clear()
    # self.set_xticks([])
    # self.set_yticks([])
    # self.set_xlabel("")
    # self.set_ylabel("")
    # self.set_styles("background: #333333;")
    # self.scatter([i for i in range(0, len(self.audio))], self.audio[:, 0], hires_mode=HiResMode.BRAILLE, marker_style="purple")

    # self.clear()
