from __future__ import annotations

from systems.terminal_ui import print_text, rule


class Player:
    """Data dan aturan dasar karakter pemain."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.name = "Petualang"
        self.max_hp = 4
        self.hp = self.max_hp
        # Nilai atribut awal 10 adalah nilai rata-rata sementara.
        self.str = 10
        self.dex = 10
        self.int = 10
        self.will = 10
        self.gold = 10

    @staticmethod
    def modifier(score: int) -> int:
        """Mengubah skor atribut menjadi modifier gaya D&D."""
        return (score - 10) // 2

    def show_status(self) -> None:
        rule("STATUS KARAKTER")
        print_text(f"Nama : {self.name}", "story")
        print_text(f"HP   : {self.hp}/{self.max_hp}", "success" if self.hp > 1 else "failure")
        print_text(f"STR  : {self.str} ({self.modifier(self.str):+d})", "status")
        print_text(f"DEX  : {self.dex} ({self.modifier(self.dex):+d})", "status")
        print_text(f"INT  : {self.int} ({self.modifier(self.int):+d})", "status")
        print_text(f"WILL : {self.will} ({self.modifier(self.will):+d})", "status")
        print_text(f"Koin : {self.gold}", "warning")
        rule()
