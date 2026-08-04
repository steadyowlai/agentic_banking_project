"""
THIS AGENT IS NOT ACTIVE IN THE CURRENT IMPLEMENTATION.
"""


"""
Policy Worker Agent for Agent Gateway (Hierarchical Multi-Agent Pattern)

has 2 nodes:
-fetches policy resources from mcp_server over SSE into state.
-uses LLM to synthesize answer from policy_doc state.
"""

import sys
import os
from typing import Optional, TypedDict, List, Annotated

from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

#path resolution to access config.py
WORKERS_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.dirname(WORKERS_DIR)
SRC_DIR = os.path.dirname(AGENTS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config import MCP_SERVER_URL, LLM_MODEL, LLM_TEMPERATURE


#state
class PolicyAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    customer_type: str
    policy_doc: Optional[str]


#node 1: fetch policy resource from mcp_server
async def fetch_policy_node(state: PolicyAgentState) -> dict:
    """
    Connects to mcp_server via SSE and loads policy text for the user's customer_type.
    """
    customer_type = state.get("customer_type", "retail")
    resource_uri = f"policy://{customer_type.lower()}"
    policy_doc = f"Policy documentation for {customer_type} is unavailable."
    
    try:
        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                policy_data = await session.read_resource(resource_uri)
                if policy_data and policy_data.contents:
                    policy_doc = policy_data.contents[0].text
    except Exception as e:
        print(f"Error reading policy resource {resource_uri}: {e}")
        
    return {"policy_doc": policy_doc}


#node 2: generate answer using LLM
async def generate_answer_node(state: PolicyAgentState) -> dict:
    """
    Synthesizes a concise answer using ChatOpenAI based on loaded policy_doc.
    """
    customer_type = state.get("customer_type", "retail")
    policy_doc = state.get("policy_doc", "")
    
    system_prompt = (
        f"You are the Bank Lending Policy Expert for {customer_type.upper()} customers.\n"
        f"Base your answers strictly on the official bank lending policy document provided below:\n\n"
        f"--- OFFICIAL BANK POLICY DOCUMENT ---\n"
        f"{policy_doc}\n"
        f"------------------------------------\n"
        f"Answer the user's question concisely based on the policy."
    )
    
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    response = await llm.ainvoke(messages)
    response.name = "policy_worker"
    
    return {"messages": [response]}


#add nodes
builder = StateGraph(PolicyAgentState)
builder.add_node("fetch_policy", fetch_policy_node)
builder.add_node("generate_answer", generate_answer_node)

#build graph
builder.add_edge(START, "fetch_policy")
builder.add_edge("fetch_policy", "generate_answer")
builder.add_edge("generate_answer", END)

policy_agent = builder.compile()
