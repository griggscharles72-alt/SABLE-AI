#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from interfaces.cli_ui import start_cli
from interfaces.ai_interface import start_ai_loop

def launch(ui="cli"):
    if ui == "cli":
        return start_cli()
    if ui == "ai":
        return start_ai_loop()
    if ui == "tk":
        return {"status": "tk launcher placeholder"}
    return {"error": "unknown ui", "ui": ui}

if __name__ == "__main__":
    ui = sys.argv[1] if len(sys.argv) > 1 else "cli"
    print(launch(ui))
