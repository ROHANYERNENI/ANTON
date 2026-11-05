
import os
from pathlib import Path
from collections import Counter


# Directories that should never be scanned.
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
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache"
}


# Source-code languages recognized by ANTON.
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


# Project configuration and documentation files.
IMPORTANT_FILES = {
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "package-lock.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "cargo.toml",
    "go.mod",
    "makefile",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".gitignore"
}


# Files that must never be sent to an AI provider.
IGNORED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "credentials.json",
    "secrets.json",
    "id_rsa",
    "id_ed25519"
}


MAX_FILE_SIZE = 100_000
MAX_TOTAL_CONTENT = 300_000
MAX_FILES = 250


def should_ignore_file(filename):

    name = filename.lower()

    if name in IGNORED_FILES:
        return True

    if name.startswith(".env"):
        return True

    if name.endswith((".pem", ".key", ".p12", ".pfx")):
        return True

    return False


def scan_project(project_path):

    project_path = Path(project_path).expanduser().resolve()

    if not project_path.is_dir():
        raise ValueError("Invalid repository directory.")

    language_counts = Counter()

    total_files = 0
    total_lines = 0
    total_content = 0

    top_level_items = [
        item.name for item in project_path.iterdir()
    ]

    project_tree = []
    source_files = []
    context_files = []

    for root, directories, filenames in os.walk(project_path):

        directories[:] = sorted([
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
            and not (Path(root) / directory).is_symlink()
        ])

        for filename in sorted(filenames):

            if should_ignore_file(filename):
                continue

            file_path = Path(root) / filename

            if file_path.is_symlink():
                continue

            relative_path = file_path.relative_to(project_path)

            project_tree.append(str(relative_path))

            extension = file_path.suffix.lower()

            is_source = extension in LANGUAGES

            is_important = filename.lower() in IMPORTANT_FILES

            if not is_source and not is_important:
                continue

            if len(context_files) >= MAX_FILES:
                break

            try:

                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue

                with file_path.open(
                    "r",
                    encoding="utf-8"
                ) as file:
                    content = file.read()

                if "\x00" in content:
                    continue

                if total_content + len(content) > MAX_TOTAL_CONTENT:
                    continue

                lines = content.count("\n")

                if content and not content.endswith("\n"):
                    lines += 1

                file_information = {
                    "path": str(relative_path),
                    "content": content,
                    "lines": lines
                }

                context_files.append(file_information)

                total_content += len(content)

                if is_source:

                    language = LANGUAGES[extension]

                    language_counts[language] += 1
                    total_files += 1
                    total_lines += lines

                    source_files.append({
                        **file_information,
                        "language": language
                    })

            except (OSError, UnicodeDecodeError):
                continue

        if len(context_files) >= MAX_FILES:
            break

    return {
        "languages": language_counts,
        "total_files": total_files,
        "total_lines": total_lines,
        "top_level_items": top_level_items,
        "project_tree": sorted(project_tree),
        "source_files": source_files,
        "context_files": context_files
    }
