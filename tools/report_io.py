#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def write_json(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return str(p)

def read_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return {} if default is None else default
    return json.loads(p.read_text(encoding="utf-8"))
