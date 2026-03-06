import os
import pandas as pd
import github3
from getpass import getpass
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm


def get_github_token() -> str:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        token = os.getenv("GITHUB_PAT", "").strip()
    if not token:
        load_dotenv()
        token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        token = os.getenv("GITHUB_PAT", "").strip()
    if not token:
        token = getpass(
            "Enter your GitHub Personal Access Token (press Enter to skip): "
        ).strip()
    if not token:
        raise ValueError(
            "No GitHub token provided. Please provide a token via environment variable, .env file, or prompt."
        )
    return token


def get_output_path() -> Path:
    try:
        script_dir = Path(__file__).parent
        return script_dir.parent / "data"
    except NameError:
        return Path.cwd() / "data"


def fetch_website_urls(csv_path: str, output_csv: str = None):
    """
    Fetch the website/homepage URL for each repo and add it to the CSV.

    Args:
        csv_path: Path to input CSV file
        output_csv: Path to output CSV file (if None, overwrites input_csv)
    """
    token = get_github_token()

    try:
        gh = github3.login(token=token)
    except github3.exceptions.AuthenticationFailed:
        print("\nAuthentication failed with provided token.")
        token = getpass(
            "Please manually paste your GitHub Personal Access Token: "
        ).strip()
        if not token:
            raise ValueError("No token provided. Cannot authenticate with GitHub.")
        gh = github3.login(token=token)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} repositories from {csv_path}")

    website_urls = []

    print("\nFetching website URLs...")
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing repos"):
        full_name = row["full_name"]
        owner, repo_name = full_name.split("/", 1)

        try:
            repo = gh.repository(owner, repo_name)
            website_urls.append(repo.homepage or "")
        except Exception:
            website_urls.append("")

    df["website_url"] = website_urls

    output_path = output_csv if output_csv else csv_path
    df.to_csv(output_path, index=False)

    found = sum(1 for url in website_urls if url)
    print(f"\nFound website URLs for {found}/{len(df)} repositories")
    print(f"Updated CSV saved to {output_path}")

    print("\nSample of website URLs:")
    print(df[["name", "group_number", "website_url"]].head(10))

    return df


def main():
    """Main function to fetch website URLs."""
    data_dir = get_output_path()
    input_file = data_dir / "dsci_532_repos.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}\n"
            "Please run 01-fetch_repos.py and 02-parse_repos.py first."
        )

    print("Fetching website URLs from GitHub repositories...")
    fetch_website_urls(str(input_file))


if __name__ == "__main__":
    main()
