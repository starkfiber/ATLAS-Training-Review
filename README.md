# ATLAS Training Review

A free example from Stark Fiber Enterprise, Malaysia. Compare three fictional training-document revisions and trace their impact on equipment models, lesson material and questions. The public [Review Studio](https://starkfiber.my/atlasai/petronas#training-review) uses these same examples.

## Connect Codex

Extract the files into a directory you control. Install Python 3.10+ and run the command with the absolute path to the extracted script.

```sh
codex mcp add atlas-training-review -- python3 /absolute/path/atlas_review.py
codex mcp list
```

Start a new Codex session and ask: “List the ATLAS training revisions, then review the pump seal case. Show the source change, the affected lesson material, and what the instructor needs to request before sign-off.”

The server reads the bundled casebook and answers locally over stdio. Tool arguments accept a case ID only. The MCP server has no network, account or write tools. Your AI client controls how tool responses are processed. The records are fictional learning material. Use approved references and an instructor's review for real work.

## Validate without a client

```sh
python3 test_review.py
```

This sends a real initialize, initialized notification, tools/list and tools/call sequence over stdin/stdout to a fresh process. It checks the three case outcomes and verifies that unknown cases and unexpected arguments are rejected.
