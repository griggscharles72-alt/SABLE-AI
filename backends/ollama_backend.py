#!/usr/bin/env python3
import json
import os
import urllib.request
import urllib.error

DEFAULT_BASE = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("SABLE_OLLAMA_MODEL", "qwen2.5-coder:7b")

def _api_base():
    return DEFAULT_BASE.rstrip("/") + "/api"

def _request(path, payload=None):
    url = _api_base() + path
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "error": f"HTTP {exc.code}", "detail": detail}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

def version():
    return _request("/version")

def tags():
    return _request("/tags")

def available_models():
    data = tags()
    models = data.get("models", []) if isinstance(data, dict) else []
    return [m.get("name") for m in models if m.get("name")]

def health():
    v = version()
    models = available_models()
    if isinstance(v, dict) and v.get("error"):
        return {
            "ok": False,
            "backend": "ollama",
            "host": DEFAULT_BASE,
            "model": DEFAULT_MODEL,
            "error": v.get("error"),
            "detail": v.get("detail"),
        }
    return {
        "ok": True,
        "backend": "ollama",
        "host": DEFAULT_BASE,
        "model": DEFAULT_MODEL,
        "version": v.get("version"),
        "models": models,
    }

def ask(prompt: str, model: str = None, system: str = None):
    model = model or DEFAULT_MODEL
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    data = _request("/chat", {"model": model, "messages": messages, "stream": False})
    if isinstance(data, dict) and data.get("error"):
        return {"ok": False, "backend": "ollama", "model": model, "prompt": prompt, "error": data.get("error"), "detail": data.get("detail")}
    msg = data.get("message", {}) if isinstance(data, dict) else {}
    return {"ok": True, "backend": "ollama", "model": model, "prompt": prompt, "response": msg.get("content", ""), "raw": data}
