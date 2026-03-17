#!/usr/bin/env python3
from backends.ollama_backend import ask as ollama_ask, health as ollama_health, available_models

def query_ai(prompt, model=None, system=None):
    return ollama_ask(prompt=prompt, model=model, system=system)

def ai_health():
    return ollama_health()

def ai_models():
    return {"ok": True, "backend": "ollama", "models": available_models()}

def start_ai_loop():
    return {"ok": True, "interface": "ai", "backend": "ollama", "status": "ready"}
