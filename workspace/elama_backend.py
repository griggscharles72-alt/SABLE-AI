#!/usr/bin/env python3
import subprocess, sys, json
engine = "/home/pc-1/sable-agent-run/sable-agent/workspace/agent_engine.py"
goal = sys.argv[1] if len(sys.argv) > 1 else "No goal"
try:
    result = subprocess.run([engine, goal], capture_output=True, text=True, check=True)
    print(json.dumps(json.loads(result.stdout)))
except Exception as e:
    print(json.dumps({"response": str(e)}))
