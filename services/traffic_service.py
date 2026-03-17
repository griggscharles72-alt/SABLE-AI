#!/usr/bin/env python3
from tools.report_io import utc_now, write_json, read_json
STATE_PATH = "state/traffic_state.json"
OUTPUT_PATH = "output/traffic_state_latest.json"
def start():
    report = {"status": "traffic monitoring started", "running": True, "started_at": utc_now(), "stopped_at": None}
    write_json(STATE_PATH, report); write_json(OUTPUT_PATH, report); return report
def stop():
    current = read_json(STATE_PATH, default={})
    report = {"status": "traffic monitoring stopped", "running": False, "started_at": current.get("started_at"), "stopped_at": utc_now()}
    write_json(STATE_PATH, report); write_json(OUTPUT_PATH, report); return report
def status():
    current = read_json(STATE_PATH, default={})
    if not current:
        return {"status": "operational", "running": False, "started_at": None, "stopped_at": None}
    return {"status": "operational", "running": current.get("running", False), "started_at": current.get("started_at"), "stopped_at": current.get("stopped_at")}
