
import json
from pathlib import Path

from documentation.scanner import scan_project
from documentation.context_builder import build_project_context
from documentation.generator import generate_documentation
from documentation.writer import write_documentation


def main():

    # Load ANTON configuration

    config_path = Path.home() / ".anton" / "config.json"

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    repository_path = config.get("git_local_path")

    if not repository_path:
        raise RuntimeError("No Git repository is connected.")

    repository_path = Path(repository_path).expanduser().resolve()

    if not repository_path.is_dir():
        raise RuntimeError("Connected repository does not exist.")

    print("\nANTON DOCUMENTATION ENGINE")
    print("==========================")

    # STEP 1: Scan repository

    print("\n[1/4] Scanning repository...")

    scan_results = scan_project(repository_path)

    print("Source files:", scan_results["total_files"])
    print("Source lines:", scan_results["total_lines"])

    # STEP 2: Build context

    print("\n[2/4] Building repository context...")

    project_context = build_project_context(
        repository_path,
        scan_results
    )

    print("Context characters:", len(project_context))

    # STEP 3: Generate documentation

    print("\n[3/4] Generating documentation...")

    documents = generate_documentation(
        config,
        project_context
    )

    # STEP 4: Save documentation

    print("\n[4/4] Saving documentation...")

    results = write_documentation(
        repository_path,
        documents,
        overwrite=False
    )

    print("\nDOCUMENTATION RESULTS")
    print("=====================")

    for filename in results["saved"]:
        print("Saved:", filename)

    for filename in results["skipped"]:
        print("Skipped (already exists):", filename)

    print("\nDocumentation directory:")
    print(results["directory"])

    print("\nANTON documentation process completed.")


if __name__ == "__main__":
    main()

