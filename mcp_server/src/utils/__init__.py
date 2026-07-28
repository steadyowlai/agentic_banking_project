"""
Utility modules for MCP Server

Contains shared helper functions and utilities:
- database: Database connection and query helpers
- file_utils: File reading utilities (policies, etc.)
"""

from .database import (
    get_db_connection,
    get_user_by_username,
    get_user_by_id,
    get_loan_by_id,
    get_loans_by_user_id,
)

from .file_utils import (
    get_policy_content,
)

__all__ = [
    'get_db_connection',
    'get_user_by_username',
    'get_user_by_id',
    'get_loan_by_id',
    'get_loans_by_user_id',
    'get_policy_content',
]
