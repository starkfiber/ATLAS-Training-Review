"""Read the bundled fictional training revision cases from a local MCP client."""
import json
from pathlib import Path

from mcp_stdio import serve

CASEBOOK = Path(__file__).with_name("review-cases.json")
CASES = {case["id"]: case for case in json.loads(CASEBOOK.read_text(encoding="utf-8"))["cases"]}

TOOLS = [
    {
        "name": "list_training_revisions",
        "description": "List the bundled fictional equipment-training revisions.",
        "inputSchema": {"type": "object", "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "review_training_revision",
        "description": "Return the source comparison, affected training items and evidence gaps for one example. This is a draft for a human instructor.",
        "inputSchema": {
            "type": "object",
            "properties": {"case_id": {"type": "string", "enum": list(CASES)}},
            "required": ["case_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
]


def call_tool(name, arguments):
    if not isinstance(arguments, dict):
        raise ValueError("Supply an object of tool arguments.")
    if name == "list_training_revisions":
        if arguments:
            raise ValueError("This tool takes no arguments.")
        return {"fictional": True, "cases": [
            {key: case[key] for key in ("id", "title", "record")}
            for case in CASES.values()
        ]}
    if name != "review_training_revision" or set(arguments) != {"case_id"}:
        raise ValueError("Supply only case_id for a review.")
    case_id = arguments["case_id"]
    if not isinstance(case_id, str) or case_id not in CASES:
        raise ValueError("Choose a case ID returned by list_training_revisions.")
    case = CASES[case_id]
    statuses = {item["status"] for item in case["items"]}
    decision = "Ready for instructor review"
    if "missing" in statuses:
        decision = "Hold for evidence"
    elif "outdated" in statuses:
        decision = "Changes required"
    return {
        "schema": "atlas.training-review-draft.v1",
        "fictional": True,
        "state": "draft",
        "caseId": case_id,
        "record": case["record"],
        "before": case["before"],
        "after": case["after"],
        "decision": decision,
        "items": [{**item, "inspected": False} for item in case["items"]],
    }


if __name__ == "__main__":
    serve("atlas-training-review", "1.0.0", TOOLS, call_tool)
