from pathlib import Path

def read_file(filepath):
    path = Path(filepath)
    if not path.exists():
        return {"error": "File not found", "filepath": str(path)}
    content = path.read_text(encoding="utf-8")
    return {"filepath": str(path), "content": content}

if __name__ == "__main__":
    result = read_file("README.md")
    print(result)
