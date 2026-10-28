from __future__ import annotations

import random
from dataclasses import dataclass

from player import Player
from systems.terminal_ui import animate_roll


@dataclass
class CheckResult:
    roll: int
    modifier: int
    total: int
    difficulty: int
    success: bool


class DiceSystem:
    """Dadu d20 dan pemeriksaan atribut; animasi hanya bersifat visual."""

    ATTRIBUTES = {"str", "dex", "int", "will"}

    def roll(self, sides: int = 20) -> int:
        if sides < 2:
            raise ValueError("Dadu harus memiliki setidaknya 2 sisi.")
        animate_roll(sides)
        return random.randint(1, sides)

    def check(self, player: Player, attribute: str, difficulty: int) -> CheckResult:
        attribute = attribute.lower()
        if attribute not in self.ATTRIBUTES:
            raise ValueError(f"Atribut tidak dikenal: {attribute}")
        roll = self.roll(20)
        modifier = player.modifier(getattr(player, attribute))
        total = roll + modifier
        success = (roll == 20) or (roll != 1 and total >= difficulty)
        return CheckResult(roll, modifier, total, difficulty, success)
