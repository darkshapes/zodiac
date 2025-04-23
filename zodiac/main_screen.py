#  # # <!-- // /*  SPDX-License-Identifier: blessing) */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

"""Auto-Orienting Split screen"""

import os
from collections import defaultdict
from typing import Callable  # , Any
from textual import events, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen

# from textual.widget import Widget
from textual.widgets import Static, ContentSwitcher  # , DataTable

from nnll_01 import debug_monitor, info_message as nfo, debug_message as dbug
from zodiac.message_panel import MessagePanel
from zodiac.graph import IntentProcessor
from zodiac.input_tag import InputTag
from zodiac.output_tag import OutputTag
from zodiac.selectah import Selectah


class Fold(Screen[bool]):
    """Orienting display Horizontal
    Main interface container"""

    DEFAULT_CSS = """Screen { min-height: 5; }"""

    BINDINGS = [
        Binding("bk", "alternate_panel('text',0)", "⌨️"),  # Return to text input panel
        Binding("alt+bk", "clear_input", "del"),  # Empty focused prompt panel
        Binding("ent", "start_recording", "◉", priority=True),  # Start audio prompt
        Binding("space", "play", "▶︎", priority=True),  # Listen to prompt audio
        Binding("escape", "cancel_generation", "◼︎ / ⏏︎"),  # Cancel response
        Binding("`", "loop_sender", "✎", priority=True),  # Send to LLM
    ]

    ui: dict = defaultdict(dict)
    int_proc: reactive[Callable] = reactive(None)
    tx_data: dict = {}
    counter = 0
    hover_name: reactive[str] = reactive("")
    input_map: dict = {
        "text": "message_panel",
        "image": "message_panel",
        "speech": "voice_panel",
    }

    def compose(self) -> ComposeResult:
        """Textual API widget constructor, build graph, apply custom widget classes"""
        from textual.containers import Horizontal
        from textual.widgets import Footer
        from zodiac.display_bar import DisplayBar

        from zodiac.response_panel import ResponsePanel
        from zodiac.voice_panel import VoicePanel

        self.int_proc = IntentProcessor()
        self.int_proc.calc_graph()
        self.ready_tx(mode_in="text", mode_out="text")
        yield Footer(id="footer")
        with Horizontal(id="app-grid", classes="app-grid-horizontal"):
            yield ResponsiveLeftTop(id="left-frame")
            with Container(id="centre-frame"):  # 3:1:3 ratio
                with Container(id="responsive_input"):  # 3:
                    with ContentSwitcher(id="panel_swap", initial="message_panel"):
                        yield MessagePanel("""""", id="message_panel", max_checkpoints=100)
                        yield VoicePanel(id="voice_panel")
                    yield InputTag(id="input_tag", classes="input_tag")
                with Horizontal(id="seam"):
                    yield DisplayBar(id="display_bar")  # 1:
                    yield Selectah(
                        id="selectah",
                        classes="selectah",
                        prompt=os.path.basename(next(iter(self.int_proc.models))[0]) if self.int_proc.models is not None else "No model",
                        options=self.int_proc.models if self.int_proc.models is not None else [("No model", "No models")],
                        type_to_search=True,
                    )
                with Container(id="responsive_display"):  #
                    yield ResponsePanel("\n", id="response_panel", language="markdown")
                    yield OutputTag(id="output_tag", classes="output_tag")
            yield ResponsiveRightBottom(id="right-frame")

    @work(exclusive=True)
    async def on_mount(self) -> None:
        """Textual API, Query all available widgets at once"""
        self.ui["db"] = self.query_one("#display_bar")
        self.ui["it"] = self.query_one("#input_tag")
        self.ui["mp"] = self.query_one("#message_panel")
        self.ui["ot"] = self.query_one("#output_tag")  # type : ignore
        self.ui["ps"] = self.query_one(ContentSwitcher)
        self.ui["rd"] = self.query_one("#responsive_display")
        self.ui["rp"] = self.query_one("#response_panel")
        self.ui["vp"] = self.query_one("#voice_panel")
        self.ui["sl"] = self.query_one("#selectah")
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
        if (hasattr(event, "character") and event.character == "`") or event.key == "grave_accent":
            event.prevent_default()
            self.ready_tx(io_only=False)
            if self.int_proc.has_graph() and self.int_proc.has_path():
                self.walk_intent(send=True)
        elif event.key == "escape" and "active" in self.ui["sl"].classes:
            Message.stop(True)
            self.stop_gen()
        elif (hasattr(event, "character") and event.character == "\r") or event.key == "enter":
            self.flip_panel("voice_panel", 1)
            self.ui["vp"].record_audio()
            self.audio_to_token()
        elif (hasattr(event, "character") and event.character == " ") or event.key == "space":
            self.flip_panel("voice_panel", 1)
            self.ui["vp"].play_audio()
        elif (event.name) == "ctrl_w" or event.key == "ctrl+w":
            self.clear_input()
        elif not self.ui["rp"].has_focus and ((hasattr(event, "character") and event.character == "\x7f") or event.key == "backspace"):
            self.flip_panel("message_panel", 0)

    @debug_monitor
    def _on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        """Textual API event trigger, Translate scroll events into datatable cursor movement
        Trigger scroll at 1/10th intensity when menu has focus
        :param event: Event data for the trigger"""

        scroll_delta = [self.ui["it"].current_cell, self.ui["ot"].current_cell]
        if self.ui["rd"].has_focus_within != self.ui["rp"].has_focus and not self.ui["sl"].has_focus:
            event.prevent_default()
            self.ui["ot"].emulate_scroll(direction=1)
        elif self.ui["it"].has_focus:
            event.prevent_default()
            mode_in_name = self.ui["it"].emulate_scroll(direction=1)
            self.ui["ps"].current = self.input_map.get(mode_in_name)
        if scroll_delta != [self.ui["it"].current_cell, self.ui["ot"].current_cell]:
            self.ready_tx()
            self.walk_intent()
            self.ui["sl"].mode_in = self.ui["it"].current_cell
            self.ui["sl"].mode_out = self.ui["ot"].current_cell
            self.ui["sl"].prompt = next(iter(self.int_proc.models))[0]

    @debug_monitor
    def _on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Textual API event trigger,Translate scroll events into datatable cursor movement
        Trigger scroll at 1/10th intensity when menu has focus
        :param event: Event data for the trigger"""

        scroll_delta = [self.ui["it"].current_cell, self.ui["ot"].current_cell]
        if self.ui["rd"].has_focus_within != self.ui["rp"].has_focus and not self.ui["sl"].has_focus:
            event.prevent_default()
            self.ui["ot"].emulate_scroll(direction=-1)
        elif self.ui["it"].has_focus:
            event.prevent_default()
            mode_name = self.ui["it"].emulate_scroll(direction=-1)
            self.ui["ps"].current = self.input_map.get(mode_name)
        if scroll_delta != [self.ui["it"].current_cell, self.ui["ot"].current_cell]:
            self.ready_tx()
            self.walk_intent()
            self.ui["sl"].mode_in = self.ui["it"].current_cell
            self.ui["sl"].mode_out = self.ui["ot"].current_cell
            self.ui["sl"].prompt = next(iter(self.int_proc.models))[0]

    # @work(exclusive=True)
    @on(MessagePanel.Changed, "#message_panel")
    async def txt_to_token(self) -> None:
        """Transmit info to token calculation"""
        message = self.ui["mp"].text
        next_model = next(iter(self.int_proc.models))[1]
        self.ui["db"].show_tokens(next_model, message=message)

    @work(exclusive=True)
    async def audio_to_token(self) -> None:
        """Transmit audio to sample length"""
        duration = self.ui["vp"].time_audio()
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
                "audio": self.ui["vp"].audio,
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
                    self.tx_data = self.send_tx(last_hop=False)
                    self.ready_tx(mode_in=coords[i + 1], mode_out=coords[i + 2])
                else:
                    old_models = self.int_proc.models if self.int_proc.models else []
                    dbug(old_models, "walk_intent")
                    self.ready_tx(mode_in=coords[i + 1], mode_out=coords[i + 2])
                    self.int_proc.models.extend(old_models)
                    dbug(self.int_proc.models)

            elif send:
                self.send_tx()

    @work(exclusive=True)
    async def send_tx(self, last_hop=True) -> None:
        """Transfer path and promptmedia to generative processing endpoint
        :param last_hop: Whether this is the user-determined objective or not"""

        from nnll_11 import ChatMachineWithMemory, QASignature

        ckpt = self.ui["sl"].selection
        if ckpt is None:
            ckpt = next(iter(self.int_proc.ckpts)).get("entry")
        chat = ChatMachineWithMemory(sig=QASignature)
        self.ui["rp"].on_text_area_changed()
        self.ui["rp"].insert("\n---\n")
        self.ui["sl"].add_class("active")
        if last_hop:
            nfo(ckpt)
            async for chunk in chat.forward(tx_data=self.tx_data, model=ckpt.model, library=ckpt.library, max_workers=8):
                if chunk is not None:
                    self.ui["rp"].insert(chunk)
            self.ui["sl"].set_classes(["selectah"])
        else:
            self.tx_data = chat.forward(tx_data=self.tx_data, model=ckpt.model, library=ckpt.library, max_workers=8)

    @work(exclusive=True)
    async def stop_gen(self) -> None:
        """Cancel the inference processing of a model"""
        self.ui["rp"].workers.cancel_all()
        self.ui["ot"].set_classes("output_tag")

    @work(exclusive=True)
    async def clear_input(self) -> None:
        """Clear the input on the focused panel"""
        if self.ui["vp"].has_focus:
            self.ui["vp"].erase_audio()
            self.audio_to_token()
        elif self.ui["mp"].has_focus:
            self.ui["mp"].erase_message()

    @work(exclusive=True)
    async def flip_panel(self, id_name: str, y_coord: int) -> None:
        """Switch between text input and audio input
        :param id_name: The panel to switch to
        :param y_coordinate: _description_
        """
        self.ui["it"].scroll_to(x=1, y=y_coord, force=True, immediate=True, on_complete=self.ui["it"].refresh)
        self.ui["ps"].current = id_name


class ResponsiveLeftTop(Container):
    """Sidebar Left/Top"""

    def compose(self) -> ComposeResult:
        yield Static()


class ResponsiveRightBottom(Container):
    """Sidebar Right/Bottom"""

    def compose(self) -> ComposeResult:
        yield Static()
        yield Static()
