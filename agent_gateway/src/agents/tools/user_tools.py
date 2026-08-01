"""
Tools for interacting with user profile records via the MCP server.
"""
import sys
import os
import json
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from mcp import ClientSession
from mcp.client.sse import sse_client

#path resolution
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.dirname(TOOLS_DIR)
SRC_DIR = os.path.dirname(AGENTS_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config import MCP_SERVER_URL

#for this demo, we load dev tokens to easily look up the user's token by ID.
#assume JWT is already handled by the frontend application.
CLIENT_DATA = os.path.join(PROJECT_ROOT, "client_side_data", "dev_tokens.json")

def _get_dev_token(user_id: str) -> str:
    """Helper to lookup a mock JWT token by user_id for demonstration purposes."""
    try:
        with open(CLIENT_DATA, "r") as f:
            tokens = json.load(f)
        for user_data in tokens.values():
            if user_data["user_id"] == user_id:
                return user_data["authorization_header"]
    except Exception:
        pass
    return ""


@tool
async def get_my_profile_tool(config: RunnableConfig) -> str:
    """
    Fetches profile information for the currently authenticated user (name, username, customer tier, etc.).
    Use this tool whenever the user asks about their account profile, account details, or identity.
    """
    #get user id from runnable config
    user_id = config.get("configurable", {}).get("user_id", "usr_alice")

    #get auth header from runnable config
    auth_header = _get_dev_token(user_id)
    headers = {"Authorization": auth_header} if auth_header else {}

    try:
        #pass headers to sse_client so the MCP Server can decode the JWT
        async with sse_client(MCP_SERVER_URL, headers=headers) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                #call MCP tool by name
                result = await session.call_tool("get_my_profile", {})

                #format response
                if result and result.content:
                    return result.content[0].text
                return "No data returned from profile server."
    except Exception as e:
        return f"Error connecting to profile server: {e}"
