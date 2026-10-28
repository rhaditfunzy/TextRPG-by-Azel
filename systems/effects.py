from __future__ import annotations

from typing import Any
from player import Player
from systems.terminal_ui import print_text


def apply_effects(player: Player, effects: dict[str, Any] | None) -> None:
    """Menerapkan efek yang didukung. Nilai bisa positif atau negatif."""
    if not effects:
        return

    if "gold" in effects:
        amount = int(effects["gold"])
        player.gold = max(0, player.gold + amount)
        print_text(f"Efek: koin {'+' if amount >= 0 else ''}{amount} (sekarang {player.gold}).", "warning")

    if "hp" in effects:
        amount = int(effects["hp"])
        player.hp = max(0, min(player.max_hp, player.hp + amount))
        style = "success" if amount > 0 else "failure"
        print_text(f"Efek: HP {'+' if amount >= 0 else ''}{amount} (sekarang {player.hp}/{player.max_hp}).", style)

    if "heal" in effects:
        amount = max(0, int(effects["heal"]))
        old_hp = player.hp
        player.hp = min(player.max_hp, player.hp + amount)
        print_text(f"Efek: pulih {player.hp - old_hp} HP (sekarang {player.hp}/{player.max_hp}).", "success")

    for attribute in ("str", "dex", "int", "will"):
        if attribute in effects:
            amount = int(effects[attribute])
            setattr(player, attribute, max(1, min(30, getattr(player, attribute) + amount)))
            print_text(
                f"Efek: {attribute.upper()} {'+' if amount >= 0 else ''}{amount} "
                f"(sekarang {getattr(player, attribute)}).",
                "status",
            )

    if "max_hp" in effects:
        amount = int(effects["max_hp"])
        player.max_hp = max(1, min(99, player.max_hp + amount))
        player.hp = min(player.hp, player.max_hp)
        print_text(f"Efek: HP maksimum berubah menjadi {player.max_hp}.", "status")
