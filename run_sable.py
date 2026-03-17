#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from router.dispatch import dispatch, parse_payload, list_commands
from launchers.launch import launch
from interfaces.ai_interface import query_ai

STATUS_COMMANDS = [
    "doctor.status",
    "sentinel.status",
    "iphone.status",
    "traffic.status",
    "device_lab.status",
    "wifi.status",
]

SCAN_COMMANDS = [
    "doctor.scan",
    "iphone.inspect",
    "wifi.scan",
    "system.info",
    "repo.audit",
]

def run_status_all():
    return {cmd: dispatch(cmd) for cmd in STATUS_COMMANDS}

def run_scan_all():
    return {cmd: dispatch(cmd) for cmd in SCAN_COMMANDS}

def interactive_ai_loop():
    print("SABLE AI loop started. Type: run doctor.status")
    print("Other commands: list.commands, status.all, scan.all, exit")
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
            print(json.dumps(list_commands(), indent=2))
            continue

        if line == "status.all":
            print(json.dumps(run_status_all(), indent=2))
            continue

        if line == "scan.all":
            print(json.dumps(run_scan_all(), indent=2))
            continue

        print(json.dumps(query_ai(line), indent=2))

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

        if command in {"help", "--help", "-h"}:
            print(json.dumps({
                "status": "ok",
                "commands": [
                    "list.commands",
                    "status.all",
                    "scan.all",
                    "doctor.status",
                    "doctor.scan",
                    "sentinel.restore",
                    "sentinel.verify",
                    "iphone.inspect",
                    "traffic.start",
                    "traffic.stop",
                    "device_lab.check",
                    "wifi.scan",
                    "system.info",
                    "repo.audit",
                    "read_file",
                    "write_file",
                    "--ui cli",
                    "--ui ai"
                ]
            }, indent=2))
            return

        if command == "list.commands":
            print(json.dumps(list_commands(), indent=2))
            return

        if command == "status.all":
            print(json.dumps(run_status_all(), indent=2))
            return

        if command == "scan.all":
            print(json.dumps(run_scan_all(), indent=2))
            return

        payload = parse_payload(sys.argv[2]) if len(sys.argv) >= 3 else None
        print(json.dumps(dispatch(command, payload), indent=2))
        return

    print(json.dumps({
        "status": "ok",
        "usage": [
            "python3 run_sable.py help",
            "python3 run_sable.py list.commands",
            "python3 run_sable.py status.all",
            "python3 run_sable.py scan.all",
            "python3 run_sable.py doctor.status",
            "python3 run_sable.py sentinel.restore '{\"create_baseline\": true}'",
            "python3 run_sable.py write_file '{\"filename\":\"notes.txt\",\"content\":\"hello\",\"overwrite\":true}'",
            "python3 run_sable.py --ui cli",
            "python3 run_sable.py --ui ai"
        ]
    }, indent=2))

if __name__ == "__main__":
    main()
