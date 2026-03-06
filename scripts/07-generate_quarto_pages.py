import pandas as pd
from pathlib import Path


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


def get_projects_path() -> Path:
    """
    Get the path to the projects directory for Quarto listing.

    Returns:
        Path to the projects directory
    """
    try:
        # Running as a script
        script_dir = Path(__file__).parent
        return script_dir.parent / "projects"
    except NameError:
        # Running interactively (e.g., Jupyter, REPL)
        return Path.cwd() / "projects"


def create_project_page(
    group_number: str,
    project_name: str,
    html_url: str,
    website_url: str,
    description: str,
    sketch_path: str,
    demo_path: str,
    projects_dir: Path,
    sort_order: int,
) -> None:
    """
    Create a Quarto markdown file for a project.

    Args:
        group_number: Group number
        project_name: Project name
        html_url: GitHub repository URL
        website_url: Deployed app URL
        description: Project description
        sketch_path: Path to sketch image
        demo_path: Path to demo gif
        projects_dir: Directory to save project pages
        sort_order: Numeric order for sorting (group number or high value for non-numeric)
    """
    # Create filename from group number
    filename = f"group-{group_number}.qmd"
    filepath = projects_dir / filename

    # Use demo path if available, fall back to sketch, then placeholder
    if demo_path and pd.notna(demo_path):
        image_path = f"../{demo_path}"
    elif sketch_path and pd.notna(sketch_path):
        image_path = f"../{sketch_path}"
    else:
        image_path = "https://via.placeholder.com/400x300?text=No+Image"

    # Clean description
    clean_description = (
        description if description and pd.notna(description) else ""
    )

    # dashboard and repo as separate fields
    dashboard_field = (
        f'"{website_url}"' if website_url and pd.notna(website_url) else '""'
    )

    # Build image sections for page body
    body_lines = []
    if demo_path and pd.notna(demo_path):
        body_lines.append("## Demo\n")
        body_lines.append(f"![Demo](../{demo_path})\n")
    if sketch_path and pd.notna(sketch_path):
        body_lines.append("## Sketch\n")
        body_lines.append(f"![Sketch](../{sketch_path})\n")
    body = "\n".join(body_lines) if body_lines else ""

    # Create YAML frontmatter and minimal content
    content = f"""---
title: "Group {group_number}"
subtitle: "{project_name}"
description: "{clean_description}"
repo: "{html_url}"
dashboard: {dashboard_field}
image: {image_path}
order: {sort_order}
---

{body}"""

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def generate_all_pages(csv_path: str) -> None:
    """
    Generate Quarto pages for all projects in the CSV.

    Args:
        csv_path: Path to input CSV file
    """
    # Read the CSV
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} repositories from {csv_path}")

    # Get projects directory
    projects_dir = get_projects_path()
    projects_dir.mkdir(parents=True, exist_ok=True)

    # Generate page for each project
    pages_created = 0
    non_numeric_groups = []

    # First pass: process numeric groups
    for idx, row in df.iterrows():
        group_number = row["group_number"]

        # Skip if no group number
        if not group_number or pd.isna(group_number):
            continue

        # Check if group_number is numeric
        try:
            group_num_int = int(float(group_number))
            group_num_str = str(group_num_int)
            sort_order = group_num_int
        except (ValueError, TypeError):
            # Save non-numeric groups for later
            non_numeric_groups.append((group_number, row))
            continue

        project_name = (
            row["project_name"] if pd.notna(row["project_name"]) else ""
        )
        html_url = row["html_url"]
        website_url = (
            row["website_url"]
            if "website_url" in row and pd.notna(row["website_url"])
            else ""
        )
        description = (
            row["description"] if pd.notna(row["description"]) else ""
        )
        sketch_path = (
            row["sketch_path"]
            if "sketch_path" in row and pd.notna(row["sketch_path"])
            else ""
        )
        demo_path = (
            row["demo_path"]
            if "demo_path" in row and pd.notna(row["demo_path"])
            else ""
        )

        create_project_page(
            group_num_str,
            project_name,
            html_url,
            website_url,
            description,
            sketch_path,
            demo_path,
            projects_dir,
            sort_order,
        )

        pages_created += 1

    # Second pass: process non-numeric groups (alphabetically at the end)
    # Sort non-numeric groups alphabetically
    non_numeric_groups.sort(key=lambda x: x[0])

    for idx, (group_number, row) in enumerate(non_numeric_groups):
        # Assign high sort order (9000+) to put at end, with alphabetical ordering
        sort_order = 9000 + idx

        project_name = (
            row["project_name"] if pd.notna(row["project_name"]) else ""
        )
        html_url = row["html_url"]
        website_url = (
            row["website_url"]
            if "website_url" in row and pd.notna(row["website_url"])
            else ""
        )
        description = (
            row["description"] if pd.notna(row["description"]) else ""
        )
        sketch_path = (
            row["sketch_path"]
            if "sketch_path" in row and pd.notna(row["sketch_path"])
            else ""
        )
        demo_path = (
            row["demo_path"]
            if "demo_path" in row and pd.notna(row["demo_path"])
            else ""
        )

        create_project_page(
            str(group_number),
            project_name,
            html_url,
            website_url,
            description,
            sketch_path,
            demo_path,
            projects_dir,
            sort_order,
        )

        pages_created += 1
        print(
            f"Created page for non-numeric group '{group_number}' with sort order {sort_order}"
        )

    print(
        f"\nSuccessfully created {pages_created} project pages in {projects_dir}"
    )
    print("\nTo build the website, run:")
    print("  quarto render")


def main():
    """Main function to generate Quarto project pages."""
    data_dir = get_output_path()
    input_file = data_dir / "dsci_532_repos.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}\n"
            "Please run 01- through 05- scripts first."
        )

    print("Generating Quarto project pages...")
    generate_all_pages(str(input_file))


if __name__ == "__main__":
    main()
