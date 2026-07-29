"""
Database utilities for MCP Server

Handles all database connections and queries with Docker-ready path resolution.
Uses environment variables for production/Docker, falls back to local paths for development.
"""

import sqlite3
import os
from typing import Optional, Dict, List, Any

# Path resolution for Docker and local development
# This file: mcp_server/src/utils/database.py
# Target:    data/database/ (at project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # mcp_server/src/utils/
SRC_DIR = os.path.dirname(BASE_DIR)                    # mcp_server/src/
MCP_SERVER_ROOT = os.path.dirname(SRC_DIR)             # mcp_server/
PROJECT_ROOT = os.path.dirname(MCP_SERVER_ROOT)        # root project directory

# Use environment variables for Docker, fallback to local paths for development
DB_PATH = os.getenv('DB_PATH', os.path.join(PROJECT_ROOT, 'data', 'database', 'business.db'))


def get_db_connection() -> sqlite3.Connection:
    """
    Get a connection to the business database.
    
    Returns:
        sqlite3.Connection: Database connection object
    
    Raises:
        sqlite3.Error: If database connection fails
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  #enable column access by name
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Failed to connect to database at {DB_PATH}: {str(e)}")


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user information by username (for authentication).
    
    Args:
        username: The username to look up
        
    Returns:
        Dict with user_id, username, password, first_name, last_name, customer_type or None if not found
    
    Note:
        Username lookup is case-sensitive for security.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, password, first_name, last_name, customer_type FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user information by user ID.
    
    Args:
        user_id: The user ID to look up (e.g., 'usr_alice')
        
    Returns:
        Dict with user_id, username, first_name, last_name, customer_type or None if not found
        (password excluded for security)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, first_name, last_name, customer_type FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_loan_by_id(loan_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve loan details by loan ID.
    
    Args:
        loan_id: The loan ID to look up
        
    Returns:
        Dict with loan details or None if not found
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT loan_id, user_id, customer_type, balance, interest_rate, 
                      maturity_date, status 
               FROM loans WHERE loan_id = ?""",
            (loan_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_loans_by_user_id(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all loans for a specific user.
    
    Args:
        user_id: The user ID to look up loans for
        
    Returns:
        List of loan dictionaries, empty list if no loans found
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT loan_id, user_id, customer_type, balance, interest_rate, 
                      maturity_date, status 
               FROM loans WHERE user_id = ?""",
            (user_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
