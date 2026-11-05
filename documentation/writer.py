
from pathlib import Path


ALLOWED_DOCUMENTS = {
    "README.md",
    "ARCHITECTURE.md"
}


def write_documentation(project_path, documents, overwrite=False):

    project_path = Path(project_path).expanduser().resolve()

    if not project_path.is_dir():
        raise ValueError("Invalid repository directory.")

    documentation_directory = project_path / "docs"

    documentation_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    saved_files = []
    skipped_files = []

    for filename, content in documents.items():

        if filename not in ALLOWED_DOCUMENTS:
            raise ValueError(
                f"Unsupported documentation filename: {filename}"
            )

        if not isinstance(content, str) or not content.strip():
            raise ValueError(
                f"Documentation content is empty: {filename}"
            )

        destination = documentation_directory / filename

        if destination.exists() and not overwrite:

            skipped_files.append(filename)
            continue

        temporary_file = destination.with_name(
            destination.name + ".tmp"
        )

        try:

            temporary_file.write_text(
                content,
                encoding="utf-8"
            )

            temporary_file.replace(destination)

            saved_files.append(str(destination))

        except OSError:

            if temporary_file.exists():
                temporary_file.unlink()

            raise

    return {
        "saved": saved_files,
        "skipped": skipped_files,
        "directory": str(documentation_directory)
    }
