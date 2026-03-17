#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from router.dispatch import dispatch, parse_payload, list_commands
from launchers.launch import launch

STATUS_COMMANDS = [
    "doctor.status",
    "sentinel.status",
    "iphone.status",
    "traffic.status",
    "device_lab.status",
    "wifi.status",
    "ai.health",
    "agent.memory_status",
]

SCAN_COMMANDS = [
    "doctor.scan",
    "iphone.inspect",
    "wifi.scan",
    "system.info",
    "repo.audit",
    "workspace.manifest",
    "workspace.index",
]

def run_status_all():
    return {cmd: dispatch(cmd) for cmd in STATUS_COMMANDS}

def run_scan_all():
    return {cmd: dispatch(cmd) for cmd in SCAN_COMMANDS}

def interactive_ai_loop():
    print("SABLE AI loop started.")
    print("Type a normal prompt to talk to the model.")
    print("Built-ins: list.commands, status.all, scan.all, exit")
    print("Deterministic command: run doctor.status")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break
        if line == "list.commands":
            print(json.dumps(list_commands(), indent=2)); continue
        if line == "status.all":
            print(json.dumps(run_status_all(), indent=2)); continue
        if line == "scan.all":
            print(json.dumps(run_scan_all(), indent=2)); continue
        if line.startswith("run "):
            print(json.dumps(dispatch(line[4:].strip()), indent=2)); continue
        print(json.dumps(dispatch("ai.ask", {"prompt": line}), indent=2))

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--ui":
        if sys.argv[2] == "ai":
            interactive_ai_loop()
            return
        print(json.dumps(launch(sys.argv[2]), indent=2))
        return

    if len(sys.argv) >= 2:
        command = sys.argv[1]
        if command in {"help", "--help", "-h"}:
            print(json.dumps({
                "status": "ok",
                "commands": [
                    "list.commands", "status.all", "scan.all",
                    "doctor.status", "doctor.scan",
                    "sentinel.restore", "sentinel.verify",
                    "iphone.inspect",
                    "traffic.start", "traffic.stop",
                    "device_lab.check",
                    "wifi.scan",
                    "system.info", "repo.audit",
                    "read_file", "write_file",
                    "workspace.list", "workspace.manifest", "workspace.write", "workspace.read", "workspace.index",
                    "ai.health", "ai.models", "ai.ask",
                    "agent.run", "agent.reflect", "agent.memory_status",
                    "--ui cli", "--ui ai"
                ]
            }, indent=2))
            return
        if command == "list.commands":
            print(json.dumps(list_commands(), indent=2)); return
        if command == "status.all":
            print(json.dumps(run_status_all(), indent=2)); return
        if command == "scan.all":
            print(json.dumps(run_scan_all(), indent=2)); return

        payload = parse_payload(sys.argv[2]) if len(sys.argv) >= 3 else None
        print(json.dumps(dispatch(command, payload), indent=2))
        return

    print(json.dumps({"status": "ok", "usage": ["python3 run_sable.py help"]}, indent=2))

if __name__ == "__main__":
    main()
