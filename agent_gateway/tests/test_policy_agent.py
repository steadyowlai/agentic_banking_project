"""
Integration Test for Policy Worker Node
"""

import sys
import os
import pytest
from langchain_core.messages import HumanMessage

# Path resolution
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
GATEWAY_DIR = os.path.dirname(TESTS_DIR)
GATEWAY_SRC = os.path.join(GATEWAY_DIR, "src")
if GATEWAY_SRC not in sys.path:
    sys.path.insert(0, GATEWAY_SRC)

from agents.workers.policy_agent import policy_agent_graph


@pytest.mark.anyio
async def test_fetch_policy_node():
    """Verify policy_agent_graph fetches policy_doc into state when mcp_server is running."""
    initial_state = {
        "messages": [HumanMessage(content="What is the pre-approval limit?")],
        "customer_type": "retail",
        "policy_doc": None
    }
    
    result = await policy_agent_graph.ainvoke(initial_state)
    assert result["policy_doc"] is not None
    assert len(result["policy_doc"]) > 0
