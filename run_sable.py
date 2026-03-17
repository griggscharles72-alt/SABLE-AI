#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from router.dispatch import dispatch, parse_payload
from launchers.launch import launch

def interactive_ai_loop():
    print("SABLE AI loop started. Type commands like: run doctor.status")
    print("Type: exit")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break

        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break

        if line.startswith("run "):
            command = line[4:].strip()
            result = dispatch(command)
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({"echo": line, "status": "placeholder"}, indent=2))

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--ui":
        ui = sys.argv[2]
        if ui == "ai":
            interactive_ai_loop()
            return
        print(json.dumps(launch(ui), indent=2))
        return

    if len(sys.argv) >= 2:
        command = sys.argv[1]
        payload = parse_payload(sys.argv[2]) if len(sys.argv) >= 3 else None
        result = dispatch(command, payload)
        print(json.dumps(result, indent=2))
        return

    print(json.dumps({
        "status": "ok",
        "usage": [
            "python3 run_sable.py doctor.status",
            "python3 run_sable.py sentinel.restore '{\"create_baseline\": true}'",
            "python3 run_sable.py write_file '{\"filename\":\"notes.txt\",\"content\":\"hello\",\"overwrite\":true}'",
            "python3 run_sable.py --ui cli",
            "python3 run_sable.py --ui ai"
        ]
    }, indent=2))

if __name__ == "__main__":
    main()
