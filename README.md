# Live Exam MCP Server

A minimal public MCP Streamable HTTP endpoint at `/mcp`. It exposes exactly one tool: `solve_challenge`.

## Deploy on Render

1. Create a GitHub repository and upload `main.py`, `requirements.txt`, and `render.yaml`.
2. In Render, choose **New → Blueprint** and select that repository (or create a Python web service).
3. Wait for deployment to finish. Render provides an HTTPS URL such as `https://your-service.onrender.com`.
4. Submit the MCP endpoint URL, including `/mcp`: `https://your-service.onrender.com/mcp`.
5. Open the base URL in a browser; `{"status":"ok","mcp_endpoint":"/mcp"}` confirms the service is awake.

## Protocol behavior

- Handles `initialize`, `notifications/initialized`, `tools/list`, `tools/call`, and `ping`.
- `solve_challenge` has no required input properties.
- Each call reads `X-Exam-Challenge` from that call's HTTP headers and returns the first 16 lowercase hex characters of SHA-256 of `challenge:23f3003865@ds.study.iitm.ac.in`.
- The challenge is never read from the JSON body. Signature verification is intentionally omitted because it is optional for grading.

## Local test

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Send MCP JSON-RPC requests to `http://127.0.0.1:8000/mcp`. For a live grading URL, use the deployed HTTPS address.
