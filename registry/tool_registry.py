#!/usr/bin/env python3
from services.doctor_service import scan as doctor_scan, status as doctor_status
from services.sentinel_service import restore as sentinel_restore, verify as sentinel_verify, status as sentinel_status
from services.iphone_service import inspect as iphone_inspect, status as iphone_status
from services.traffic_service import start as traffic_start, stop as traffic_stop, status as traffic_status
from services.device_lab_service import check as device_lab_check, status as device_lab_status
from services.wifi_service import scan_networks as wifi_scan_networks, status as wifi_status

from tools.files_read import read_file
from tools.files_write import write_file
from tools.system_info import get_system_info
from tools.repo_audit import list_repo_files
from tools.workspace_io import workspace_list, workspace_manifest, workspace_write, workspace_read
from tools.workspace_index import index_workspace

from interfaces.ai_interface import query_ai as ai_ask, ai_health, ai_models
from agent.runtime import run as agent_run
from agent.reflection import reflect_latest as agent_reflect, memory_status as agent_memory_status

TOOL_REGISTRY = {
    "doctor.scan": doctor_scan,
    "doctor.status": doctor_status,

    "sentinel.restore": sentinel_restore,
    "sentinel.verify": sentinel_verify,
    "sentinel.status": sentinel_status,

    "iphone.inspect": iphone_inspect,
    "iphone.status": iphone_status,

    "traffic.start": traffic_start,
    "traffic.stop": traffic_stop,
    "traffic.status": traffic_status,

    "device_lab.check": device_lab_check,
    "device_lab.status": device_lab_status,

    "wifi.scan": wifi_scan_networks,
    "wifi.status": wifi_status,

    "read_file": read_file,
    "write_file": write_file,
    "system.info": get_system_info,
    "repo.audit": list_repo_files,

    "workspace.list": workspace_list,
    "workspace.manifest": workspace_manifest,
    "workspace.write": workspace_write,
    "workspace.read": workspace_read,
    "workspace.index": index_workspace,

    "ai.health": ai_health,
    "ai.models": ai_models,
    "ai.ask": ai_ask,

    "agent.run": agent_run,
    "agent.reflect": agent_reflect,
    "agent.memory_status": agent_memory_status,
}
