import json
from pathlib import Path
import subprocess
import sys

script = Path(__file__).with_name("atlas_review.py")
requests = [
    {"id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
    {"method": "notifications/initialized"},
    {"id": 2, "method": "tools/list"},
]
for index, case_id in enumerate(("seal", "tray", "batch", "unknown", ["seal"]), 3):
    requests.append({"id": index, "method": "tools/call", "params": {
        "name": "review_training_revision", "arguments": {"case_id": case_id}
    }})
requests.append({"id": 8, "method": "tools/call", "params": {
    "name": "list_training_revisions", "arguments": {"path": "/tmp/sample.json"}
}})
requests.append({"id": 9, "method": "tools/call", "params": {"name": "list_training_revisions"}})
result = subprocess.run(
    [sys.executable, str(script)],
    input="".join(json.dumps({"jsonrpc": "2.0", **message}) + "\n" for message in requests),
    text=True, capture_output=True, timeout=10, check=True,
)
answers = {entry["id"]: entry["result"] for entry in map(json.loads, result.stdout.splitlines())}
assert len(answers[2]["tools"]) == 2
assert answers[9]["structuredContent"]["fictional"] is True
assert len(answers[9]["structuredContent"]["cases"]) == 3
for index, decision in enumerate(("Hold for evidence", "Changes required", "Hold for evidence"), 3):
    draft = answers[index]["structuredContent"]
    assert draft["decision"] == decision and draft["state"] == "draft"
    assert len(draft["items"]) == 3 and all(not item["inspected"] for item in draft["items"])
assert all(answers[index]["isError"] for index in (6, 7, 8))
print("MCP handshake, tools/list, all three review paths and invalid arguments passed.")
