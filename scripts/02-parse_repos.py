import pandas as pd
from pathlib import Path
from typing import Tuple


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


def parse_repo_name(repo_name: str, pattern: str = "DSCI-532_2026_") -> Tuple[str, str]:
    """
    Parse repository name to extract group number and project name.

    Args:
        repo_name: Full repository name (e.g., "DSCI-532_2026_12_my-project")
        pattern: The prefix pattern to remove

    Returns:
        Tuple of (group_number, project_name)
    """
    # Remove the prefix pattern
    if not repo_name.startswith(pattern):
        return "", ""

    remainder = repo_name[len(pattern):]

    # Split by underscore
    parts = remainder.split("_", 1)

    if len(parts) < 2:
        # Only group number, no project name
        return parts[0], ""

    group_number = parts[0]
    project_name = parts[1]

    return group_number, project_name


def parse_repos_csv(input_file: str, output_file: str = None):
    """
    Parse repository names and add group_number and project_name columns.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file (if None, overwrites input_file)
    """
    # Read the CSV
    df = pd.read_csv(input_file)

    print(f"Loaded {len(df)} repositories from {input_file}")

    # Parse each repository name
    parsed_data = df["name"].apply(lambda x: pd.Series(parse_repo_name(x)))
    parsed_data.columns = ["group_number", "project_name"]

    # Add new columns to dataframe
    df["group_number"] = parsed_data["group_number"]
    df["project_name"] = parsed_data["project_name"]

    # Save to CSV
    output_path = output_file if output_file else input_file
    df.to_csv(output_path, index=False)

    print(f"Successfully parsed and saved to {output_path}")
    print("\nSample of parsed data:")
    print(df[["name", "group_number", "project_name"]].head(10))

    return df


def main():
    """Main function to parse repository CSV."""
    data_dir = get_output_path()
    input_file = data_dir / "dsci_532_repos.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}\n"
            "Please run 01-fetch_repos.py first to generate the CSV file."
        )

    print("Parsing repository names...")
    df = parse_repos_csv(str(input_file))

    return df


if __name__ == "__main__":
    main()
