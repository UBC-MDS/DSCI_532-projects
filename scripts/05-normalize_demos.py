from pathlib import Path
from PIL import Image


def get_group_data_path() -> Path:
    try:
        script_dir = Path(__file__).parent
        return script_dir.parent / "group_data"
    except NameError:
        return Path.cwd() / "group_data"


def process_gif(
    gif_path: Path,
    max_duration_ms: int = 1000,
    max_width: int = 800,
    max_colors: int = 128,
) -> tuple[int, int]:
    """
    Process a GIF in a single pass:
      - Resize frames to max_width (preserving aspect ratio)
      - Reduce color palette to max_colors
      - Scale frame durations so total playback <= max_duration_ms

    Returns (original_bytes, new_bytes).
    """
    original_size = gif_path.stat().st_size

    img = Image.open(gif_path)
    frames = []
    durations = []

    try:
        while True:
            durations.append(img.info.get("duration", 100))
            frame = img.copy().convert("RGBA")

            # Resize if wider than max_width
            if frame.width > max_width:
                ratio = max_width / frame.width
                frame = frame.resize(
                    (max_width, int(frame.height * ratio)), Image.LANCZOS
                )

            frames.append(frame)
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    # Scale durations to fit within max_duration_ms
    total = sum(durations)
    if total > max_duration_ms:
        scale = max_duration_ms / total
        durations = [max(10, int(d * scale)) for d in durations]

    # Quantize each frame to reduce palette size
    palette_frames = [
        f.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
        for f in frames
    ]

    palette_frames[0].save(
        gif_path,
        save_all=True,
        append_images=palette_frames[1:],
        loop=0,
        duration=durations,
        optimize=True,
    )

    new_size = gif_path.stat().st_size
    return original_size, new_size


def process_all_demos(
    group_data_dir: Path,
    max_duration_ms: int = 1000,
    max_width: int = 800,
    max_colors: int = 128,
):
    """Process every demo.gif in group_data_dir."""
    gifs = list(group_data_dir.glob("*/demo.gif"))

    if not gifs:
        print("No demo.gif files found.")
        return

    print(f"Found {len(gifs)} demo.gif files. Processing...")

    total_before = total_after = 0

    for gif_path in sorted(gifs):
        try:
            before, after = process_gif(gif_path, max_duration_ms, max_width, max_colors)
            total_before += before
            total_after += after
            saved_pct = (1 - after / before) * 100 if before else 0
            print(
                f"  {gif_path.parent.name}/demo.gif — "
                f"{before / 1_000_000:.1f}MB → {after / 1_000_000:.1f}MB "
                f"({saved_pct:.0f}% reduction)"
            )
        except Exception as e:
            print(f"  {gif_path.parent.name}/demo.gif — ERROR: {e}")

    overall_pct = (1 - total_after / total_before) * 100 if total_before else 0
    print(
        f"\nDone. {total_before / 1_000_000:.1f}MB → {total_after / 1_000_000:.1f}MB "
        f"({overall_pct:.0f}% total reduction)"
    )


def main():
    group_data_dir = get_group_data_path()

    if not group_data_dir.exists():
        raise FileNotFoundError(
            f"group_data directory not found: {group_data_dir}\n"
            "Please run 04-download_demos.py first."
        )

    process_all_demos(group_data_dir)


if __name__ == "__main__":
    main()
