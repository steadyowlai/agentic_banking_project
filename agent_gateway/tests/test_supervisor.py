"""
Integration Test for Supervisor React Agent
"""

import sys
import os
import pytest
from langchain_core.messages import HumanMessage, SystemMessage

#path resolution
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
GATEWAY_DIR = os.path.dirname(TESTS_DIR)
GATEWAY_SRC = os.path.join(GATEWAY_DIR, "src")
if GATEWAY_SRC not in sys.path:
    sys.path.insert(0, GATEWAY_SRC)

from agents.supervisor import supervisor_graph


@pytest.mark.anyio
async def test_supervisor_react_agent():
    """Verify Supervisor correctly calls the fetch_bank_policy tool."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("Skipping OpenAI test because OPENAI_API_KEY is not set.")

    initial_state = {
        "messages": [
            SystemMessage(content="[System context: The user is a retail customer.]"),
            HumanMessage(content="What is the retail pre-approval limit?")
        ]
    }
    
    result = await supervisor_graph.ainvoke(initial_state)
    
    # Check that it generated an AIMessage
    assert len(result["messages"]) > 1
    final_message = result["messages"][-1]
    
    # We can check that a tool call was made in the history
    tool_calls_made = False
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
            assert msg.tool_calls[0]["name"] == "fetch_bank_policy"
            tool_calls_made = True
            break
            
    assert tool_calls_made, "The agent failed to call the fetch_bank_policy tool."
    assert "retail" in final_message.content.lower() or "50,000" in final_message.content or "50k" in final_message.content.lower()
