import json
from pathlib import Path

CHECKPOINT_FILE = Path("state/checkpoints.json")

def save_checkpoint(name, data):
    checkpoint = load_checkpoints()
    checkpoint[name] = data
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))
    return checkpoint

def load_checkpoints():
    if not CHECKPOINT_FILE.exists():
        return {}
    return json.loads(CHECKPOINT_FILE.read_text())

if __name__ == "__main__":
    save_checkpoint("start", {"status": "ok"})
    print(load_checkpoints())
