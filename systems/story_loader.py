from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

VALID_TYPES = {"short", "medium", "long"}


class StoryLoader:
    """Memuat semua cerita JSON dari folder stories/ secara rekursif."""

    def __init__(self, stories_dir: str | Path = "stories") -> None:
        self.stories_dir = Path(stories_dir)
        self.stories: list[dict[str, Any]] = []
        self.errors: list[str] = []
        self.reload()

    def reload(self) -> None:
        self.stories.clear()
        self.errors.clear()
        if not self.stories_dir.exists():
            self.errors.append(f"Folder cerita tidak ditemukan: {self.stories_dir}")
            return
        seen_ids: set[str] = set()
        for path in sorted(self.stories_dir.rglob("*.json")):
            try:
                with path.open("r", encoding="utf-8") as file:
                    story = json.load(file)
                self._validate(story, path)
                story_id = story["id"]
                if story_id in seen_ids:
                    raise ValueError(f"ID cerita duplikat: {story_id}")
                seen_ids.add(story_id)
                story["_source_file"] = str(path)
                self.stories.append(story)
            except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
                self.errors.append(f"{path}: {exc}")

    @staticmethod
    def _validate(story: Any, path: Path) -> None:
        if not isinstance(story, dict):
            raise ValueError("Isi JSON harus berupa object.")
        for key in ("id", "title", "type", "start", "nodes"):
            if key not in story:
                raise ValueError(f"Field wajib tidak ada: {key}")
        if story["type"] not in VALID_TYPES:
            raise ValueError("type harus 'short', 'medium', atau 'long'.")
        if not isinstance(story["nodes"], dict) or not story["nodes"]:
            raise ValueError("nodes harus berupa object yang tidak kosong.")
        if story["start"] not in story["nodes"]:
            raise ValueError(f"Node awal '{story['start']}' tidak ditemukan.")
        for node_id, node in story["nodes"].items():
            if not isinstance(node, dict) or "text" not in node:
                raise ValueError(f"Node '{node_id}' harus berupa object dan memiliki text.")
            if "art" in node and not isinstance(node["art"], str):
                raise ValueError(f"Field art di node '{node_id}' harus berupa path string.")
            if not isinstance(node.get("choices", []), list):
                raise ValueError(f"choices di node '{node_id}' harus berupa list.")
            for choice in node.get("choices", []):
                if not isinstance(choice, dict) or "text" not in choice:
                    raise ValueError(f"Pilihan di node '{node_id}' harus memiliki text.")
                destinations = [choice.get("next")]
                check = choice.get("check")
                battle = choice.get("battle")
                if check:
                    destinations.extend([check.get("success"), check.get("failure")])
                if battle:
                    destinations.extend([battle.get("win"), battle.get("lose")])
                for destination in destinations:
                    if destination is not None and destination not in story["nodes"]:
                        raise ValueError(f"Tujuan '{destination}' pada node '{node_id}' tidak ditemukan.")

    def pick_random(self, previous_id: str | None = None) -> dict[str, Any] | None:
        if not self.stories:
            return None
        candidates = [story for story in self.stories if story["id"] != previous_id]
        if not candidates:
            candidates = self.stories[:]
        return random.choice(candidates)
