#  # # <!-- // /*  SPDX-License-Identifier: blessing */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

from textual import work
from textual.reactive import reactive
from textual.widgets import DataTable
from zodiac.token_counters import tk_count


class DisplayBar(DataTable):
    """Thin instant user feedback display"""

    UNIT1 = "chr /   "  # Display Bar Units
    UNIT2 = "tkn / "
    UNIT3 = "″"
    unit_labels = [UNIT1, UNIT2, UNIT3]
    duration: reactive[float] = reactive(0.0, recompose=True)

    def on_mount(self) -> None:
        rows: list[tuple] = [
            (0, 0, 0, 0),
            (f"     0{self.UNIT1}", f"0{self.UNIT2}", f"0.0{self.UNIT3}", " "),
        ]
        self.add_columns(*rows[0])
        self.add_rows(rows[1:])
        self.show_header = False
        self.show_row_labels = False
        self.cursor_type = None

    @work(exclusive=True)
    async def show_tokens(self, tokenizer_model: str, message: str) -> None:
        """Live display of tokens and characters"""
        token_count = await tk_count(tokenizer_model, message)
        character_count = len(message)
        self.update_cell_at((0, 0), f"     {character_count}{self.unit_labels[0]}")
        self.update_cell_at((0, 1), f"{token_count}{self.unit_labels[1]}")
        self.update_cell_at((0, 2), f"{self.duration}{self.unit_labels[2]}")

    @work(exclusive=True)
    async def show_time(self, duration: float) -> None:
        """Live display of sound recording length"""
        self.duration = duration if duration > 0.0 else 0.0
        self.update_cell_at((0, 2), f"{self.duration}{self.unit_labels[2]}", update_width=True)
