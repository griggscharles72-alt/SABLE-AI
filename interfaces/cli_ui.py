#!/usr/bin/env python3
from router.dispatch import dispatch

def run_command(command, payload=None):
    return dispatch(command, payload)

def start_cli():
    return {
        "ok": True,
        "interface": "cli",
        "status": "ready",
        "usage": [
            "python3 run_sable.py list.commands",
            "python3 run_sable.py doctor.status",
            "python3 run_sable.py status.all",
            "python3 run_sable.py scan.all",
        ],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(start_cli(), indent=2))
    print(json.dumps(run_command("doctor.status"), indent=2))
