#!/usr/bin/env python3
from router.dispatch import dispatch

def query_ai(prompt):
    prompt = (prompt or "").strip()
    if prompt.startswith("run "):
        cmd = prompt[4:].strip()
        return dispatch(cmd)
    return {
        "ok": True,
        "prompt": prompt,
        "response": "AI placeholder response",
    }

def start_ai_loop():
    return {
        "ok": True,
        "interface": "ai",
        "status": "ready",
        "hint": "Use input like: run doctor.status",
    }

if __name__ == "__main__":
    import json
    print(json.dumps(start_ai_loop(), indent=2))
    print(json.dumps(query_ai("run doctor.status"), indent=2))
