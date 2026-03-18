# SABLE-AI

SABLE-AI is a local-first runtime scaffold using one real local backend through Ollama.

## Current Reality

sable_agent_full.py -> workspace/ollama_backend.py -> ollama -> local model

## Primary Files

sable-agent/
├── README.md
├── sable_agent_full.py
├── launchers/
│   └── sable_ollama_agent.sh
├── workspace/
│   ├── ollama_backend.py
│   ├── ollama_config.json
│   └── datasets/
├── state/
│   └── agent_memory.json
└── output/
    ├── agent_run_latest.json
    ├── agent_run_latest.md
    └── conversations/

## What It Does Now

- sends a real goal string into Ollama
- chooses an installed local model
- captures the local-model response
- writes JSON and Markdown run artifacts
- writes per-run conversation logs
- tracks run memory in state/agent_memory.json

## Default Model Selection

Preferred models:
1. qwen2.5-coder:7b
2. llama3.2:1b

Override:
export SABLE_OLLAMA_MODEL="your-model-name"

## Run It

cd /home/pc-1/sable-agent-run/sable-agent && \
python3 sable_agent_full.py "Give me a direct status summary of this repo"

or

cd /home/pc-1/sable-agent-run/sable-agent && \
./launchers/sable_ollama_agent.sh "Tell me what this system can do right now"

## Notes

- this repo now uses one real backend only: Ollama
- cosmetic placeholder backends were removed
- conversation logs are written into output/conversations/
- latest run artifacts are written into output/
