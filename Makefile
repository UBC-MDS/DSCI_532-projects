.PHONY: setup all publish

setup:
	uv venv
	source .venv/bin/activate && uv pip install -e .

all:
	python scripts/01-fetch_repos.py
	python scripts/02-parse_repos.py
	python scripts/03-download_sketches.py
	python scripts/04-download_demos.py
	python scripts/05-normalize_demos.py
	python scripts/06-fetch_website_urls.py
	python scripts/07-generate_quarto_pages.py

publish:
	quarto publish gh-pages
