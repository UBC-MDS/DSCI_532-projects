import github3
import csv
import os
from getpass import getpass
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm


def get_github_token() -> str:
    """
    Get GitHub Personal Access Token.

    Checks in order:
    1. Environment variables (GITHUB_TOKEN or GITHUB_PAT)
    2. .env file (GITHUB_TOKEN or GITHUB_PAT)
    3. Prompts user for input

    Returns:
        GitHub Personal Access Token
    """
    # Check environment variables first (for CI/CD)
    token = os.getenv("GITHUB_TOKEN", "").strip()

    # If not found, check GITHUB_PAT
    if not token:
        token = os.getenv("GITHUB_PAT", "").strip()

    # If still not found, load from .env file
    if not token:
        load_dotenv()
        token = os.getenv("GITHUB_TOKEN", "").strip()

    # If still not found, check GITHUB_PAT from .env
    if not token:
        token = os.getenv("GITHUB_PAT", "").strip()

    # Finally, prompt user if still empty
    if not token:
        token = getpass(
            "Enter your GitHub Personal Access Token (press Enter to skip): "
        ).strip()

    if not token:
        raise ValueError(
            "No GitHub token provided. Please provide a token via environment variable, .env file, or prompt."
        )

    return token


def fetch_ubc_mds_repos(
    pattern: str = "DSCI-532_2026_", token: str = None
) -> List[Dict]:
    """
    Fetch all repositories from UBC-MDS organization that match the given pattern.

    Args:
        pattern: The prefix pattern to match repository names against
        token: GitHub Personal Access Token

    Returns:
        List of repository dictionaries containing name and other metadata
    """
    org_name = "UBC-MDS"

    # Create GitHub client with token
    gh = github3.login(token=token)
    org = gh.organization(org_name)

    matching_repos = []

    # Iterate through all repos (github3 handles pagination automatically)
    with tqdm(desc="Scanning repos (0 matches)", unit=" repos") as pbar:
        for repo in org.repositories():
            pbar.update(1)
            if repo.name.startswith(pattern):
                matching_repos.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "html_url": repo.html_url,
                    "description": repo.description or "",
                    "created_at": repo.created_at if repo.created_at else "",
                    "updated_at": repo.updated_at if repo.updated_at else "",
                    "private": repo.private,
                })
                # Update progress bar description with match count
                pbar.set_description(f"Scanning repos ({len(matching_repos)} matches)")

    return matching_repos


def get_output_path() -> Path:
    """
    Get the output path for the CSV file.

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


def save_to_csv(repos: List[Dict], filename: str = "dsci_532_repos.csv"):
    """
    Save the list of repositories to a CSV file.

    Args:
        repos: List of repository dictionaries
        filename: Output CSV filename (can be relative or absolute path)
    """
    if not repos:
        print("No repositories found matching the pattern.")
        return

    fieldnames = [
        "name",
        "full_name",
        "html_url",
        "description",
        "created_at",
        "updated_at",
        "private",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repos)

    print(f"Successfully saved {len(repos)} repositories to {filename}")


def main():
    """Main function to fetch and save repositories."""
    # Get GitHub token
    token = get_github_token()

    print("Fetching repositories from UBC-MDS organization...")
    repos = fetch_ubc_mds_repos("DSCI-532_2026_", token=token)

    print(f"Found {len(repos)} repositories matching pattern 'DSCI-532_2026_'")

    if repos:
        # Save to data directory
        data_dir = get_output_path()
        data_dir.mkdir(parents=True, exist_ok=True)
        output_path = data_dir / "dsci_532_repos.csv"
        save_to_csv(repos, str(output_path))
        print("\nRepository names:")
        for repo in repos:
            print(f"  - {repo['name']}")

    return repos


if __name__ == "__main__":
    main()
