# SABLE-AI

SABLE-AI is a local-first Python prototype for deterministic service execution, tool routing, memory/state scaffolding, and structured artifact generation.

## Current Status

Working layers currently in the repo:

- tools layer
- memory layer
- services layer
- interfaces layer
- registry/router/launcher/entrypoint wiring
- state/report artifact generation

The system is currently capable of:

- dispatching named commands through `run_sable.py`
- running aggregate command groups like `status.all` and `scan.all`
- writing service artifacts into `state/` and `output/`
- operating through a basic CLI and placeholder AI loop

## Repository Root

Primary local repo path:

```bash
/home/pc-1/sable-agent-run/sable-agent
```

Primary GitHub repo:

```text
https://github.com/griggscharles72-alt/SABLE-AI
```

## File Structure

```text
sable-agent/
├── README.md
├── requirements.txt
├── .gitignore
├── run_sable.py
├── agent/
├── backends/
├── interfaces/
├── launchers/
├── memory/
├── registry/
├── router/
├── services/
├── state/
├── output/
├── tools/
└── workspace/
```

## Architecture

- Tools layer: low-level helpers used by services and routing logic.
- Memory layer: small state helpers and persistence scaffolds.
- Services layer: deterministic named service surfaces.
- Registry/router: central dispatch path.
- Interfaces layer: CLI, AI placeholder loop, Tkinter placeholder.

Dispatch flow:

```text
run_sable.py -> router/dispatch.py -> registry/tool_registry.py -> service/tool function
```

## Current Commands

### Discovery

```bash
cd /home/pc-1/sable-agent-run/sable-agent && python3 run_sable.py help
cd /home/pc-1/sable-agent-run/sable-agent && python3 run_sable.py list.commands
```

### Aggregate Commands

```bash
cd /home/pc-1/sable-agent-run/sable-agent && python3 run_sable.py status.all
cd /home/pc-1/sable-agent-run/sable-agent && python3 run_sable.py scan.all
```

### Interfaces

```bash
cd /home/pc-1/sable-agent-run/sable-agent && python3 run_sable.py --ui cli
cd /home/pc-1/sable-agent-run/sable-agent && python3 run_sable.py --ui ai
```

## State and Output Artifacts

### state/

- baseline.json
- sentinel_last_report.json
- doctor_last_report.json
- iphone_last_report.json
- traffic_state.json
- device_lab_last_report.json
- wifi_last_report.json
- sable.db

### output/

- doctor_scan_latest.json
- iphone_inspect_latest.json
- traffic_state_latest.json
- device_lab_check_latest.json
- wifi_scan_latest.json

## Local Setup

```bash
cd /home/pc-1/sable-agent-run/sable-agent && python3 -m pip install -r requirements.txt
```

## Quick Smoke Test

```bash
cd /home/pc-1/sable-agent-run/sable-agent && \
python3 run_sable.py help && \
python3 run_sable.py list.commands && \
python3 run_sable.py status.all && \
python3 run_sable.py scan.all
```

## Git Workflow

```bash
cd /home/pc-1/sable-agent-run/sable-agent
git add .
git commit -m "update message"
git push origin main
```

## Notes

This project is being built with a local-first repo workflow:

- build locally
- test locally
- sync to GitHub afterward
- prefer deterministic service surfaces before heavier AI/backend expansion
