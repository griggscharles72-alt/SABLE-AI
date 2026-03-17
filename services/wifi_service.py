#!/usr/bin/env python3
from tools.report_io import utc_now, write_json, read_json
STATE_PATH = "state/wifi_last_report.json"
OUTPUT_PATH = "output/wifi_scan_latest.json"
def scan_networks():
    report = {"timestamp": utc_now(), "networks": []}
    write_json(STATE_PATH, report); write_json(OUTPUT_PATH, report); return report
def status():
    last = read_json(STATE_PATH, default={})
    return {"status": "operational", "last_scan_at": last.get("timestamp"), "network_count": len(last.get("networks", []))}
