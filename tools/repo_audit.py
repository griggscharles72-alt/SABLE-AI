#!/usr/bin/env python3
import os

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
}

SKIP_FILES = {
    "sync_log.txt",
    "push_log.txt",
}

def list_repo_files(base_dir="."):
    results = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name in SKIP_FILES:
                continue
            path = os.path.relpath(os.path.join(root, name), base_dir)
            results.append(path)
    return sorted(results)

if __name__ == "__main__":
    items = list_repo_files()
    print(items)
