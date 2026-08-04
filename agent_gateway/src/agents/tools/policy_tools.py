"""
Tools for fetching banking policies.
"""
import sys
import os
from langchain_core.tools import tool
from mcp import ClientSession
from mcp.client.sse import sse_client

#path resolution to access config.py
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.dirname(TOOLS_DIR)
SRC_DIR = os.path.dirname(AGENTS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config import MCP_SERVER_URL


@tool
async def fetch_bank_policy(customer_type: str) -> str:
    """
    Fetches the official bank lending policy for a given customer type.
    Use this tool whenever the user asks about rules, limits, eligibility, maturity, or policies.
    
    Args:
        customer_type: The type of customer ('retail', 'corporate').
    """
    resource_uri = f"policy://{customer_type.lower()}"
    policy_doc = f"Policy documentation for {customer_type} is unavailable."
    
    print(f"[DEBUG][TOOL: fetch_bank_policy] Querying MCP Policy resource: '{resource_uri}'")
    try:
        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                policy_data = await session.read_resource(resource_uri)
                if policy_data and policy_data.contents:
                    policy_doc = policy_data.contents[0].text
                    print(f"[DEBUG][TOOL: fetch_bank_policy] Retrieved {len(policy_doc)} chars of policy text")
    except Exception as e:
        print(f"[DEBUG][TOOL: fetch_bank_policy] Error reading resource '{resource_uri}': {e}")
        return f"Error reading policy resource {resource_uri}: {e}"
        
    return policy_doc
