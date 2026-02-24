# DSCI_532-projects

Scripts for managing DSCI 532 project repositories from the UBC-MDS GitHub organization.

## Setup

Create a virtual environment and install dependencies:

```bash
make setup
```

Or manually:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

### GitHub Authentication

The script requires a GitHub Personal Access Token (PAT). You can provide it in three ways (in order of precedence):

1. Enter it when prompted (press Enter to skip to next option)
2. Store in a `.env` file (copy `.env.example` to `.env` and add your token):
   ```bash
   cp .env.example .env
   # Then edit .env and add your token
   ```
3. Set as an environment variable:
   ```bash
   export GITHUB_TOKEN=your_token_here
   # or
   export GITHUB_PAT=your_token_here
   ```

To create a token, visit: https://github.com/settings/tokens

### Running the Scripts

The project includes several scripts that should be run in sequence:

```bash
# 1. Fetch repository data from GitHub
python scripts/01-fetch_repos.py

# 2. Parse repository information
python scripts/02-parse_repos.py

# 3. Download project sketches
python scripts/03-download_sketches.py

# 4. Generate Quarto pages
python scripts/04-generate_quarto_pages.py
```

Or run all scripts in sequence using the Makefile:

```bash
make all
```

## Quarto Document

### Preview Locally

To render and preview the Quarto website locally:

```bash
quarto preview
```

This will start a local web server and automatically open the site in your browser. The preview will auto-refresh when you make changes to any `.qmd` files.

### Render Only

To build the site without previewing:

```bash
quarto render
```

The rendered site will be in the `_site/` directory.
