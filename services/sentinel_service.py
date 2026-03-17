#!/usr/bin/env python3
from tools.system_info import get_system_info
from tools.repo_audit import list_repo_files
from tools.report_io import utc_now, write_json, read_json

BASELINE_PATH = "state/baseline.json"
REPORT_PATH = "state/sentinel_last_report.json"

def restore(create_baseline=False):
    baseline = {
        "timestamp": utc_now(),
        "system_info": get_system_info(),
        "repo_file_count": len(list_repo_files()),
    }

    if create_baseline:
        write_json(BASELINE_PATH, baseline)

    report = {
        "status": "restore complete",
        "baseline_created": create_baseline,
        "timestamp": utc_now(),
        "baseline_path": BASELINE_PATH if create_baseline else None,
    }
    write_json(REPORT_PATH, report)
    return report

def verify():
    baseline = read_json(BASELINE_PATH, default={})
    report = {
        "status": "verification complete",
        "timestamp": utc_now(),
        "baseline_present": bool(baseline),
        "baseline_timestamp": baseline.get("timestamp"),
    }
    write_json(REPORT_PATH, report)
    return report

def status():
    last = read_json(REPORT_PATH, default={})
    return {
        "status": "operational",
        "last_event_at": last.get("timestamp"),
        "baseline_present": bool(read_json(BASELINE_PATH, default={})),
    }

if __name__ == "__main__":
    print(restore(True))
    print(verify())
    print(status())
