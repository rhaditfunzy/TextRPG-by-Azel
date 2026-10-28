from __future__ import annotations

from pathlib import Path
from typing import Any

from player import Player
from dice import DiceSystem
from battle import BattleSystem
from systems.story_loader import StoryLoader
from systems.effects import apply_effects
from systems.terminal_ui import print_text, rule, show_art, loading


class StoryEngine:
    def __init__(
        self,
        player: Player,
        loader: StoryLoader,
        project_dir: Path | None = None,
    ) -> None:
        self.player = player
        self.loader = loader
        self.dice = DiceSystem()
        self.battle = BattleSystem(player, self.dice)
        self.last_story_id: str | None = None
        self.project_dir = (project_dir or Path(__file__).resolve().parent).resolve()

    def play(self, story: dict[str, Any]) -> None:
        self.last_story_id = story["id"]
        node_id = story["start"]
        visited_steps = 0
        rule(f"{story['title']} [{story['type'].upper()}]")

        while node_id and self.player.hp > 0:
            visited_steps += 1
            if visited_steps > 200:
                print_text(
                    "Peringatan: cerita dihentikan karena melewati 200 langkah (kemungkinan loop).",
                    "warning",
                )
                break

            node = story["nodes"][node_id]
            art_path = node.get("art")
            if art_path:
                show_art(str(art_path), self.project_dir)
            print_text(f"\n{node['text']}", "story")
            apply_effects(self.player, node.get("effects"))
            if self.player.hp <= 0:
                break

            choices = node.get("choices", [])
            if node.get("end") or not choices:
                print_text("\n--- Cerita selesai ---", "muted")
                break

            for index, choice in enumerate(choices, 1):
                print_text(f"  {index}. {choice['text']}", "choice")

            selected = self._read_choice(len(choices))
            choice = choices[selected - 1]

            if choice.get("check"):
                check_data = choice["check"]
                loading("Menyiapkan uji atribut...", duration=0.2)
                node_id = self._run_check(check_data)
            elif choice.get("battle"):
                battle_data = choice["battle"]
                won = self.battle.fight(battle_data.get("enemy", {}))
                if self.player.hp <= 0:
                    break
                node_id = battle_data.get("win") if won else battle_data.get("lose")
            else:
                apply_effects(self.player, choice.get("effects"))
                node_id = choice.get("next")

            if not node_id:
                print_text("\n--- Cerita selesai ---", "muted")
                break

        if self.player.hp > 0:
            print_text("\nCerita berakhir. Ketik Ready untuk mendapat cerita berikutnya.", "system")

    @staticmethod
    def _read_choice(number_of_choices: int) -> int:
        while True:
            raw = input("Pilih nomor: ").strip()
            try:
                value = int(raw)
            except ValueError:
                print_text("Masukkan nomor pilihan.", "warning")
                continue
            if 1 <= value <= number_of_choices:
                return value
            print_text(f"Pilih angka 1 sampai {number_of_choices}.", "warning")

    def _run_check(self, check: dict[str, Any]) -> str | None:
        attribute = str(check.get("attribute", "will")).lower()
        difficulty = int(check.get("dc", 10))
        result = self.dice.check(self.player, attribute, difficulty)
        print_text(
            f"\nUji {attribute.upper()}: d20 {result.roll} "
            f"{result.modifier:+d} = {result.total} (target {result.difficulty}).",
            "dice",
        )
        if result.roll == 20:
            print_text("Natural 20! Berhasil.", "success")
        elif result.roll == 1:
            print_text("Natural 1! Gagal.", "failure")
        print_text("Berhasil!" if result.success else "Gagal!", "success" if result.success else "failure")
        branch = "success" if result.success else "failure"
        apply_effects(self.player, check.get(f"{branch}_effects"))
        return check.get(branch)
