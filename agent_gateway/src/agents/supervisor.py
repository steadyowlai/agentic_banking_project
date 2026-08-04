"""
Agent Gateway Supervisor
Uses LangGraph StateGraph with explicit AgentState, ToolNode, and conditional edges.
"""

import sys
import os
from typing import Optional, TypedDict, Annotated, Sequence

#path resolution
AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(AGENTS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from config import LLM_MODEL, LLM_TEMPERATURE
from agents.tools.policy_tools import fetch_bank_policy
from agents.tools.loan_tools import get_my_loans_tool, get_loan_details_tool
from agents.tools.user_tools import get_my_profile_tool
from agents.tools.calculator_tools import calculate


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: Optional[str]


#system instructions with few-shot tool-chaining guidance
system_message = (
    "You are a read-only banking assistant.\n"
    "You can ONLY look up user profiles, active loans, bank policies, and compute calculations.\n\n"

    "STRICT BOUNDARIES:\n"
    "- You CANNOT open accounts, create loans, process applications, or make transfers.\n"
    "- If asked to open accounts or apply for loans, immediately refuse in 1-2 sentences and direct the user to contact customer support. Do NOT ask intake questions.\n"
    "- You must strictly refuse to answer any questions outside banking, loan inquiries, user profiles, and bank lending policies (e.g. general knowledge, life advice, coding, or non-banking topics). Politely state that you can only assist with banking and loan-related inquiries.\n\n"

    "TOOL CHAINING RECIPE EXAMPLES:\n"
    "1. Borrowing Capacity / Limits:\n"
    "   - Call `get_my_loans_tool` to get total current loan balance.\n"
    "   - Call `fetch_bank_policy` with the customer's tier to get maximum policy limit.\n"
    "   - Call `calculate(a=limit, b=current_balance, operation='subtract')` to find remaining capacity.\n"
    "2. Full Account Summary:\n"
    "   - Call `get_my_profile_tool` AND `get_my_loans_tool` together.\n"
    "3. Math Rule:\n"
    "   - NEVER calculate numbers in your text. ALWAYS use the `calculate` tool.\n\n"

    "Keep all final responses concise, professional, and accurate."
)


#initialize tools and llm with bound tools
tools = [fetch_bank_policy, get_my_loans_tool, get_loan_details_tool, get_my_profile_tool, calculate]
llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
model_with_tools = llm.bind_tools(tools)

#state graph nodes and condition
async def supervisor_node(state: AgentState, config: RunnableConfig):
    """Invokes the LLM with conversation history and bound tools, prepending system prompt if needed."""
    messages = list(state["messages"])
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=system_message)] + messages
        
    print(f"[DEBUG][SUPERVISOR_NODE] Invoking LLM (Context depth: {len(messages)} messages)")
    response = await model_with_tools.ainvoke(messages, config=config)
    
    if getattr(response, "tool_calls", None):
        for tc in response.tool_calls:
            print(f"[DEBUG][SUPERVISOR_NODE] LLM requested tool call: name='{tc['name']}', args={tc.get('args', {})}")
    else:
        preview = response.content[:100].replace('\n', ' ')
        print(f"[DEBUG][SUPERVISOR_NODE] LLM generated final text response: '{preview}...'")

    return {"messages": [response]}

def router(state: AgentState) -> str:
    """Routes to 'tools' if tool calls are present, otherwise ends turn."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        print(f"[DEBUG][ROUTER] Found {len(last_message.tool_calls)} tool call(s) -> Routing to 'tools'")
        return "tools"
    print("[DEBUG][ROUTER] No tool calls found -> Routing to END")
    return END

builder = StateGraph(AgentState)

#nodes
builder.add_node("supervisor", supervisor_node)
builder.add_node("tools", ToolNode(tools))

#edges
builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", router, ["tools", END])
builder.add_edge("tools", "supervisor")

#in memory checkpointer for multi turn sessions
checkpointer = MemorySaver()
supervisor_graph = builder.compile(checkpointer=checkpointer)


#helper function to run supervisor agent
async def run_supervisor_agent(user_query: str, user_id: str, thread_id: Optional[str] = None) -> str:
    """
    Runs the supervisor graph with checkpointed conversational memory.
    
    Args:
        user_query: The customer's message or prompt.
        user_id: The unique customer identifier (e.g. 'usr_alice').
        thread_id: Optional conversation thread ID for session isolation. Defaults to 'thread_{user_id}'.
    """
    thread_id = thread_id or f"thread_{user_id}"

    print(f"\n[DEBUG][SUPERVISOR] Starting graph run: user_id='{user_id}', thread_id='{thread_id}'")
    print(f"[DEBUG][SUPERVISOR] User Query: '{user_query}'")

    initial_state: AgentState = {
        "messages": [
            HumanMessage(content=user_query)
        ],
        "user_id": user_id
    }
    
    #pass user_id and thread_id via config so tools and checkpointer can extract it
    config = {
        "configurable": {
            "user_id": user_id,
            "thread_id": thread_id
        }
    }
    
    result = await supervisor_graph.ainvoke(initial_state, config=config)
    final_output = result["messages"][-1].content
    print(f"[DEBUG][SUPERVISOR] Graph execution completed successfully.\n")
    return final_output
