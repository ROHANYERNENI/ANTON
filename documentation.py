
import os
import re
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from ai_client import generate_text


console = Console()


# Directories ANTON should ignore.
IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".idea",
    ".vscode",
    ".next",
    "dist",
    "build",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "vendor"
}


# Files ANTON should never send to the AI.
IGNORED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json"
}


# Supported source and configuration file extensions.
SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
    ".html", ".css", ".c", ".cpp", ".h", ".hpp",
    ".swift", ".go", ".rs", ".php", ".rb", ".sql",
    ".json", ".yaml", ".yml", ".toml", ".xml",
    ".md", ".txt", ".gradle", ".properties",
    ".sh", ".bat"
}


MAX_FILE_SIZE = 100_000
MAX_CONTEXT_SIZE = 50_000
MAX_FILES = 150


def should_ignore_file(file_path):
    """Check whether a file should be excluded."""

    name = file_path.name.lower()

    if name in IGNORED_FILES:
        return True

    if name.startswith(".env."):
        return True

    ignored_extensions = {
        ".pem", ".key", ".p12", ".pfx", ".jks",
        ".keystore", ".sqlite", ".db", ".png",
        ".jpg", ".jpeg", ".gif", ".pdf", ".zip",
        ".mp4", ".mp3", ".dylib", ".so", ".dll"
    }

    if file_path.suffix.lower() in ignored_extensions:
        return True

    return file_path.suffix.lower() not in SUPPORTED_EXTENSIONS


def redact_secrets(content):
    """Redact common hardcoded secrets before sending code to AI."""

    patterns = [
        r'(?i)(api[_-]?key\s*[:=]\s*)["\'][^"\']+["\']',
        r'(?i)(secret\s*[:=]\s*)["\'][^"\']+["\']',
        r'(?i)(password\s*[:=]\s*)["\'][^"\']+["\']',
        r'(?i)(access[_-]?token\s*[:=]\s*)["\'][^"\']+["\']'
    ]

    for pattern in patterns:
        content = re.sub(
            pattern,
            r'\1"[REDACTED]"',
            content
        )

    return content


def collect_project_context(project_path):
    """Collect the repository structure and selected source files."""

    project_tree = []
    source_context = []

    total_files = 0
    included_files = 0
    context_size = 0

    for root, directories, filenames in os.walk(project_path):

        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
            and not (Path(root) / directory).is_symlink()
        )

        relative_root = Path(root).relative_to(project_path)

        for directory in directories:
            directory_path = relative_root / directory
            project_tree.append(f"{directory_path}/")

        for filename in sorted(filenames):

            file_path = Path(root) / filename

            if file_path.is_symlink():
                continue

            total_files += 1

            relative_path = file_path.relative_to(project_path)

            if should_ignore_file(file_path):
                continue

            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue

                content = file_path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                content = redact_secrets(content)

                remaining_space = MAX_CONTEXT_SIZE - context_size

                if remaining_space <= 0:
                    break

                if included_files >= MAX_FILES:
                    break

                file_section = (
                    f"\n\n--- FILE: {relative_path} ---\n"
                    f"{content}"
                )

                file_section = file_section[:remaining_space]

                source_context.append(file_section)

                context_size += len(file_section)
                included_files += 1

            except OSError:
                continue

        if context_size >= MAX_CONTEXT_SIZE:
            break

        if included_files >= MAX_FILES:
            break

    tree_text = "\n".join(project_tree[:500])
    source_text = "\n".join(source_context)

    context = f"""
PROJECT STRUCTURE:

{tree_text}

SOURCE CODE AND CONFIGURATION:

{source_text}
"""

    return context, {
        "total_files": total_files,
        "included_files": included_files
    }


def clean_markdown_response(response):
    """Remove unnecessary outer Markdown code fences."""

    response = response.strip()

    if response.startswith("```markdown"):
        response = response[len("```markdown"):].strip()

    elif response.startswith("```md"):
        response = response[len("```md"):].strip()

    elif response.startswith("```"):
        response = response[3:].strip()

    if response.endswith("```"):
        response = response[:-3].strip()

    return response


def generate_document(config, project_context, document_type):
    """Generate documentation using ANTON's configured AI."""

    if document_type == "README":

        prompt = f"""
You are a senior software engineer writing technical documentation.

Generate a clear and professional README.md for this repository.

Use only the supplied project structure and source code as evidence.

Include these sections when the available information supports them:

1. Project title
2. Project overview
3. Features
4. Technology stack
5. Project structure
6. Installation and setup
7. Configuration
8. How to run the project
9. Usage examples
10. Future improvements

Rules:
- Do not invent features.
- Do not invent installation commands.
- Do not invent environment variables.
- Do not claim something works unless the source supports it.
- If important information is missing, state that it is not specified.
- Return Markdown only.

REPOSITORY CONTEXT:

{project_context}
"""

    elif document_type == "ARCHITECTURE":

        prompt = f"""
You are a senior software architect documenting a software repository.

Generate an ARCHITECTURE.md explaining the actual architecture.

Use only the supplied project structure and source code as evidence.

Include these sections when the available information supports them:

1. Architecture overview
2. Main components and their responsibilities
3. Important modules and files
4. How components interact
5. Data flow
6. External services and integrations
7. Configuration and persistence
8. Important design decisions
9. Current limitations

Rules:
- Explain the architecture that exists, not an ideal architecture.
- Do not invent modules, APIs, databases, or integrations.
- Distinguish confirmed behavior from reasonable inference.
- Identify missing information instead of guessing.
- Return Markdown only.

REPOSITORY CONTEXT:

{project_context}
"""

    else:
        raise ValueError(
            f"Unsupported document type: {document_type}"
        )

    response = generate_text(
        config=config,
        prompt=prompt
    )

    return clean_markdown_response(response)


def generate_documentation(config):
    """Generate README and architecture documentation."""

    console.print(
        "\n[bold cyan]ANTON DOCUMENTATION ENGINE[/bold cyan]\n"
    )

    repository_path = config.get("git_local_path")

    if not repository_path:
        console.print(
            "[red]No repository is connected. "
            "Connect a Git repository first.[/red]"
        )
        return

    project_path = Path(repository_path).expanduser()

    if not project_path.is_dir():
        console.print(
            "[red]Connected repository does not exist.[/red]"
        )
        return

    project_path = project_path.resolve()

    console.print(
        f"[dim]Repository: {project_path}[/dim]"
    )

    console.print(
        "[dim]Collecting project structure and source code...[/dim]\n"
    )

    project_context, statistics = collect_project_context(
        project_path
    )

    console.print(
        f"Files discovered: {statistics['total_files']}"
    )

    console.print(
        f"Files included in AI context: {statistics['included_files']}"
    )

    if statistics["included_files"] == 0:
        console.print(
            "[red]No supported source files were found.[/red]"
        )
        return

    documentation_directory = project_path / "docs"

    try:
        documentation_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        console.print(
            "\n[cyan]Generating README.md...[/cyan]"
        )

        readme = generate_document(
            config,
            project_context,
            "README"
        )

        if not readme.strip():
            raise RuntimeError(
                "AI returned an empty README."
            )

        console.print(
            "[cyan]Generating ARCHITECTURE.md...[/cyan]"
        )

        architecture = generate_document(
            config,
            project_context,
            "ARCHITECTURE"
        )

        if not architecture.strip():
            raise RuntimeError(
                "AI returned empty architecture documentation."
            )

        readme_path = documentation_directory / "README.md"

        architecture_path = (
            documentation_directory / "ARCHITECTURE.md"
        )

        readme_path.write_text(
            readme + "\n",
            encoding="utf-8"
        )

        architecture_path.write_text(
            architecture + "\n",
            encoding="utf-8"
        )

        console.print(
            Panel(
                f"README: {readme_path}\n\n"
                f"Architecture: {architecture_path}",
                title="Documentation generated successfully",
                border_style="green"
            )
        )

    except Exception as error:

        console.print(
            "\n[bold red]Documentation generation failed[/bold red]"
        )

        console.print(str(error))
