import subprocess
import tempfile
import pandas as pd
import requests
from pathlib import Path
from typing import Optional
from tqdm import tqdm


def mp4_to_gif(mp4_path: Path, gif_path: Path) -> bool:
    """
    Convert an MP4 file to GIF using ffmpeg with palette optimisation.

    Returns True on success, False if ffmpeg is unavailable or fails.
    """
    try:
        # Two-pass palettegen for best colour quality
        filter_graph = (
            "fps=10,scale=800:-1:flags=lanczos,"
            "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
        )
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(mp4_path),
                "-vf", filter_graph,
                "-loop", "0",
                str(gif_path),
            ],
            capture_output=True,
            timeout=120,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_output_path() -> Path:
    try:
        script_dir = Path(__file__).parent
        return script_dir.parent / "data"
    except NameError:
        return Path.cwd() / "data"


def get_group_data_path() -> Path:
    try:
        script_dir = Path(__file__).parent
        return script_dir.parent / "group_data"
    except NameError:
        return Path.cwd() / "group_data"


def download_demo(
    repo_full_name: str, group_number: str, group_data_dir: Path
) -> Optional[str]:
    """
    Download demo.gif from a repository's img/ folder.

    Args:
        repo_full_name: Full repository name (e.g., "UBC-MDS/DSCI-532_2026_12_my-project")
        group_number: Group number for directory structure
        group_data_dir: Base directory for group data

    Returns:
        Path to downloaded file if successful, None otherwise
    """
    group_dir = group_data_dir / str(group_number)
    group_dir.mkdir(parents=True, exist_ok=True)

    output_path = group_dir / "demo.gif"

    # If already downloaded, return the existing path
    if output_path.exists():
        return str(output_path.relative_to(group_data_dir.parent))

    branches = ["main", "master"]

    # Try GIF first, then MP4
    for file_path in ["img/demo.gif", "img/demo.mp4"]:
        for branch in branches:
            raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/{branch}/{file_path}"

            try:
                response = requests.get(raw_url, timeout=30)
                if response.status_code != 200:
                    continue

                if file_path.endswith(".gif"):
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    return str(output_path.relative_to(group_data_dir.parent))

                else:
                    # Write MP4 to a temp file and convert to GIF
                    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                        tmp.write(response.content)
                        tmp_path = Path(tmp.name)
                    try:
                        if mp4_to_gif(tmp_path, output_path):
                            return str(output_path.relative_to(group_data_dir.parent))
                    finally:
                        tmp_path.unlink(missing_ok=True)

            except requests.exceptions.RequestException:
                continue

    return None


def download_all_demos(csv_path: str, output_csv: str = None):
    """
    Download demo.gif files for all repositories and update CSV with paths.

    Args:
        csv_path: Path to input CSV file
        output_csv: Path to output CSV file (if None, overwrites input_csv)
    """
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} repositories from {csv_path}")

    group_data_dir = get_group_data_path()
    group_data_dir.mkdir(parents=True, exist_ok=True)

    demo_paths = []

    print("\nDownloading demo files...")
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing repos"):
        repo_full_name = row["full_name"]
        group_number = row["group_number"]

        if not group_number:
            demo_paths.append("")
            continue

        demo_path = download_demo(repo_full_name, group_number, group_data_dir)
        demo_paths.append(demo_path if demo_path else "")

    df["demo_path"] = demo_paths

    output_path = output_csv if output_csv else csv_path
    df.to_csv(output_path, index=False)

    successful_downloads = sum(1 for path in demo_paths if path)
    print(f"\nSuccessfully downloaded {successful_downloads}/{len(df)} demo files")
    print(f"Updated CSV saved to {output_path}")

    print("\nSample of downloaded files:")
    print(df[["name", "group_number", "demo_path"]].head(10))

    return df


def main():
    """Main function to download demo files."""
    data_dir = get_output_path()
    input_file = data_dir / "dsci_532_repos.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}\n"
            "Please run 01-fetch_repos.py and 02-parse_repos.py first."
        )

    print("Downloading demo files from repositories...")
    df = download_all_demos(str(input_file))

    return df


if __name__ == "__main__":
    main()
