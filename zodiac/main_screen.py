#  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3 */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Auto-Orienting Split screen"""

import os
from collections import defaultdict
from typing import Callable  # , Any

from dspy import Module as dspy_Module
from nnll_01 import dbug, debug_monitor  # , nfo
from textual import events, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import ContentSwitcher, Static
from textual.containers import Horizontal

from zodiac.message_panel import MessagePanel
from zodiac.display_bar import DisplayBar
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
        Binding("bk", "alternate_panel('text',0)", "⌨️"),  # Return to text input panel
        Binding("alt+bk", "clear_input", "del"),  # Empty focused prompt panel
        Binding("space", "play", "▶︎", priority=True),  # Listen to prompt audio
        Binding("`", "start_recording", "◉", priority=True),  # Send to LLM
        Binding("ctrl+c", "copy", "⧉", priority=True),
    ]
    id: str = "fold_screen"
    ui: dict = defaultdict(dict)
    int_proc: reactive[Callable] = reactive(None)
    tx_data: dict = {}
    hover_name: reactive[str] = reactive("")
    safety: reactive[int] = reactive(1)
    chat: dspy_Module = None

    def compose(self) -> ComposeResult:
        """Textual API widget constructor, build graph, apply custom widget classes"""
        # from textual.widgets import Footer
        self.int_proc = IntentProcessor()
        self.int_proc.calc_graph()
        self.ready_tx(mode_in="text", mode_out="text")
        with Horizontal(id="app-grid", classes="app-grid-horizontal"):
            yield ResponsiveLeftTop(id="left-frame")
            with Container(id="centre-frame"):  # 3:1:3 ratio
                with Container(id="responsive_input"):  # 3:
                    with ContentSwitcher(initial="message_panel", name="message_swap", id="message_swap"):
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
                    )
                with Container(id="responsive_display"):  # 3
                    with ContentSwitcher(initial="response_panel", name="response_swap", id="response_swap"):
                        yield ResponsePanel("\n", id="response_panel", language="markdown")
                        yield VoicePanel(id="voice_response", name="voice_response", classes="voice_panel")
                    yield OutputTag(id="output_tag", classes="output_tag")
            yield ResponsiveRightBottom(id="right-frame")

    @work(exclusive=True)
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
        self.init_graph()

    @work(exclusive=True)
    async def init_graph(self) -> None:
        """Construct graph"""
        from nnll_11 import ChatMachineWithMemory, QASignature  # modularize Signature

        self.chat = ChatMachineWithMemory(sig=QASignature, max_workers=8)
        if self.int_proc.models is not None:
            self.ready_tx()
            self.walk_intent()
            # id_name = self.input_tag.highlight_link_id

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
        """Recalculate path when models are shown"""
        if event.control.id == "selectah":
            self.ready_tx()
            self.walk_intent()
            self.ui["sl"].prompt = next(iter(self.int_proc.models))[0]

    @work(exclusive=True)
    async def _on_key(self, event: events.Key) -> None:
        """Textual API event trigger, Suppress/augment default key actions to trigger keybindings"""
        if event.key not in ["escape", "ctrl+left_square_brace"]:
            self.safety = min(1, self.safety + 1)
        else:
            if "active" in self.ui["sl"].classes:
                self.stop_gen()
                self.ui["sl"].set_classes(["selectah"])
            self.safe_exit()
        if (hasattr(event, "character") and event.character == "\r") or event.key == "enter" and not (self.ui["sl"].has_focus or self.ui["sl"].has_focus_within):
            event.prevent_default()
            self.ready_tx(io_only=False)
            if self.int_proc.has_graph() and self.int_proc.has_path():
                self.walk_intent(send=True)
        elif (hasattr(event, "character") and event.character == " ") or event.key == "space":
            if self.ui["rd"].has_focus_within:
                self.flip_panel(id_name="voice_response", force=True)
                self.ui["vr"].play_audio()
            elif not self.ui["sl"].has_focus or self.ui["sl"].has_focus_within:
                self.flip_panel(id_name="voice_message", force=True)
                self.ui["vm"].play_audio()
        if (hasattr(event, "character") and event.character == "`") or event.key == "grave_accent":
            if self.ui["rd"].has_focus_within:
                self.flip_panel(id_name="voice_response", force=True)
                self.ui["vr"].record_audio()
                self.audio_to_token(top=False)
            elif not self.ui["sl"].has_focus or self.ui["sl"].has_focus_within:
                self.flip_panel(id_name="voice_message", force=True)
                self.ui["vm"].record_audio()
                self.audio_to_token()
        elif (event.name) == "ctrl_w" or event.key == "ctrl+w":
            self.clear_input()
        elif not self.ui["rp"].has_focus and ((hasattr(event, "character") and event.character == "\x7f") or event.key == "backspace"):
            self.flip_panel(id_name="message_panel", force=True)

    @work(exit_on_error=True)
    async def safe_exit(self) -> None:
        """trigger exit on second press"""
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
    def ready_tx(self, io_only: bool = True, mode_in: str = None, mode_out: str = None) -> None:
        """Retrieve graph data, prepare to send"""
        if not mode_in:
            mode_in = self.ui["it"].get_cell_at((self.ui["it"].current_row, 1))
        if not mode_out:
            mode_out = self.ui["ot"].get_cell_at((self.ui["ot"].current_row, 1))
        self.int_proc.set_path(mode_in=mode_in, mode_out=mode_out)
        self.int_proc.set_ckpts()
        if not io_only:
            self.tx_data = {
                "text": self.ui["mp"].text,
                "speech": self.ui["vm"].audio,
                # "attachment": self.message_panel.file # drag and drop from external window
                # "image": self.image_panel.image #  active video feed / screenshot / import file
            }

    # @work(exclusive=True)
    def walk_intent(self, send=False) -> None:
        """Provided the coordinates in the intent processor, follow the list of in and out methods"""
        coords = self.int_proc.coord_path
        if not coords:
            coords = ["text", "text"]
        hops = len(coords) - 1
        for i in range(hops):
            if i + 1 < hops:
                if send:
                    self.send_tx()
                    self.ready_tx(mode_in=coords[i + 1], mode_out=coords[i + 2])
                else:  # This allows us to predict the models required for a pass
                    old_models = self.int_proc.models if self.int_proc.models else []
                    dbug(old_models, "walk_intent")
                    self.ready_tx(mode_in=coords[i + 1], mode_out=coords[i + 2])
                    self.int_proc.models.extend(old_models)
                    dbug(self.int_proc.models)

            elif send:
                self.send_tx()

    @work(exclusive=True)
    async def send_tx(self) -> None:
        """Transfer path and promptmedia to generative processing endpoint
        :param last_hop: Whether this is the user-determined objective or not"""
        self.ui["rp"].on_text_area_changed()
        self.ui["rp"].insert("\n---\n")
        self.ui["sl"].add_class("active")
        ckpt = self.ui["sl"].selection
        if ckpt is None:
            ckpt = next(iter(self.int_proc.ckpts)).get("entry")
        try:
            self.tx_data = self.ui["rp"].pass_req(chat=self.chat, tx_data=self.tx_data, ckpt=ckpt, out_type=self.ui["ot"].current_cell)
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
            self.ui["vm"].erase_audio()
            self.audio_to_token()
        elif self.ui["rd"].has_focus_within:
            self.ui["vr"].erase_audio()
            self.audio_to_token(top=False)
        elif self.ui["mp"].has_focus:
            self.ui["mp"].erase_message()

    # @work(exclusive=True)
    async def flip_panel(self, id_name: str, force: bool = True) -> None:
        """Switch between text and audio panels\n
        :param top: Whether to rotate top panel or bottom
        :param id: Panel name to flip to
        :param force: Skip to the tag corresponding to the panel
        """
        # self.ui["it"].scroll_to(x=1, y=2, force=True, immediate=True, on_complete=self.ui["it"].refresh)
        # self.ui["ps"].current = id_name
        if id_name in ["message_panel", "voice_message"]:
            self.ui["ms"].current = id_name
            if force:
                # get the position of speech and move to it
                self.ui["it"].skip_to(top=True)

        elif id_name in ["response_panel", "voice_response"]:
            self.ui["rs"].current = id_name
            if force:
                # get the position of speech and move to it
                self.ui["ot"].skip_to(top=False)


class ResponsiveLeftTop(Container):
    """Sidebar Left/Top"""

    def compose(self) -> ComposeResult:
        yield Static()


class ResponsiveRightBottom(Container):
    """Sidebar Right/Bottom"""

    def compose(self) -> ComposeResult:
        yield Static()
        yield Static()
