from __future__ import annotations

import random
from player import Player
from dice import DiceSystem
from systems.terminal_ui import print_text, rule


class BattleSystem:
    """Pertarungan giliran sederhana berbasis d20."""

    def __init__(self, player: Player, dice: DiceSystem | None = None) -> None:
        self.player = player
        self.dice = dice or DiceSystem()

    def fight(self, enemy_data: dict) -> bool:
        enemy = {
            "name": str(enemy_data.get("name", "Musuh")),
            "hp": max(1, int(enemy_data.get("hp", 3))),
            "ac": int(enemy_data.get("ac", 10)),
            "attack_bonus": int(enemy_data.get("attack_bonus", 0)),
            "damage_min": max(1, int(enemy_data.get("damage_min", 1))),
            "damage_max": max(1, int(enemy_data.get("damage_max", 2))),
        }
        if enemy["damage_max"] < enemy["damage_min"]:
            enemy["damage_max"] = enemy["damage_min"]

        rule(f"PERTARUNGAN: {enemy['name']}")
        print_text("Ketik A untuk menyerang atau P untuk mencoba pergi.", "muted")

        while self.player.hp > 0 and enemy["hp"] > 0:
            print_text(
                f"\nHP kamu: {self.player.hp}/{self.player.max_hp} | "
                f"HP {enemy['name']}: {enemy['hp']}",
                "status",
            )
            action = input("Aksi [A/P]: ").strip().lower()

            if action in {"p", "pergi"}:
                print_text("Kamu mencoba mundur dari pertarungan...", "warning")
                flee_roll = self.dice.roll(20)
                if flee_roll >= 10:
                    print_text(f"Berhasil melarikan diri (d20={flee_roll}).", "success")
                    return False
                print_text(f"Gagal melarikan diri (d20={flee_roll})!", "failure")
            elif action not in {"a", "serang", "attack"}:
                print_text("Pilihan tidak dikenal. Giliran musuh tetap berjalan.", "warning")
            else:
                roll = self.dice.roll(20)
                mod = self.player.modifier(self.player.str)
                total = roll + mod
                print_text(
                    f"Seranganmu: d20 {roll} {mod:+d} = {total} melawan AC {enemy['ac']}.",
                    "dice",
                )
                if roll == 20 or (roll != 1 and total >= enemy["ac"]):
                    damage = max(1, self.dice.roll(4) + max(0, mod))
                    enemy["hp"] -= damage
                    print_text(f"Serangan mengenai {enemy['name']} dan memberi {damage} damage.", "success")
                else:
                    print_text("Seranganmu meleset.", "failure")

            if enemy["hp"] <= 0:
                print_text(f"Kamu mengalahkan {enemy['name']}!", "success")
                return True

            enemy_roll = self.dice.roll(20)
            player_ac = 10 + max(0, self.player.modifier(self.player.dex))
            enemy_total = enemy_roll + enemy["attack_bonus"]
            print_text(
                f"Serangan musuh: d20 {enemy_roll} + {enemy['attack_bonus']} = "
                f"{enemy_total} melawan AC kamu {player_ac}.",
                "dice",
            )
            if enemy_roll == 20 or (enemy_roll != 1 and enemy_total >= player_ac):
                damage = random.randint(enemy["damage_min"], enemy["damage_max"])
                self.player.hp = max(0, self.player.hp - damage)
                print_text(f"Kamu terkena serangan dan kehilangan {damage} HP.", "failure")
            else:
                print_text("Musuh meleset.", "success")

        return enemy["hp"] <= 0 and self.player.hp > 0
