#!/usr/bin/env python3
from tools.report_io import read_json, write_json, utc_now

MEMORY_PATH = "state/agent_memory.json"
RUN_ARTIFACT = "output/agent_run_latest.json"
REFLECTION_ARTIFACT = "output/agent_reflection_latest.json"

def load_memory():
    data = read_json(MEMORY_PATH, default={})
    if not data:
        data = {"runs": []}
    data.setdefault("runs", [])
    return data

def save_memory(data):
    write_json(MEMORY_PATH, data)
    return data

def append_run(run_summary):
    memory = load_memory()
    memory["runs"].append(run_summary)
    memory["runs"] = memory["runs"][-50:]
    save_memory(memory)
    return {"ok": True, "run_count": len(memory["runs"]), "latest_goal": run_summary.get("goal")}

def memory_status():
    memory = load_memory()
    latest = memory["runs"][-1] if memory["runs"] else {}
    return {
        "ok": True,
        "run_count": len(memory["runs"]),
        "latest_goal": latest.get("goal"),
        "latest_model": latest.get("model"),
        "latest_timestamp": latest.get("timestamp"),
    }

def reflect_latest():
    run = read_json(RUN_ARTIFACT, default={})
    if not run:
        return {"ok": False, "error": "no latest agent run artifact found", "expected": RUN_ARTIFACT}
    ai_result = run.get("ai_result", {})
    response = ai_result.get("response", "") if isinstance(ai_result, dict) else ""
    reflection = {
        "timestamp": utc_now(),
        "goal": run.get("goal"),
        "profile": run.get("profile"),
        "model": run.get("model"),
        "workspace_file_count": run.get("workspace_file_count", 0),
        "response_length": len(response),
        "checks": {
            "has_goal": bool(run.get("goal")),
            "has_response": bool(response.strip()),
            "response_long_enough": len(response.strip()) >= 40,
        },
        "next_actions": [
            "review output/agent_run_latest.md",
            "extract actionable file changes",
            "run another pass with a narrower goal if output is too broad",
        ],
    }
    write_json(REFLECTION_ARTIFACT, reflection)
    return {"ok": True, "reflection_artifact": REFLECTION_ARTIFACT, "response_length": len(response)}
