from pathlib import Path
from documentation.scanner import scan_project


repository_path = Path("workspace/ANTON")

results = scan_project(repository_path)

print("\nANTON REPOSITORY SCAN")

print("Source files:", results["total_files"])
print("Total lines:", results["total_lines"])

print("\nLANGUAGES")

for language, count in results["languages"].most_common():
    print(language, count)

print("\nPROJECT STRUCTURE")

for item in results["project_tree"]:
    print(item)

print("\nCOLLECTED SOURCE FILES")

for file in results["source_files"]:
    print(file["path"], "-", file["lines"], "lines")

print("\nCONTEXT FILES:", len(results["context_files"]))