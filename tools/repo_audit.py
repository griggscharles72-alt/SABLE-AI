import os

def list_repo_files(base_dir="."):
    files = []
    for root, dirs, filenames in os.walk(base_dir):
        for f in filenames:
            files.append(os.path.relpath(os.path.join(root, f), base_dir))
    return files

if __name__ == "__main__":
    all_files = list_repo_files()
    print(f"Files in repo ({len(all_files)}):")
    for f in all_files:
        print(f" - {f}")
