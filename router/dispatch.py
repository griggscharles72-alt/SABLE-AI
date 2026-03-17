#!/usr/bin/env python3
import json
from registry.tool_registry import TOOL_REGISTRY

def dispatch(command: str, payload=None):
    if command not in TOOL_REGISTRY:
        return {"error": "unknown command", "command": command}

    fn = TOOL_REGISTRY[command]

    if payload is None:
        return fn()

    if isinstance(payload, dict):
        return fn(**payload)

    return fn(payload)

def parse_payload(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw

if __name__ == "__main__":
    print(dispatch("doctor.status"))
