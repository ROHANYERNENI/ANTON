
import os
import subprocess
from pathlib import Path
from collections import Counter

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".next",
    "coverage"
}

LANGUAGES = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".html": "HTML",
    ".css": "CSS",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".swift": "Swift",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".sql": "SQL"
}


def get_git_information(project_path):
    result = subprocess.run(
        ["git", "-C", str(project_path), "status", "--short", "--branch"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return "Git information unavailable."

    return result.stdout.strip() or "Working tree clean."


def scan_project(project_path):
    language_counts = Counter()
    total_files = 0
    total_lines = 0
    top_level_items = []

    for item in project_path.iterdir():
        top_level_items.append(item.name)

    for root, directories, files in os.walk(project_path):
        directories[:] = [
            directory for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in files:
            file_path = Path(root) / filename

            if file_path.is_symlink():
                continue

            extension = file_path.suffix.lower()

            if extension not in LANGUAGES:
                continue

            try:
                if file_path.stat().st_size > 1_000_000:
                    continue

                with file_path.open(
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:
                    lines = sum(1 for _ in file)

                language_counts[LANGUAGES[extension]] += 1
                total_files += 1
                total_lines += lines

            except OSError:
                continue

    return {
        "languages": language_counts,
        "total_files": total_files,
        "total_lines": total_lines,
        "top_level_items": top_level_items
    }


def analyze_project(config):
    console.print("\n[bold]ANTON PROJECT ANALYSIS[/bold]\n")

    repository_path = config.get("git_local_path")

    if not repository_path:
        console.print(
            "[yellow]No project is connected. "
            "Connect a Git repository first.[/yellow]"
        )
        return

    project_path = Path(repository_path).expanduser()

    if not project_path.is_dir():
        console.print("[red]Project directory does not exist.[/red]")
        return

    project_path = project_path.resolve()

    console.print(f"[dim]Inspecting: {project_path}[/dim]")
    console.print("[dim]Reading project structure and source files...[/dim]\n")

    results = scan_project(project_path)

    console.print(
        Panel(
            f"[bold]{project_path.name}[/bold]\n"
            f"Location: {project_path}\n"
            f"Source files: {results['total_files']}\n"
            f"Lines of code: {results['total_lines']}",
            title="PROJECT OVERVIEW",
            border_style="blue"
        )
    )

    language_table = Table(title="LANGUAGE BREAKDOWN")
    language_table.add_column("Language")
    language_table.add_column("Files", justify="right")

    for language, count in results["languages"].most_common():
        language_table.add_row(language, str(count))

    console.print(language_table)

    structure_table = Table(title="PROJECT STRUCTURE")
    structure_table.add_column("Top-level files and folders")

    for item in sorted(results["top_level_items"]):
        structure_table.add_row(item)

    console.print(structure_table)

    console.print(
        Panel(
            get_git_information(project_path),
            title="GIT STATUS",
            border_style="green"
        )
    )

    console.print("\n[bold green]Project scan completed.[/bold green]")
