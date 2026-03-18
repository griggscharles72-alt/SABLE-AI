#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
OUTPUT_DIR = BASE_DIR / "output"
CONV_DIR = OUTPUT_DIR / "conversations"
CONFIG_PATH = WORKSPACE_DIR / "ollama_config.json"

CONV_DIR.mkdir(parents=True, exist_ok=True)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def list_models():
    result = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ollama list failed")
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    models = []
    for line in lines[1:]:
        parts = line.split()
        if parts:
            models.append(parts[0])
    return models

def choose_model(installed, preferred):
    env_model = os.environ.get("SABLE_OLLAMA_MODEL", "").strip()
    if env_model:
        return env_model
    for model in preferred:
        if model in installed:
            return model
    return installed[0] if installed else None

def main():
    goal = " ".join(sys.argv[1:]).strip() or "No goal specified"
    config = read_json(CONFIG_PATH, default={}) or {}
    preferred_models = config.get("preferred_models") or []
    prompt_preamble = config.get("prompt_preamble") or "You are SABLE's local runtime brain. Return plain text only."

    try:
        installed_models = list_models()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "backend": "ollama",
            "goal": goal,
            "error": str(exc),
            "timestamp": utc_now()
        }))
        return

    model = choose_model(installed_models, preferred_models)
    if not model:
        print(json.dumps({
            "ok": False,
            "backend": "ollama",
            "goal": goal,
            "error": "no_models_installed",
            "installed_models": installed_models,
            "timestamp": utc_now()
        }))
        return

    prompt = f"{prompt_preamble}\n\nGoal:\n{goal}\n"

    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True
    )

    response_text = (result.stdout or "").strip()
    stderr_text = (result.stderr or "").strip()
    ok = result.returncode == 0 and bool(response_text)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    conversation_json = CONV_DIR / f"conversation_{stamp}.json"
    conversation_md = CONV_DIR / f"conversation_{stamp}.md"

    payload = {
        "ok": ok,
        "backend": "ollama",
        "goal": goal,
        "model": model,
        "installed_models": installed_models,
        "response": response_text if response_text else "",
        "error": stderr_text if not ok else "",
        "conversation_json": str(conversation_json),
        "conversation_md": str(conversation_md),
        "timestamp": utc_now()
    }

    conversation_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    conversation_md.write_text(
        "# SABLE Ollama Conversation\n\n"
        f"**Timestamp:** {payload['timestamp']}\n\n"
        f"**Model:** {model}\n\n"
        f"**Goal:** {goal}\n\n"
        "## Response\n\n"
        f"{payload['response']}\n",
        encoding="utf-8"
    )

    print(json.dumps(payload))

if __name__ == "__main__":
    main()
