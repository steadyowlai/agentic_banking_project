"""
Script to pre-calculate and save dev JWT tokens for mock users into client_side_data/dev_tokens.json
"""

import os
import sys
import json

# Add agent_gateway/src to python path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
GATEWAY_SRC = os.path.join(PROJECT_ROOT, "agent_gateway", "src")
sys.path.insert(0, GATEWAY_SRC)

from auth import create_access_token
from config import CLIENT_SIDE_DATA_DIR

#these mock users match the exact records seeded into data/database/business.db by scripts/init_db.py
MOCK_USERS = [
    {"user_id": "usr_alice", "username": "alice", "customer_type": "retail", "name": "Alice Johnson"},
    {"user_id": "usr_bob", "username": "bob", "customer_type": "retail", "name": "Bob Smith"},
    {"user_id": "usr_charlie", "username": "charlie", "customer_type": "corporate", "name": "Charlie Williams"},
    {"user_id": "usr_diana", "username": "diana", "customer_type": "corporate", "name": "Diana Martinez"},
]


def generate_tokens():
    os.makedirs(CLIENT_SIDE_DATA_DIR, exist_ok=True)
    tokens_file = os.path.join(CLIENT_SIDE_DATA_DIR, "dev_tokens.json")

    tokens_data = {}
    for user in MOCK_USERS:
        token = create_access_token(
            user_id=user["user_id"],
            username=user["username"],
            customer_type=user["customer_type"]
        )
        tokens_data[user["username"]] = {
            "user_id": user["user_id"],
            "name": user["name"],
            "customer_type": user["customer_type"],
            "jwt_token": token,
            "authorization_header": f"Bearer {token}"
        }

    with open(tokens_file, "w") as f:
        json.dump(tokens_data, f, indent=2)

    print(f"✅ Successfully generated pre-calculated JWT tokens for {len(tokens_data)} users!")
    print(f"📄 Saved to: {tokens_file}")


if __name__ == "__main__":
    generate_tokens()
