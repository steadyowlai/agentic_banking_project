"""
MCP Server Authentication Utilities

Provides standalone Zero Trust JWT verification for the MCP server.
Reads JWT_SECRET from the root .env file.
"""

import os
from typing import Optional, Dict, Any
import jwt
from dotenv import load_dotenv

# path resolution to load .env from project root
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(UTILS_DIR)
MCP_SERVER_DIR = os.path.dirname(SRC_DIR)
PROJECT_ROOT = os.path.dirname(MCP_SERVER_DIR)

# load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# jwt configuration
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-banking-key-change-in-prod-12345")
JWT_ALGORITHM = "HS256"

def verify_and_decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT access token. 
    Returns payload dict containing user_id and customer_type, or None if invalid.
    """
    if not token:
        return None
        
    # strip 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        print(f"JWT Verification Failed: {e}")
        return None
