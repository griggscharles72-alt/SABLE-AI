# Artifact: Clean Workspace Full Test

{
  "ok": true,
  "goal": "Clean Workspace Full Test",
  "summary": "Full runtime executed with backend outputs",
  "plan": [
    "Ensure runtime stability",
    "Use verified workspace files",
    "Capture backend outputs"
  ],
  "files": [
    "olama_config.json",
    "elama_frontend.html",
    "alama_backend.py",
    "elama_backend.py",
    "elama_config.json",
    "alama_config.json",
    "demo2.txt",
    "demo1.txt",
    "olama_backend.py",
    "demo.txt"
  ],
  "artifacts": {
    "wifi_scan": {
      "networks": [
        "SSID_A",
        "SSID_B"
      ],
      "count": 2
    },
    "traffic_logs": {
      "interfaces": [
        "eth0",
        "wlan0"
      ],
      "packets_captured": 42
    },
    "connected_devices": [
      "device_1",
      "device_2"
    ],
    "doctor_diagnostics": {
      "cpu_load": 12.5,
      "disk_usage": "32GB/128GB"
    },
    "iphone_data": {
      "battery": "87%",
      "connected_apps": [
        "app1",
        "app2"
      ]
    },
    "sentinel_baseline": {
      "baseline_files": [
        "file1",
        "file2"
      ],
      "drift_detected": false
    },
    "alama_backend": {
      "path": "/home/pc-1/sable-agent-run/sable-agent/workspace/alama_backend.py",
      "tokens": "unlimited",
      "response": {
        "response": "Hello, I am Alama AI and ready to talk!"
      }
    },
    "elama_backend": {
      "path": "/home/pc-1/sable-agent-run/sable-agent/workspace/elama_backend.py",
      "tokens": "unlimited",
      "response": {
        "response": "Hello, I am Elama AI and ready to talk!"
      }
    },
    "olama_backend": {
      "path": "/home/pc-1/sable-agent-run/sable-agent/workspace/olama_backend.py",
      "tokens": "unlimited",
      "response": {
        "response": "Hello, I am Olama AI and ready to talk!"
      }
    }
  },
  "timestamp": "2026-03-18T00:32:44.320365+00:00",
  "memory": {
    "runs": 1
  }
}