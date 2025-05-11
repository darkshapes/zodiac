#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Auto-Orienting Split screen"""

# pylint: disable=protected-access

import os
from collections import defaultdict
from typing import Any, Callable  # , Any

from dspy import Module as dspy_Module
from nnll_01 import dbug, debug_monitor, nfo
from textual import events, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Horizontal

from zodiac.message_panel import MessagePanel
from zodiac.display_bar import DisplayBar
from zodiac.flip import Flip
from zodiac.graph import IntentProcessor
from zodiac.input_tag import InputTag
from zodiac.output_tag import OutputTag
from zodiac.response_panel import ResponsePanel
from zodiac.selectah import Selectah
from zodiac.voice_panel import VoicePanel


class Fold(Screen[bool]):
    """Orienting display Horizontal
    Main interface container"""

    DEFAULT_CSS = """Screen { min-height: 5; }"""

    BINDINGS = [
        Binding("ent", "send_tx", "✉︎", priority=True),  # Start audio prompt
        Binding("escape", "stop_gen", "◼︎ / ⏏︎"),  # Cancel response/Safe
        Binding("bk", "ui['ot'].skip_to(text)", "⌨️"),  # Return to text input panel
        Binding("alt+backspace", "clear_input()", "del"),  # Empty focused prompt panel
        Binding("space", "alternate_panel", "▶︎", priority=True),  # Listen to prompt audio
        Binding("`", "key_space", "◉", priority=True),  # Send to LLM
        Binding("ctrl+c", "copy", "⧉", priority=True),
    ]
    id: str = "fold_screen"
    ui: dict = defaultdict(dict)
    int_proc: reactive[Callable] = reactive(None)
    tx_data: dict = {}
    hover_name: reactive[str] = reactive("")
    safety: reactive[int] = reactive(1)
    chat: dspy_Module = None
    mode_in: reactive[str] = reactive("text")
    mode_out: reactive[str] = reactive("text")
    models: reactive[list[tuple[str, str]]] = reactive([("", "")])

    def compose(self) -> ComposeResult:
        """Textual API widget constructor, build graph, apply custom widget classes"""
        # from textual.widgets import Footer
        self.int_proc = IntentProcessor()
        self.int_proc.calc_graph()
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
    async def on_mount(self) -> None:
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

    # # @work(exclusive=True)
    # async def init_graph(self) -> None:
    #     """Construct graph"""
    #     if self.int_proc.models is not None:
    #         self.next_intent()
    #         # id_name = self.input_tag.highlight_link_id

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
            assert hasattr(self.ui["sl"], "is_mounted")
        except AssertionError as error_log:
            dbug(error_log)
            return False
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

    @work(exclusive=True)
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
                self.ui["sl"].set_classes(["selectah"])
            else:
                nfo(f" exit focus {self.focus_on_sel()}")
                self.safe_exit()
        else:
            self.safety = min(1, self.safety + 1)
        if (hasattr(event, "character") and event.character == "\r") or event.key == "enter":
            event.prevent_default()
            self.next_intent(io_only=False, bypass_send=False)

        # if is_char("\r", "enter"):
        #     event.prevent_default()
        #     self.next_intent(io_only=False, bypass_send=False)

        elif is_char(" ", "space"):
            if self.ui["rd"].has_focus_within:
                self.mode_out = "speech"
                self.ui["ot"].skip_to(self.mode_out)
                self.ui["vr"].play_audio()
            else:
                self.mode_in = "speech"
                self.ui["it"].skip_to(self.mode_in)
                self.ui["vm"].play_audio()

        if is_char("`", "grave_accent"):
            self.mode_in = "speech"
            self.ui["it"].skip_to(self.mode_in)
            self.ui["vm"].record_audio()
            self.audio_to_token()

    @work(exit_on_error=True)
    async def safe_exit(self) -> None:
        """Notify first press, trigger exit on second press"""
        self.safety = max(0, self.safety)
        if self.safety == 0:
            await self.app.action_quit()
        self.safety -= 1
        self.notify("Press ESC again to quit")

    # @work(exclusive=True)
    @on(MessagePanel.Changed, "#message_panel")
    async def txt_to_token(self) -> None:
        """Transmit info to token calculation"""
        message = self.ui["mp"].text
        if self.int_proc.models:
            next_model = next(iter(self.int_proc.models))[1]
            self.ui["db"].show_tokens(next_model, message=message)

    @work(exclusive=True)
    async def audio_to_token(self, top: bool = True) -> None:
        """Transmit audio to sample length
        :param top: Selector for audio panel top or bottom
        """
        panel = "vm" if top else "vr"
        duration = self.ui[panel].time_audio()
        self.ui["db"].show_time(duration)

    # @work(exclusive=True)
    def ready_tx(
        self,
        io_only: bool = True,
        mode_in: reactive[str] = mode_in._default,
        mode_out: reactive[str] = mode_out._default,
    ) -> None:
        """Retrieve graph data, prepare to send"""

        self.int_proc.set_path(mode_in=mode_in, mode_out=mode_out)
        self.int_proc.set_ckpts()
        if not io_only:
            self.tx_data = {
                "text": self.ui["mp"].text,
                "speech": self.ui["vm"].audio,
                # "attachment": self.message_panel.file # drag and drop from external window
                # "image": self.image_panel.image #  active video feed / screenshot / import file
            }

    @work(exclusive=True)
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
        self.ui["rp"].on_text_area_changed()
        self.ui["rp"].insert("\n---\n")
        self.ui["sl"].add_class("active")
        ckpt = self.ui["sl"].selection
        if ckpt is None:
            ckpt = next(iter(self.int_proc.ckpts)).get("entry")

        from nnll_11 import QASignature  # , BasicImageSignature

        nfo(f"Graph extraction : {ckpt}")
        sig = QASignature
        if self.mode_out == "image":
            # sig = BasicImageSignature

            from nnll_05 import lookup_function_for
            # from nnll_64 import run_inference

            constructor, mir_arch = lookup_function_for(ckpt.model)
            dbug(constructor, mir_arch)
            multiproc(mir_arch)
            self.ui["sl"].set_classes(["selectah"])
        else:  # lora is arg 2
            try:
                self.ui["rp"].pass_req(sig=sig, tx_data=self.tx_data, ckpt=ckpt, out_type=self.mode_out)
                self.ui["rp"].on_text_area_changed()
            except (GeneratorExit, RuntimeError, ExceptionGroup) as error_log:
                dbug(error_log)
                self.ui["sl"].set_classes(["selectah"])

    @work(exclusive=True)
    async def stop_gen(self) -> None:
        """Cancel the inference processing of a model"""
        self.ui["rp"].workers.cancel_all()
        self.ui["ot"].set_classes("output_tag")

    @work(exclusive=True)
    async def clear_input(self) -> None:
        """Clear the input on the focused panel"""
        if self.ui["ri"].has_focus_within:
            if self.ui["mp"].has_focus:
                self.ui["mp"].erase_message()
            self.ui["vm"].erase_audio()
            self.audio_to_token()
        elif self.ui["rd"].has_focus_within:
            self.ui["vr"].erase_audio()
            self.audio_to_token(top=False)

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
            self.walk_intent(bypass_send=bypass_send)
        if not hasattr(self.ui["sl"], "prompt") or self.int_proc.models is None:
            pass
        elif self.int_proc.models is None and hasattr(self.ui.get("sl"), "prompt"):
            self.ui["sl"].set_options = [("No models", "No Models.")]
        elif hasattr(self.ui["sl"], "prompt"):
            self.ui["sl"].set_options(self.int_proc.models)
            self.ui["sl"].prompt = next(iter(self.int_proc.models))[0]


class ResponsiveLeftTop(Container):
    """Sidebar Left/Top"""

    def compose(self) -> ComposeResult:
        yield Static()


class ResponsiveRightBottom(Container):
    """Sidebar Right/Bottom"""

    def compose(self) -> ComposeResult:
        yield Static()
        yield Static()
