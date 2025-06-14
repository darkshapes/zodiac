#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Auto-Orienting Split screen"""

# pylint: disable=protected-access

import asyncio
import multiprocessing as mp
import os
from collections import defaultdict
from typing import Any, Callable, Union  # , Any

import psutil
from dspy import Module as dspy_Module
from mir.registry_entry import RegistryEntry
from nnll.monitor.file import dbug, debug_monitor, nfo
from textual import events, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Static

from zodiac.chat_machine import BasicImageSignature, VectorMachine, QASignature
from zodiac.display_bar import DisplayBar
from zodiac.flip import Flip
from zodiac.graph import IntentProcessor
from zodiac.input_tag import InputTag
from zodiac.message_panel import MessagePanel
from zodiac.output_tag import OutputTag
from zodiac.response_panel import ResponsePanel
from zodiac.selectah import Selectah
from zodiac.voice_panel import VoicePanel

lock = asyncio.Lock()

fds = psutil.Process(os.getpid()).open_files()
for item in fds:
    num = item[1]
    os.set_inheritable(num, False)

mp.set_start_method("spawn", force=True)


class Fold(Screen[bool]):
    """Orienting display Horizontal
    Main interface container"""

    DEFAULT_CSS = """Screen { min-height: 5; }"""

    BINDINGS = [
        # Binding("ent", "", "✉︎", priority=True),
        Binding("escape", "stop_gen", "◼︎ / ⏏︎"),  # Cancel response/Safe
        Binding("bk", "ui['it'].skip_to('text')", "⌨️"),  # Return to text input panel
        Binding("alt+backspace", "clear_input()", "del"),  # Empty focused prompt panel
        Binding("space", "ui['it'].skip_to('speech')", "▶︎", priority=True),  # Listen to prompt audio
        Binding("`", "", "◉", priority=True),  # Record Audio
        Binding("ctrl+c", "copy", "⧉", priority=True),
    ]
    id: str = "fold_screen"
    ui: dict = defaultdict(dict)
    int_proc: reactive[Callable] = reactive(None)
    tx_data: dict = {}
    hover_name: reactive[str] = reactive("")
    safety: reactive[int] = reactive(1)
    chat: dspy_Module = VectorMachine(max_workers=8)  # and this

    mode_in: reactive[str] = reactive("text")
    mode_out: reactive[str] = reactive("text")
    models: reactive[list[tuple[str, str]]] = reactive([("", "")])

    def compose(self) -> ComposeResult:
        """Textual API widget constructor, build graph, apply custom widget classes"""
        # from textual.widgets import Footer
        from mir.registry_entry import from_cache

        self.int_proc = IntentProcessor()

        self.int_proc.calc_graph(from_cache())
        nfo("Graph calculated.")
        with Horizontal(id="app-grid", classes="app-grid-horizontal"):
            yield ResponsiveLeftTop(id="left-frame")
            with Container(id="centre-frame"):  # 3:1:3 ratio
                with Container(id="responsive_input"):  # 3:
                    with Flip(initial="message_panel", name="message_swap", id="message_swap").data_bind(mode_in=Fold.mode_in):
                        yield MessagePanel("""""", id="message_panel", max_checkpoints=100).focus()
                        yield VoicePanel(name="voice_message", id="voice_message", classes="voice_message")
                    yield InputTag(id="input_tag", classes="input_tag")
                with Horizontal(id="seam"):
                    yield DisplayBar(id="display_bar")  # 1:
                    yield Selectah(
                        id="selectah",
                        classes="selectah",
                        prompt=os.path.basename(next(iter(self.int_proc.models))[0]) if self.int_proc.models is not None else "No model",
                        # value=next(iter(self.int_proc.models))[1], # this forces the first option to be weighted immediately
                        options=self.int_proc.models if self.int_proc.models is not None else [("No model", "No models")],
                        type_to_search=True,
                        # allow_blank=False,
                    ).data_bind(mode_in=Fold.mode_in, mode_out=Fold.mode_out)
                with Container(id="responsive_display"):  # 3
                    with Flip(initial="response_panel", name="response_swap", id="response_swap").data_bind(mode_out=Fold.mode_out):
                        yield ResponsePanel("\n", id="response_panel", language="markdown")
                        yield VoicePanel(id="voice_response", name="voice_response", classes="voice_panel")
                    yield OutputTag(id="output_tag", classes="output_tag")
            yield ResponsiveRightBottom(id="right-frame")

    # @work(exclusive=True)
    def on_mount(self) -> None:
        """Textual API, Query all available widgets at once"""
        self.ui["db"] = self.query_one("#display_bar")
        self.ui["sl"] = self.query_one("#selectah")
        self.ui["ri"] = self.query_one("#responsive_input")
        self.ui["it"] = self.query_one("#input_tag")
        self.ui["mp"] = self.query_one("#message_panel")
        self.ui["vm"] = self.query_one("#voice_message")
        self.ui["ot"] = self.query_one("#output_tag")  # type : ignore
        self.ui["rd"] = self.query_one("#responsive_display")
        self.ui["rp"] = self.query_one("#response_panel")
        self.ui["vr"] = self.query_one("#voice_response")
        self.ui["ms"] = self.query_one("#message_swap")
        self.ui["rs"] = self.query_one("#response_swap")
        self.ui["mp"].focus()
        self.next_intent()

    @work(exit_on_error=False)
    async def on_resize(self, event=events.Resize) -> None:
        """Textual API, scale/orientation screen responsivity"""
        if self.is_ui_ready():
            display = self.query_one("#app-grid")
            width = event.container_size.width
            height = event.container_size.height
            if width / 2 >= height:  # Screen is wide
                display.set_classes("app-grid-horizontal")
            elif width / 2 < height:  # Screen is tall
                display.set_classes("app-grid-vertical")

    @debug_monitor
    def is_ui_ready(self) -> bool:
        """Confirm UI is active"""
        try:
            selector = hasattr(self.ui["sl"], "is_mounted")
            message = hasattr(self.ui["ms"], "is_mounted")
            response = hasattr(self.ui["rs"], "is_mounted")
        except AttributeError as error_log:
            dbug(error_log)
            return False
        else:
            if selector and message and response:
                return True

    @on(events.Focus)
    async def on_focus(self, event=events.Focus) -> None:
        """Textual API event trigger, Recalculate path when models are shown"""
        if event.control.id == "selectah":
            self.next_intent()

    @work(exclusive=True)
    async def focus_on_sel(self) -> bool:
        """Textual API event trigger, Check selectah focus"""
        return self.ui["sl"].has_focus  # or self.ui["sl"].has_focus_within

    @work(group="key_events", exclusive=True)
    async def _on_key(self, event: events.Key) -> None:
        """Textual API event trigger, Suppress/augment default key actions to trigger keybindings"""

        def is_key(key: str) -> bool:
            return event.key == key

        def is_char(char: str, key: str) -> bool:
            if is_key(key):
                return hasattr(event, "character") and event.character == char
            return False

        if event.name == "ctrl_w" or is_key("ctrl+w"):
            self.clear_input()

        elif not self.ui["rp"].has_focus and is_char("\x7f", "backspace"):
            self.mode_in = "text"
            self.ui["it"].skip_to(self.mode_in)

        if is_key("escape") or is_key("ctrl+left_square_brace"):
            if "active" in self.ui["sl"].classes or self.ui["sl"].expanded:
                self.stop_gen()
            else:
                nfo(f" exit focus {self.focus_on_sel()}")
                self.safe_exit()
        else:
            self.safety = min(1, self.safety + 1)
        if (hasattr(event, "character") and event.character == "\r") or event.key == "enter":
            event.prevent_default()
            self.next_intent(io_only=False, bypass_send=False)

        if is_char("\r", "enter"):
            event.prevent_default()
            self.ui["rp"].workers.cancel_group(self.ui["rp"], "chat")
            self.ui["sl"].set_classes("selectah")
            model_name = await self.pull_registry_entry(model=True)
            self.notify(message=f"Awaiting reply from {os.path.basename(model_name)}...", title="Active", severity="information")
            self.ui["sl"].add_class("active")
            self.next_intent(io_only=False, bypass_send=False)

        elif is_char(" ", "space"):
            if self.ui["rd"].has_focus_within:
                self.notify("Playing prompt audio...", severity="information")
                self.mode_out = "speech"
                self.ui["ot"].skip_to(self.mode_out)
                self.ui["vr"].play_audio()
            else:
                self.notify("Playing response audio...", severity="information")
                self.mode_in = "speech"
                self.ui["it"].skip_to(self.mode_in)
                self.ui["vm"].play_audio()

        if is_char("`", "grave_accent"):
            await self.notify_recording()
            self.mode_in = "speech"
            self.ui["it"].skip_to(self.mode_in)
            await self.ui["vm"].record_audio()
            await self.audio_to_token()

    async def notify_recording(self):
        self.notify("Recording audio...", severity="information")
        return None

    @work(exit_on_error=True)
    async def safe_exit(self) -> None:
        """Notify first press, trigger exit on second press"""
        self.safety = max(0, self.safety)
        if self.safety == 0:
            await self.app.action_quit()
        self.safety -= 1
        self.notify("Press ESC again to quit", severity="error")

    # @work(exclusive=True)
    @on(MessagePanel.Changed, "#message_panel")
    async def txt_to_token(self) -> None:
        """Transmit info to token calculation"""
        message = self.ui["mp"].text
        if self.int_proc.models:
            token_model = await self.pull_registry_entry(model=True)
            self.ui["db"].show_tokens(token_model, message=message)

    async def audio_to_token(self, top: bool = True) -> None:
        """Transmit audio to sample length
        :param top: Selector for audio panel top or bottom
        """
        panel = "vm" if top else "vr"
        if self.ui[panel].sample_freq > 1:
            duration = len(self.ui[panel].audio) / self.ui[panel].sample_freq
        else:
            duration = 0.0
        duration = self.ui["db"].show_time(duration)
        return duration

    # @work(exclusive=True)
    def ready_tx(
        self,
        io_only: bool = True,
        mode_in: reactive[str] = mode_in._default,
        mode_out: reactive[str] = mode_out._default,
    ) -> None:
        """Retrieve graph data, prepare to send"""

        self.int_proc.set_path(mode_in=mode_in, mode_out=mode_out)
        self.int_proc.set_registry_entries()
        nfo(f"triggered recalculation : {self.int_proc.coord_path} {self.int_proc.registry_entries}")
        if not io_only:
            self.tx_data = {
                "text": self.ui["mp"].text,
                "speech": self.ui["vm"].audio,
                # "attachment": self.message_panel.file # drag and drop from external window
                # "image": self.image_panel.image #  active video feed / screenshot / import file
            }

    # @work(exclusive=True)
    async def walk_intent(self, bypass_send=True) -> None:
        """Provided the coordinates in the intent processor, follow the list of in and out methods\n
        :param bypass_send: Find intent path, but do not process, defaults to True
        """
        coords = self.int_proc.coord_path
        hops = len(coords) - 1
        for i in range(hops):
            if i + 1 < hops:
                if not bypass_send:
                    self.send_tx()
                    self.ready_tx(mode_in=coords[i + 1], mode_out=coords[i + 2])
                else:  # This allows us to predict the models required for a pass
                    old_models = self.int_proc.models if self.int_proc.models else []
                    dbug("walk_intent", old_models)
                    self.ready_tx(mode_in=coords[i + 1], mode_out=coords[i + 2])
                    self.int_proc.models.extend(old_models)
                    dbug(self.int_proc.models)

            elif not bypass_send:
                self.send_tx()

    @work(group="chat", exclusive=True)
    async def send_tx(self) -> Any:
        """Transfer path and promptmedia to generative processing endpoint
        :param last_hop: Whether this is the user-determined objective or not"""

        self.ui["rp"].move_cursor(self.ui["rp"].document.end)
        self.ui["rp"].insert("\n---\n")
        self.ui["sl"].add_class("active")
        streaming = self.mode_out == "text"
        edge_data = await self.pull_registry_entry()
        registry_entries = edge_data["entry"]
        if self.mode_out == "image":
            sig = BasicImageSignature
        else:
            sig = QASignature
        if registry_entries != self.chat.registry_entries or self.chat.streaming != streaming or sig != self.chat.sig or not self.chat.recycle:
            dbug(f"Graph extraction : {registry_entries}")
            self.chat.active_models(registry_entries=registry_entries, sig=sig, streaming=streaming)
        self.ui["rp"].synthesize(chat=self.chat, tx_data=self.tx_data, mode_out=self.mode_out)

    def stop_gen(self) -> None:
        """Cancel the inference processing of a model"""
        self.ui["rp"].workers.cancel_all()
        self.notify("Cancelled processing!", severity="error")
        self.ui["sl"].set_classes("selectah")

    @work(exclusive=True)
    async def clear_input(self) -> None:
        """Clear the input on the focused panel"""
        if self.ui["ri"].has_focus_within:
            if self.ui["mp"].has_focus:
                self.ui["mp"].erase_message()
                self.notify("Text prompt emptied.", severity="error", markup=True)  # [@click="undo_clear()"]UNDO[/]""", )
            else:
                await self.ui["vm"].erase_audio()
                await self.audio_to_token()
                self.notify("Audio prompt emptied.", severity="error")
                return None
        elif self.ui["rd"].has_focus_within:
            await self.ui["vr"].erase_audio()
            self.notify("Audio prompt emptied.", severity="error")
            await self.audio_to_token(top=False)
            return None

    async def watch_mode_in(self, mode_in: str) -> None:  # pylint: disable=unused-argument
        """Textual API event trigger, Recalculate path when input is changed"""
        if self.is_ui_ready():
            self.next_intent()

    async def watch_mode_out(self, mode_out: str) -> None:  # pylint: disable=unused-argument
        """Textual API event trigger, Recalculate path when output is changed"""
        if self.is_ui_ready():
            self.next_intent()

    @work(exclusive=True)
    async def next_intent(self, io_only: bool = True, bypass_send: bool = True) -> None:
        """Store user input, calculate path data, repopulate fields and prepare execution/n
        :param io_only: Ignore user prompt and gather input types only, defaults to True
        :param bypass_send: Make a dry run that plots the generation path only, defaults to True
        """
        self.ready_tx(io_only=io_only, mode_in=self.mode_in, mode_out=self.mode_out)
        if self.int_proc.has_graph() and self.int_proc.has_path():
            await self.walk_intent(bypass_send=bypass_send)
        if not hasattr(self.ui["sl"], "prompt") or self.int_proc.models is None:
            nfo("intent processor models not available")
        elif self.int_proc.models is None and hasattr(self.ui.get("sl"), "prompt"):
            self.ui["sl"].set_options = [("No models", "No Models.")]
        elif hasattr(self.ui["sl"], "prompt"):
            self.ui["sl"].set_options(self.int_proc.models)
            self.ui["sl"].prompt = next(iter(self.int_proc.models))[0]

    async def pull_registry_entry(self, model: bool = False) -> Union[RegistryEntry, dict]:
        """Determine the RegistryEntry\n
        :param model: Provide only model attribute of RegistryEntry, defaults to False
        :return: _description_
        """

        edge = next(iter(self.int_proc.models))[1]
        registry_entry = self.int_proc.intent_graph[self.mode_in][self.mode_out][edge]
        if not model:
            return registry_entry
        return registry_entry["entry"].model


class ResponsiveLeftTop(Container):
    """Sidebar Left/Top"""

    def compose(self) -> ComposeResult:
        yield Static()


class ResponsiveRightBottom(Container):
    """Sidebar Right/Bottom"""

    def compose(self) -> ComposeResult:
        yield Static()
        yield Static()
