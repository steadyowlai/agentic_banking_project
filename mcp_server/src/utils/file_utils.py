"""
File utilities for MCP Server

Handles reading policy documents and other file operations.
"""

import os
from typing import Optional

# Path resolution - same pattern as database.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # mcp_server/src/utils/
SRC_DIR = os.path.dirname(BASE_DIR)                    # mcp_server/src/
MCP_SERVER_ROOT = os.path.dirname(SRC_DIR)             # mcp_server/

# Use environment variables for Docker, fallback to local paths for development
POLICY_DIR = os.getenv('POLICY_DIR', os.path.join(MCP_SERVER_ROOT, 'data', 'policies'))


def get_policy_content(customer_type: str) -> Optional[str]:
    """
    Read and return policy document content.
    
    Args:
        customer_type: Either 'retail' or 'corporate'
        
    Returns:
        Policy content as string or None if file not found
    """
    policy_file = f"{customer_type.lower()}_policy.txt"
    policy_path = os.path.join(POLICY_DIR, policy_file)
    
    try:
        with open(policy_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        raise Exception(f"Error reading policy file {policy_path}: {str(e)}")
