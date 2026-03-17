#!/usr/bin/env python3
import json
from registry.tool_registry import TOOL_REGISTRY

def list_commands():
    return sorted(TOOL_REGISTRY.keys())

def dispatch(command: str, payload=None):
    if command == "list.commands":
        return list_commands()

    if command not in TOOL_REGISTRY:
        return {"ok": False, "error": "unknown command", "command": command}

    fn = TOOL_REGISTRY[command]

    try:
        if payload is None:
            result = fn()
        elif isinstance(payload, dict):
            result = fn(**payload)
        else:
            result = fn(payload)

        return {
            "ok": True,
            "command": command,
            "result": result,
        }
    except Exception as exc:
        return {
            "ok": False,
            "command": command,
            "error": str(exc),
        }

def parse_payload(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw

if __name__ == "__main__":
    print(json.dumps(dispatch("doctor.status"), indent=2))
