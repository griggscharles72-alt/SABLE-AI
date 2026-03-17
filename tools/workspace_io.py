#!/usr/bin/env python3
from pathlib import Path

WORKSPACE_ROOT = Path("workspace")

def _root() -> Path:
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    return WORKSPACE_ROOT.resolve()

def _safe_path(relative_path: str) -> Path:
    root = _root()
    rel = Path(relative_path)
    target = (root / rel).resolve()
    if not str(target).startswith(str(root)):
        raise ValueError("path escapes workspace")
    return target

def workspace_list():
    root = _root()
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            files.append(str(p.relative_to(root)))
    return files

def workspace_manifest():
    files = workspace_list()
    return {"root": str(_root()), "file_count": len(files), "files": files}

def workspace_write(filename: str, content: str, overwrite: bool = True):
    target = _safe_path(filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        return {"ok": False, "filepath": str(target.relative_to(_root())), "error": "file exists and overwrite is false"}
    target.write_text(content, encoding="utf-8")
    return {"ok": True, "filepath": str(target.relative_to(_root())), "bytes_written": len(content.encode("utf-8"))}

def workspace_read(filepath: str):
    target = _safe_path(filepath)
    if not target.exists():
        return {"ok": False, "filepath": filepath, "error": "file not found"}
    return {"ok": True, "filepath": str(target.relative_to(_root())), "content": target.read_text(encoding="utf-8")}
