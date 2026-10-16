import hashlib
import json
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI(title="Exam MCP Server")

EMAIL = "23f3003865@ds.study.iitm.ac.in"
PROTOCOL_VERSION = "2025-03-26"

TOOLS = [{
    "name": "solve_challenge",
    "description": "Returns the required SHA-256 response for the challenge in the HTTP headers.",
    "inputSchema": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    }
}]

@app.get("/")
async def health():
    return {"status": "ok", "mcp_endpoint": "/mcp"}

@app.post("/mcp")
async def mcp(request: Request):
    # Read the JSON-RPC envelope, but never read the challenge from its body.
    try:
        body: dict[str, Any] = await request.json()
    except Exception:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": None,
             "error": {"code": -32700, "message": "Parse error"}},
            status_code=400
        )

    method = body.get("method")
    request_id = body.get("id")

    # MCP notifications have no JSON response body.
    if method == "notifications/initialized" or (isinstance(method, str) and method.startswith("notifications/")):
        return Response(status_code=202)

    if method == "initialize":
        params = body.get("params") or {}
        version = params.get("protocolVersion", PROTOCOL_VERSION)
        result = {
            "protocolVersion": version,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "exam-challenge-mcp", "version": "1.0.0"}
        }
        return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": result})

    if method == "ping":
        return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": {}})

    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0", "id": request_id,
            "result": {"tools": TOOLS}
        })

    if method == "tools/call":
        params = body.get("params") or {}
        if params.get("name") != "solve_challenge":
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32602, "message": "Unknown tool"}
            })

        # The challenge MUST come from the current HTTP request headers.
        challenge = request.headers.get("x-exam-challenge")
        if challenge is None:
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32602, "message": "Missing X-Exam-Challenge header"}
            })

        normalized_email = EMAIL.strip().lower()
        answer = hashlib.sha256(
            f"{challenge}:{normalized_email}".encode("utf-8")
        ).hexdigest()[:16]

        return JSONResponse({
            "jsonrpc": "2.0", "id": request_id,
            "result": {
                "content": [{"type": "text", "text": answer}],
                "isError": False
            }
        })

    return JSONResponse({
        "jsonrpc": "2.0", "id": request_id,
        "error": {"code": -32601, "message": "Method not found"}
    })
