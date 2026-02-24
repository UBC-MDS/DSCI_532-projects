import pandas as pd
import requests
from pathlib import Path
from typing import Optional
from tqdm import tqdm


def get_output_path() -> Path:
    """
    Get the path to the data directory.

    Works in both script and interactive modes by checking if __file__ is defined.
    If running interactively, defaults to current working directory.

    Returns:
        Path to the data directory
    """
    try:
        # Running as a script
        script_dir = Path(__file__).parent
        return script_dir.parent / "data"
    except NameError:
        # Running interactively (e.g., Jupyter, REPL)
        return Path.cwd() / "data"


def get_group_data_path() -> Path:
    """
    Get the path to the group_data directory.

    Returns:
        Path to the group_data directory
    """
    try:
        # Running as a script
        script_dir = Path(__file__).parent
        return script_dir.parent / "group_data"
    except NameError:
        # Running interactively (e.g., Jupyter, REPL)
        return Path.cwd() / "group_data"


def download_sketch(
    repo_full_name: str, group_number: str, group_data_dir: Path
) -> Optional[str]:
    """
    Download sketch.png from a repository's img/ folder.

    Args:
        repo_full_name: Full repository name (e.g., "UBC-MDS/DSCI-532_2026_12_my-project")
        group_number: Group number for directory structure
        group_data_dir: Base directory for group data

    Returns:
        Path to downloaded file if successful, None otherwise
    """
    # Create group directory
    group_dir = group_data_dir / group_number
    group_dir.mkdir(parents=True, exist_ok=True)

    # Construct raw GitHub URL (try main branch first)
    branches = ["main", "master"]
    file_path = "img/sketch.png"

    for branch in branches:
        raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/{branch}/{file_path}"

        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code == 200:
                # Save as sketch.png (each group has its own directory)
                output_filename = "sketch.png"
                output_path = group_dir / output_filename

                with open(output_path, "wb") as f:
                    f.write(response.content)

                # Return relative path from project root
                return str(output_path.relative_to(group_data_dir.parent))

        except requests.exceptions.RequestException as e:
            # Try next branch
            continue

    return None


def download_all_sketches(csv_path: str, output_csv: str = None):
    """
    Download sketch files for all repositories and update CSV with paths.

    Args:
        csv_path: Path to input CSV file
        output_csv: Path to output CSV file (if None, overwrites input_csv)
    """
    # Read the CSV
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} repositories from {csv_path}")

    # Get group data directory
    group_data_dir = get_group_data_path()
    group_data_dir.mkdir(parents=True, exist_ok=True)

    # Download sketches for each repository
    sketch_paths = []

    print("\nDownloading sketch files...")
    for idx, row in tqdm(
        df.iterrows(), total=len(df), desc="Processing repos"
    ):
        repo_full_name = row["full_name"]
        group_number = row["group_number"]

        if not group_number:
            # Skip repos without group number
            sketch_paths.append("")
            continue

        sketch_path = download_sketch(
            repo_full_name, group_number, group_data_dir
        )

        sketch_paths.append(sketch_path if sketch_path else "")

    # Add sketch_path column to dataframe
    df["sketch_path"] = sketch_paths

    # Save updated CSV
    output_path = output_csv if output_csv else csv_path
    df.to_csv(output_path, index=False)

    # Print summary
    successful_downloads = sum(1 for path in sketch_paths if path)
    print(
        f"\nSuccessfully downloaded {successful_downloads}/{len(df)} sketch files"
    )
    print(f"Updated CSV saved to {output_path}")

    # Show sample of downloaded files
    print("\nSample of downloaded files:")
    print(df[["name", "group_number", "sketch_path"]].head(10))

    return df


def main():
    """Main function to download sketch files."""
    data_dir = get_output_path()
    input_file = data_dir / "dsci_532_repos.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}\n"
            "Please run 01-fetch_repos.py and 02-parse_repos.py first."
        )

    print("Downloading sketch files from repositories...")
    df = download_all_sketches(str(input_file))

    return df


if __name__ == "__main__":
    main()
