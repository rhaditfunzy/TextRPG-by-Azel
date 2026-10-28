from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Iterable

try:
    from rich.console import Console
    from rich.text import Text
    from rich.theme import Theme

    _theme = Theme({
        "title": "bold bright_cyan",
        "story": "white",
        "choice": "bright_magenta",
        "system": "bright_cyan",
        "success": "bold bright_green",
        "failure": "bold bright_red",
        "warning": "bold bright_yellow",
        "status": "bright_yellow",
        "muted": "dim",
        "battle": "bold bright_red",
        "dice": "bold bright_magenta",
    })
    console = Console(theme=_theme, highlight=False)
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False

# Fallback ANSI colors if Rich is not installed. Windows Terminal and modern
# PowerShell/CMD support ANSI sequences; plain text is used when redirected.
ANSI = {
    "title": "\033[96;1m", "story": "\033[97m", "choice": "\033[95m",
    "system": "\033[96m", "success": "\033[92;1m", "failure": "\033[91;1m",
    "warning": "\033[93;1m", "status": "\033[93m", "muted": "\033[2m",
    "battle": "\033[91;1m", "dice": "\033[95;1m",
}
RESET = "\033[0m"


def print_text(message: object = "", style: str | None = None, *, end: str = "\n") -> None:
    """Print colored text using Rich, with an ANSI/plain-text fallback."""
    text = str(message)
    if RICH_AVAILABLE:
        console.print(Text(text, style=style or ""), end=end)
        return
    if style and sys.stdout.isatty() and os.environ.get("NO_COLOR") is None:
        print(f"{ANSI.get(style, '')}{text}{RESET}", end=end)
    else:
        print(text, end=end)


def rule(title: str = "") -> None:
    if RICH_AVAILABLE:
        console.rule(title, style="system")
    else:
        label = f" {title} " if title else ""
        print("=" * max(12, 60 - len(label)) + label)


def loading(message: str = "Menyiapkan petualangan...", duration: float = 0.45) -> None:
    """Short, optional transition animation; never blocks for long."""
    if os.environ.get("TEXTRPG_NO_ANIMATION") == "1" or not sys.stdout.isatty():
        print_text(message, "muted")
        return
    frames = ["|", "/", "-", "\\"]
    start = time.monotonic()
    i = 0
    try:
        while time.monotonic() - start < max(0.0, duration):
            frame = frames[i % len(frames)]
            if RICH_AVAILABLE:
                console.print(f"[system]{frame} {message}[/system]", end="\r", markup=True, soft_wrap=True)
            else:
                sys.stdout.write(f"\r{ANSI['system']}{frame} {message}{RESET}")
                sys.stdout.flush()
            time.sleep(0.075)
            i += 1
        if RICH_AVAILABLE:
            console.print(" " * (len(message) + 3), end="\r")
        else:
            sys.stdout.write("\r" + " " * (len(message) + 3) + "\r")
            sys.stdout.flush()
    except (KeyboardInterrupt, OSError):
        pass


def animate_roll(sides: int = 20, duration: float = 0.65) -> None:
    """Visual-only animation. It does not roll or modify random numbers."""
    if os.environ.get("TEXTRPG_NO_ANIMATION") == "1" or not sys.stdout.isatty():
        return
    frames = [
        ["     .-------.", "    /       /|", "   /  DICE / |", "   '-------' |", "   |   ?   | /", "   '-------'"],
        ["      .-------.", "     /       /|", "    /  DICE / |", "    '-------' |", "    |  ??   | /", "    '-------'"],
        ["   .-------.", "  /       /|", " /  DICE / |", " '-------' |", " |  ???  | /", " '-------'"],
    ]
    label = f"Melempar d{sides}..."
    try:
        for frame in frames:
            # Clear the previous frame, then redraw it.
            if RICH_AVAILABLE:
                console.print("\033[2J\033[H", end="")
                for line in frame:
                    console.print(Text(line, style="dice"))
                console.print(Text(label, style="muted"))
            else:
                sys.stdout.write("\033[2J\033[H")
                sys.stdout.write(ANSI["dice"] + "\n".join(frame) + RESET + "\n" + label + "\n")
                sys.stdout.flush()
            time.sleep(duration / len(frames))
        print_text("", end="\n")
    except (KeyboardInterrupt, OSError):
        # Animation interruption must not affect the actual dice roll.
        pass


def show_art(relative_path: str, project_dir: Path) -> bool:
    """Display an optional UTF-8 ASCII-art file. Returns True if displayed."""
    # Prevent story JSON from reading files outside the project's art folder.
    art_root = (project_dir / "art").resolve()
    candidate = (project_dir / relative_path).resolve()
    try:
        candidate.relative_to(art_root)
    except ValueError:
        print_text("Ilustrasi dilewati: path harus berada di folder art/.", "warning")
        return False
    if not candidate.is_file():
        print_text(f"Ilustrasi tidak ditemukan: {relative_path}", "warning")
        return False
    try:
        art = candidate.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print_text(f"Gagal membaca ilustrasi: {exc}", "warning")
        return False
    print_text(art.rstrip("\n"), "muted")
    return True
