from pathlib import Path
from PIL import Image


def get_group_data_path() -> Path:
    try:
        script_dir = Path(__file__).parent
        return script_dir.parent / "group_data"
    except NameError:
        return Path.cwd() / "group_data"


def normalize_gif(gif_path: Path, max_duration_ms: int = 2000) -> bool:
    """
    Rewrite a GIF so its total playback duration does not exceed max_duration_ms.
    Frame durations are scaled proportionally. No-ops if already within limit.

    Returns True if the file was rewritten, False otherwise.
    """
    img = Image.open(gif_path)

    frames = []
    durations = []
    try:
        while True:
            durations.append(img.info.get("duration", 100))
            frames.append(img.copy().convert("RGBA"))
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    total = sum(durations)
    if total <= max_duration_ms:
        return False

    scale = max_duration_ms / total
    new_durations = [max(10, int(d * scale)) for d in durations]

    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=new_durations,
        optimize=False,
    )
    return True


def normalize_all_demos(group_data_dir: Path, max_duration_ms: int = 2000):
    """
    Walk group_data_dir and normalize every demo.gif found.
    """
    gifs = list(group_data_dir.glob("*/demo.gif"))

    if not gifs:
        print("No demo.gif files found.")
        return

    print(f"Found {len(gifs)} demo.gif files. Normalizing to {max_duration_ms}ms max...")

    rewritten = 0
    for gif_path in sorted(gifs):
        try:
            changed = normalize_gif(gif_path, max_duration_ms)
            status = "normalized" if changed else "ok"
            print(f"  {gif_path.parent.name}/demo.gif — {status}")
            if changed:
                rewritten += 1
        except Exception as e:
            print(f"  {gif_path.parent.name}/demo.gif — ERROR: {e}")

    print(f"\nDone. {rewritten}/{len(gifs)} files rewritten.")


def main():
    group_data_dir = get_group_data_path()

    if not group_data_dir.exists():
        raise FileNotFoundError(
            f"group_data directory not found: {group_data_dir}\n"
            "Please run 04-download_demos.py first."
        )

    normalize_all_demos(group_data_dir, max_duration_ms=1000)


if __name__ == "__main__":
    main()
