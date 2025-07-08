#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

import sounddevice as sd
from nnll.monitor.file import dbuq


class AudioMachine:
    audio_stream = [0]
    frequency = 0
    duration: float = 3.0
    precision = duration * frequency
    sample_length = 0.0


async def record_audio(self, frequency: int = 16000) -> None:
    """Get audio from mic"""
    self.frequency = frequency
    self.audio_stream = [0]
    self.audio_stream = sd.rec(int(self.precision), samplerate=self.frequency, channels=1)
    sd.wait()
    self.sample_length = str(float(len(self.audio_stream) / frequency))
    return self.audio_stream


async def play_audio(self) -> None:
    """Playback audio recordings"""
    try:
        sd.play(self.audio_stream, samplerate=self.frequency)
        sd.wait()
    except TypeError as error_log:
        dbuq(error_log)


async def erase_audio(self) -> None:
    """Clear audio graph and recording"""
    self.audio_stream = [0]
    self.frequency = 0.0
    self.sample_length = 0.0
