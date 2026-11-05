
from pathlib import Path


MAX_CONTEXT_SIZE = 120_000


def build_project_context(project_path, scan_results):

    project_path = Path(project_path).resolve()

    context = []

    context.append("# REPOSITORY INFORMATION")

    context.append(f"Project name: {project_path.name}")
    context.append(f"Project location: {project_path}")

    context.append(
        f"Total source files: {scan_results['total_files']}"
    )

    context.append(
        f"Total source lines: {scan_results['total_lines']}"
    )

    context.append("\n# PROGRAMMING LANGUAGES")

    for language, count in scan_results["languages"].most_common():
        context.append(f"{language}: {count} files")

    context.append("\n# PROJECT STRUCTURE")

    for file_path in scan_results["project_tree"]:
        context.append(file_path)

    context.append("\n# SOURCE CODE AND CONFIGURATION")

    remaining_size = MAX_CONTEXT_SIZE

    for file in scan_results["context_files"]:

        file_path = file["path"]
        content = file["content"]

        section = (
            f"\n## FILE: {file_path}\n"
            f"```text\n{content}\n```\n"
        )

        if len(section) > remaining_size:

            if remaining_size <= 0:
                break

            context.append(
                f"\n## FILE: {file_path}\n"
                "[File omitted because the context limit was reached.]"
            )

            break

        context.append(section)
        remaining_size -= len(section)

    return "\n".join(context)

