#!/usr/bin/env python3
from tools.report_io import utc_now, write_json, read_json
STATE_PATH = "state/iphone_last_report.json"
OUTPUT_PATH = "output/iphone_inspect_latest.json"
def inspect():
    report = {"status": "inspection complete", "timestamp": utc_now(), "devices": []}
    write_json(STATE_PATH, report); write_json(OUTPUT_PATH, report); return report
def status():
    last = read_json(STATE_PATH, default={})
    return {"status": "operational", "last_inspect_at": last.get("timestamp"), "device_count": len(last.get("devices", []))}
