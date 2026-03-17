#!/usr/bin/env python3
from pathlib import Path
from tools.report_io import write_json, utc_now

WORKSPACE_ROOT = Path("workspace")
OUTPUT_PATH = "output/workspace_index_latest.json"

def index_workspace():
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    files = []
    for p in sorted(WORKSPACE_ROOT.rglob("*")):
        if p.is_file():
            files.append({"path": str(p.relative_to(WORKSPACE_ROOT)), "size": p.stat().st_size})
    report = {
        "timestamp": utc_now(),
        "root": str(WORKSPACE_ROOT.resolve()),
        "file_count": len(files),
        "files": files
    }
    write_json(OUTPUT_PATH, report)
    return report
