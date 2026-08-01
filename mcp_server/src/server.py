"""
Banking MCP Server

Main entry point for the Model Context Protocol server.
Exposes banking resources (policies) and tools (loans, user data) to LLM clients.
"""

import sys
import os

#add the src directory to Python path to allow absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP

from resources import setup_policy_resources
from tools.loan_tools import setup_loan_tools
from tools.user_tools import setup_user_tools

#initialize fastmcp server
mcp = FastMCP("Banking MCP Server")

#register resources and tools
setup_policy_resources(mcp)
setup_loan_tools(mcp)
setup_user_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport='sse')
