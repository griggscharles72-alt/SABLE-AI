#!/usr/bin/env python3
import json, sys, time
from pathlib import Path

timestamp = time.strftime("%Y%m%d_%H%M%S")
workspace = Path(__file__).parent
goal = sys.argv[1] if len(sys.argv) > 1 else "No goal"

response_text = f"Talking agent response to goal: '{goal}'"
log_file_json = workspace / f"conversation_{timestamp}.json"
log_file_md = workspace / f"conversation_{timestamp}.md"

# Write JSON log
log_file_json.write_text(json.dumps({"goal": goal, "response": response_text, "timestamp": timestamp}, indent=2))

# Write Markdown log
log_file_md.write_text(f"# Conversation log - {timestamp}\n\n**Goal:** {goal}\n\n**Response:** {response_text}\n")

# Output JSON to caller
print(json.dumps({"response": response_text}))
