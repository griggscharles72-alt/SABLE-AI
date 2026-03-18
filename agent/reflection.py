#!/usr/bin/env python3
import json
from pathlib import Path
from tools.report_io import write_json, read_json, utc_now

MEMORY_JSON = Path("state/agent_memory.json")

def append_run(run_entry: dict) -> dict:
    memory = read_json(str(MEMORY_JSON), default={"runs": []})
    if "runs" not in memory or not isinstance(memory["runs"], list):
        memory["runs"] = []
    if "timestamp" not in run_entry:
        run_entry["timestamp"] = utc_now()
    memory["runs"].append(run_entry)
    write_json(MEMORY_JSON, memory)
    return memory

def reflect_latest() -> dict:
    memory = read_json(str(MEMORY_JSON), default={"runs": []})
    runs = memory.get("runs", [])
    return runs[-1] if runs else {}

def memory_status() -> dict:
    memory = read_json(str(MEMORY_JSON), default={"runs": []})
    return {"runs": len(memory.get("runs", []))}
