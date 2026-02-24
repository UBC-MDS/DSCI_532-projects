.PHONY: setup all publish

setup:
	uv venv
	uv pip install -e .

all:
	python scripts/01-fetch_repos.py
	python scripts/02-parse_repos.py
	python scripts/03-download_sketches.py
	python scripts/04-generate_quarto_pages.py

publish:
	quarto publish gh-pages
