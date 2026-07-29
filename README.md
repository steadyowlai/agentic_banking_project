# Bank Loan Agentic Platform

Bank loan management platform combining Model Context Protocol (MCP), LangGraph, and FastAPI for automated loan processing and policy evaluation.

## System Architecture

- `data/`: SQLite database (`business.db`) for user/loan records and plain-text policy documents (`retail_policy.txt`, `corporate_policy.txt`).
- `scripts/`: Seeding and setup scripts (`init_db.py`).
- `mcp_server/`: FastMCP server exposing database queries and policy documents via MCP tools and resources.
- `agent_gateway/`: FastAPI service hosting the LangGraph agent and client authentication logic.

## Setup

```bash
source .venv/bin/activate
python scripts/init_db.py
pytest mcp_server
```

## Running

1. Start MCP Server:
   ```bash
   python mcp_server/src/server.py
   ```

2. Run MCP Client test:
   ```bash
   python agent_gateway/src/test_mcp_client.py
   ```

## Configuration

Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
