from __future__ import annotations

from pathlib import Path
from player import Player
from engine import StoryEngine
from systems.story_loader import StoryLoader
from systems.terminal_ui import print_text, rule, loading

BASE_DIR = Path(__file__).resolve().parent
STORIES_DIR = BASE_DIR / "stories"
ART_DIR = BASE_DIR / "art"


def print_help() -> None:
    print_text("\nPerintah:", "title")
    print_text("  Ready  - memilih dan memainkan cerita acak", "choice")
    print_text("  Debug  - memilih cerita atau melihat art berdasarkan nama file", "choice")
    print_text("  Status - melihat status karakter", "choice")
    print_text("  Help   - menampilkan bantuan", "choice")
    print_text("  Quit   - keluar dari game", "choice")
    print_text("\nTip: set TEXTRPG_NO_ANIMATION=1 untuk mematikan animasi.", "muted")


def debug_select_story(loader: StoryLoader, engine: StoryEngine) -> None:
    """Menjalankan cerita tertentu berdasarkan nama file JSON."""
    print_text("\n=== DEBUG: PILIH CERITA ===", "title")
    print_text("Masukkan nama file cerita, misalnya pengemis.json.", "story")
    print_text("Ketik Back untuk kembali ke menu Debug.", "muted")

    filename = input("Nama file cerita: ").strip()

    if filename.lower() == "back":
        return

    if not filename:
        print_text("Nama file tidak boleh kosong.", "warning")
        return

    # Hanya gunakan nama file, bukan path yang diketik pengguna.
    requested_name = Path(filename).name
    if requested_name.lower().endswith(".json"):
        requested_name = requested_name[:-5]
    requested_name = requested_name.casefold()

    matches = []
    for story in loader.stories:
        source_file = story.get("_source_file")
        if not source_file:
            continue

        if Path(source_file).stem.casefold() == requested_name:
            matches.append(story)

    if not matches:
        print_text(
            f"File cerita '{filename}' tidak ditemukan di folder stories.",
            "failure",
        )
        return

    if len(matches) > 1:
        print_text("Ada beberapa file dengan nama yang sama:", "warning")
        for index, story in enumerate(matches, start=1):
            print_text(
                f"  {index}. {story.get('title', '(tanpa judul)')} "
                f"— {story.get('_source_file', '')}",
                "choice",
            )

        try:
            selected = int(input("Pilih nomor file (0 untuk batal): ").strip())
        except ValueError:
            print_text("Input harus berupa angka.", "warning")
            return

        if selected == 0:
            return
        if not 1 <= selected <= len(matches):
            print_text("Nomor pilihan tidak valid.", "warning")
            return

        story = matches[selected - 1]
    else:
        story = matches[0]

    print_text(
        f"Debug: menjalankan '{story.get('title', '(tanpa judul)')}' "
        f"dari {story.get('_source_file', '')}",
        "success",
    )
    engine.play(story)


def debug_select_art() -> None:
    """Mencari dan menampilkan file ASCII art dari folder art/."""
    print_text("\n=== DEBUG: PILIH ART ===", "title")
    print_text("Masukkan nama file art, misalnya demo_ruins.txt (ekstensi boleh dihilangkan).", "story")
    print_text("Ketik Back untuk kembali ke menu Debug.", "muted")

    filename = input("Nama file art: ").strip()
    if filename.casefold() == "back":
        return
    if not filename:
        print_text("Nama file tidak boleh kosong.", "warning")
        return

    if not ART_DIR.is_dir():
        print_text("Folder 'art' tidak ditemukan.", "failure")
        return

    # Art game disimpan sebagai file teks UTF-8 (biasanya .txt).
    art_files = sorted(
        (path for path in ART_DIR.rglob("*") if path.is_file() and path.suffix.casefold() == ".txt"),
        key=lambda path: str(path).casefold(),
    )
    if not art_files:
        print_text("Belum ada file art .txt di folder 'art'.", "warning")
        return

    requested = Path(filename.replace("\\", "/"))
    requested_text = requested.as_posix().casefold().strip("/")
    if requested_text.endswith(".txt"):
        requested_stem = requested_text[:-4]
    else:
        requested_stem = requested_text

    matches = []
    for path in art_files:
        relative = path.relative_to(ART_DIR).as_posix().casefold()
        relative_stem = relative[:-4] if relative.endswith(".txt") else relative
        if relative == requested_text or relative_stem == requested_stem:
            matches.append(path)
        elif path.name.casefold() == requested_text or path.stem.casefold() == requested_stem:
            matches.append(path)

    # Hindari duplikat apabila satu file cocok dengan lebih dari satu aturan.
    matches = list(dict.fromkeys(matches))
    if not matches:
        print_text(f"File art '{filename}' tidak ditemukan di folder art.", "failure")
        return

    if len(matches) > 1:
        print_text("Ada beberapa file art dengan nama yang sama:", "warning")
        for index, path in enumerate(matches, start=1):
            print_text(f"  {index}. {path.relative_to(ART_DIR).as_posix()}", "choice")
        try:
            selected = int(input("Pilih nomor file (0 untuk batal): ").strip())
        except ValueError:
            print_text("Input harus berupa angka.", "warning")
            return
        if selected == 0:
            return
        if not 1 <= selected <= len(matches):
            print_text("Nomor pilihan tidak valid.", "warning")
            return
        art_path = matches[selected - 1]
    else:
        art_path = matches[0]

    try:
        art_content = art_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print_text(f"Gagal membaca file art: {exc}", "failure")
        return

    print_text(f"\nPreview art: {art_path.relative_to(BASE_DIR).as_posix()}", "success")
    print_text(art_content.rstrip("\n"), "muted")


def debug_menu(loader: StoryLoader, engine: StoryEngine) -> None:
    """Menu debug untuk memilih cerita tertentu atau melihat art."""
    while True:
        print_text("\n=== DEBUG MODE ===", "title")
        print_text("  1. Pilih cerita dari folder stories/", "choice")
        print_text("  2. Lihat art dari folder art/", "choice")
        print_text("  0. Kembali ke menu utama", "muted")
        selection = input("Debug > ").strip().lower()

        if selection in {"1", "story", "cerita"}:
            debug_select_story(loader, engine)
        elif selection in {"2", "art"}:
            debug_select_art()
        elif selection in {"0", "back", "b", "keluar"}:
            return
        else:
            print_text("Pilihan tidak dikenal. Pilih 1, 2, atau 0.", "warning")



def handle_game_over(player: Player, engine: StoryEngine) -> None:
    """Membuat karakter baru jika HP habis setelah cerita dimainkan."""
    if player.hp <= 0:
        rule("GAME OVER")
        print_text("HP karakter habis.", "failure")
        print_text(
            "Karakter baru dibuat; progres karakter sebelumnya berakhir.",
            "warning",
        )
        player.reset()
        engine.player = player
        engine.battle.player = player
        input("Tekan Enter untuk kembali ke menu...")


def main() -> None:
    rule("TEXT RPG")
    print_text("TEXT RPG - QOL UPDATE", "title")
    print_text("Cerita acak • Dice check • Battle", "muted")
    print_text("Ketik Ready untuk cerita acak atau Debug untuk memilih cerita / melihat art.\n", "story")

    player = Player()
    loader = StoryLoader(STORIES_DIR)
    engine = StoryEngine(player, loader, project_dir=BASE_DIR)

    if not loader.stories:
        print_text("Belum ada cerita yang berhasil dimuat dari folder 'stories'.", "failure")
        print_text("Periksa file JSON dan README.txt. Debug art tetap bisa digunakan.", "warning")
    else:
        print_text(f"Berhasil memuat {len(loader.stories)} cerita.", "success")

    if loader.errors:
        print_text(f"Peringatan: {len(loader.errors)} file cerita tidak berhasil dimuat.", "warning")
        for error in loader.errors:
            print_text(f"  - {error}", "muted")
    print_help()

    while True:
        try:
            command = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print_text("\nGame ditutup. Sampai jumpa!", "system")
            break

        if command == "ready":
            loading("Memilih petualangan...")
            story = loader.pick_random(previous_id=engine.last_story_id)
            if story is None:
                print_text("Tidak ada cerita yang tersedia.", "failure")
                continue
            engine.play(story)
            handle_game_over(player, engine)
        elif command == "debug":
            debug_menu(loader, engine)
            handle_game_over(player, engine)
        elif command == "status":
            player.show_status()
        elif command == "help":
            print_help()
        elif command in {"quit", "exit", "keluar"}:
            print_text("Game ditutup. Sampai jumpa!", "system")
            break
        elif command == "":
            continue
        else:
            print_text("Perintah tidak dikenal. Ketik Help untuk melihat perintah.", "warning")


if __name__ == "__main__":
    main()
