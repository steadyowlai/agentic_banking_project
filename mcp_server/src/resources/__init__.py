"""
MCP Resources Package

Contains all MCP resource implementations.
Resources provide passive, read-only context data.
"""

from .policy_resources import setup_policy_resources

__all__ = [
    'setup_policy_resources',
]
