"""
Authentication & JWT Utilities Service
"""

import datetime
import sqlite3
import sys
import os
from typing import Optional, Dict, Any
import jwt

#path resolution to access config.py
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, DB_PATH


def create_access_token(user_id: str, username: str, customer_type: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Generate a signed JWT access token containing user identity claims.
    """
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "user_id": user_id,
        "username": username,
        "customer_type": customer_type,
        "exp": expire,
        "iat": datetime.datetime.utcnow()
    }
    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT access token. Returns payload dict or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def verify_user_credentials(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify user credentials against the SQLite database users table.
    Returns user record dict (without password) if valid, None otherwise.
    """
    if not username or not password:
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, username, password, first_name, last_name, customer_type FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()

        if row and row["password"] == password:
            user_data = dict(row)
            del user_data["password"]  # exclude password from return value
            return user_data
        
        return None
    except Exception:
        return None
