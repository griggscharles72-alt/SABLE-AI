#!/usr/bin/env python3
from tools.system_info import get_system_info
from tools.report_io import utc_now, write_json, read_json

STATE_PATH = "state/device_lab_last_report.json"
OUTPUT_PATH = "output/device_lab_check_latest.json"

def check():
    report = {
        "status": "device check complete",
        "timestamp": utc_now(),
        "host": get_system_info(),
    }
    write_json(STATE_PATH, report)
    write_json(OUTPUT_PATH, report)
    return report

def status():
    last = read_json(STATE_PATH, default={})
    return {
        "status": "operational",
        "last_check_at": last.get("timestamp"),
        "has_report": bool(last),
    }

if __name__ == "__main__":
    print(check())
    print(status())
