"""
User Profile Tools

Exposes user profile access to the LLM. Enforces Zero Trust Architecture by 
verifying JWT tokens before allowing database queries.
"""

import sys
import os
from fastmcp import Context

#path resolution to access utils
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(TOOLS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from utils.database import get_user_by_id
from utils.auth_utils import verify_and_decode_token


def _extract_auth_header(ctx: Context) -> str:
    """Extract Authorization header from the injected MCP Context."""
    try:
        if ctx.request_context and ctx.request_context.request:
            req = ctx.request_context.request
            return req.headers.get("authorization") or req.headers.get("Authorization") or ""
    except Exception:
        pass
    return ""

def setup_user_tools(mcp):
    """Register user tools with the FastMCP server instance."""

    @mcp.tool()
    async def get_my_profile(ctx: Context) -> str:
        """
        Fetches profile information for the currently authenticated user.
        Requires a valid Bearer token in the authorization header.
        """
        auth_header = _extract_auth_header(ctx)

        #zero trust: verify token signature
        payload = verify_and_decode_token(auth_header)

        if not payload:
            return "AUTH_ERROR: Invalid, expired, or missing Bearer token. Please authenticate."

        user_id = payload.get("user_id")

        #fetch user profile from database
        user = get_user_by_id(user_id)

        if not user:
            return "User profile not found."

        #format the response nicely for the LLM
        response = f"User Profile for {user['username']}:\n"
        response += f"- User ID: {user['user_id']}\n"
        response += f"- Name: {user['first_name']} {user['last_name']}\n"
        response += f"- Customer Type: {user['customer_type'].title()}\n"

        return response
