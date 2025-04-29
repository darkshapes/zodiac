#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# import array
import sounddevice as sd

from textual import work
from textual.reactive import reactive

from textual_plotext import PlotextPlot

from nnll_01 import info_message as nfo  # , debug_monitor


class VoicePanel(PlotextPlot):  # (PlotWidget)
    """Create an unselectable display element"""

    ALLOW_SELECT = False
    audio = [0]
    sample_freq: int = 16000
    duration: float = 3.0
    sample_len: reactive[float] = reactive(0.0, recompose=True)

    def on_mount(self) -> None:
        self.can_focus = True
        # self.theme = "flexoki"

    @work(exclusive=True)
    async def record_audio(self) -> None:
        """Get audio from mic"""
        self.plt.clear_data()
        precision = self.duration * self.sample_freq
        self.audio = [0]
        self.audio = sd.rec(int(precision), samplerate=self.sample_freq, channels=1)
        sd.wait()
        self.graph_audio()

    @work(exclusive=True)
    async def graph_audio(self) -> None:
        """Draw audio waveform"""
        self.plt.frame(0)
        self.plt.canvas_color((0, 0, 0))
        self.can_focus = True
        self.plt.xfrequency("0", "0")
        self.plt.yfrequency("0", "0")
        self.plt.scatter(self.audio[:, 0], marker="braille", color=(128, 0, 255))

    @work(exclusive=True)
    async def play_audio(self) -> None:
        """Playback audio recordings"""
        try:
            sd.play(self.audio, samplerate=self.sample_freq)
            sd.wait()
        except TypeError as error_log:
            nfo(error_log)

    @work(exclusive=True)
    async def erase_audio(self) -> None:
        """Clear audio graph and recording"""
        self.plt.clear_data()
        self.audio = [0]

    def time_audio(self) -> float:
        sample_length = len(self.audio)
        duration = float(sample_length / self.sample_freq) if sample_length > 1 else 0.0
        return duration

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
