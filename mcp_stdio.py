"""Bounded, newline-delimited MCP transport for the standalone ATLAS Python kits."""
import json
import sys

PROTOCOL = "2025-11-25"
MAX_REQUEST_BYTES = 65536


def rpc_error(identifier, code, message):
    return {"jsonrpc": "2.0", "id": identifier, "error": {"code": code, "message": message}}


class Session:
    def __init__(self, server_name, version, tool_list, call_tool):
        self.server_info = {"name": server_name, "version": version}
        self.tools = tool_list
        self.tool_names = {tool["name"] for tool in tool_list}
        self.call_tool = call_tool
        self.state = "new"

    def handle(self, packet):
        if not isinstance(packet, dict) or packet.get("jsonrpc") != "2.0" or not isinstance(packet.get("method"), str):
            return rpc_error(None, -32600, "Invalid JSON-RPC request.")
        method = packet["method"]
        params = packet.get("params", {})
        if "id" not in packet:
            if method == "notifications/initialized" and self.state == "negotiated":
                self.state = "ready"
            return None
        identifier = packet["id"]
        if type(identifier) not in (int, str):
            return rpc_error(None, -32600, "Use an integer or string request ID.")
        if not isinstance(params, dict):
            return rpc_error(identifier, -32602, "Supply an object for params.")
        if method == "initialize" and self.state == "new":
            if not isinstance(params.get("protocolVersion"), str):
                return rpc_error(identifier, -32602, "Supply protocolVersion.")
            self.state = "negotiated"
            value = {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}}, "serverInfo": self.server_info}
        elif method == "ping":
            value = {}
        elif self.state != "ready":
            return rpc_error(identifier, -32600, "Complete initialization before requesting tools.")
        elif method == "tools/list":
            value = {"tools": self.tools}
        elif method == "tools/call":
            name = params.get("name")
            if not isinstance(name, str) or name not in self.tool_names:
                return rpc_error(identifier, -32602, "Unknown tool.")
            try:
                result = self.call_tool(name, params.get("arguments", {}))
            except ValueError as error:
                value = {"content": [{"type": "text", "text": str(error)}], "isError": True}
            else:
                value = {
                    "content": [{"type": "text", "text": json.dumps(result, allow_nan=False)}],
                    "structuredContent": result,
                    "isError": False,
                }
        else:
            return rpc_error(identifier, -32601, "Unknown method.")
        return {"jsonrpc": "2.0", "id": identifier, "result": value}


def serve(server_name, version, tool_list, call_tool):
    session = Session(server_name, version, tool_list, call_tool)
    source = sys.stdin.buffer
    while True:
        line = source.readline(MAX_REQUEST_BYTES + 1)
        if not line:
            return
        if len(line) > MAX_REQUEST_BYTES:
            while line and not line.endswith(b"\n"):
                line = source.readline(MAX_REQUEST_BYTES + 1)
            reply = rpc_error(None, -32600, "Request exceeds 64 KiB.")
        else:
            try:
                reply = session.handle(json.loads(line.decode("utf-8")))
            except (UnicodeError, ValueError, RecursionError):
                reply = rpc_error(None, -32700, "Invalid UTF-8 JSON message.")
        if reply is not None:
            print(json.dumps(reply, allow_nan=False), flush=True)
