"""
Policy Worker Node for Agent Gateway

Fetches policy resources from mcp_server over SSE and injects policy_doc into graph state.
"""

import sys
import os
from typing import Optional, TypedDict, List, Annotated

from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

#path resolution to access config.py
WORKERS_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.dirname(WORKERS_DIR)
SRC_DIR = os.path.dirname(AGENTS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config import MCP_SERVER_URL


#state
class PolicyAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    customer_type: str
    policy_doc: Optional[str]

#fetches policy from mcp server
async def fetch_policy_node(state: PolicyAgentState) -> dict:
    """
    Connects to mcp server via SSE and loads policy text for the user's customer_type.
    """
    customer_type = state.get("customer_type", "retail")
    resource_uri = f"policy://{customer_type.lower()}"
    
    try:
        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                policy_data = await session.read_resource(resource_uri)
                if policy_data and policy_data.contents:
                    return {"policy_doc": policy_data.contents[0].text}
    except Exception as e:
        print(f"Error reading policy resource {resource_uri}: {e}")
    
    return {"policy_doc": f"Policy documentation for {customer_type} is unavailable."}

#construct and compile policy graph
builder = StateGraph(PolicyAgentState)
builder.add_node("fetch_policy", fetch_policy_node)
builder.add_edge(START, "fetch_policy")
builder.add_edge("fetch_policy", END)

policy_agent = builder.compile()
