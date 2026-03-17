from pathlib import Path

def write_file(filename, content, overwrite=True):
    path = Path(filename)
    if path.exists() and not overwrite:
        return {"error": "File exists and overwrite=False", "filepath": str(path)}
    path.write_text(content, encoding="utf-8")
    return {"filepath": str(path), "status": "written"}

if __name__ == "__main__":
    result = write_file("test_note.txt", "This is a test note.")
    print(result)
