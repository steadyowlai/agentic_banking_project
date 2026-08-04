"""
Agent Gateway Configuration Settings
"""

import os
from dotenv import load_dotenv

#load env variables from .env file at project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # agent_gateway/src/
GATEWAY_ROOT = os.path.dirname(BASE_DIR)                   # agent_gateway/
PROJECT_ROOT = os.path.dirname(GATEWAY_ROOT)               # root project directory

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

#jwt config
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-banking-key-change-in-prod-12345")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  #1 year 

#database path for user authentication lookup
DB_PATH = os.getenv("DB_PATH", os.path.join(PROJECT_ROOT, "data", "database", "business.db"))

#mcp server url
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8001/sse")

#client side data dir
CLIENT_SIDE_DATA_DIR = os.path.join(PROJECT_ROOT, "client_side_data")

#llm settings
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5-nano")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
