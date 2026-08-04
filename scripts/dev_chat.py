import os
import json
import httpx

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_FILE = os.path.join(PROJECT_ROOT, "client_side_data", "dev_tokens.json")
GATEWAY_URL = "http://localhost:8000"

def load_users() -> dict:
    if not os.path.exists(TOKENS_FILE):
        print(f"Error: {TOKENS_FILE} not found. Run generate_dev_tokens.py first.")
        exit(1)
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)

def pick_user(users: dict) -> dict:
    print("\n--- Select a User ---")
    user_list = list(users.values())
    user_list.append({"name": "Guest", "customer_type": "unauthenticated", "jwt_token": ""})
    for i, user in enumerate(user_list, 1):
        print(f"{i}. {user['name']} ({user['customer_type']})")
    print("q. Quit\n")

    while True:
        choice = input("Enter choice: ").strip().lower()
        if choice in ["q", "quit", "exit"]:
            exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(user_list):
            return user_list[int(choice) - 1]
        print("Invalid choice, try again.")


def send_message(token: str, message: str) -> str:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = httpx.post(
            f"{GATEWAY_URL}/chat",
            json={"message": message},
            headers=headers,
            timeout=60.0
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"Error ({response.status_code}): {response.text}"
    except httpx.ConnectError:
        return "Error: Could not connect to FastAPI server. Is it running?"


def chat(user: dict):
    print(f"\nLogged in as {user['name']} ({user['customer_type']})")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            message = input(f"{user['name']} > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not message:
            continue
        if message.lower() in ["exit", "quit", "q"]:
            break

        reply = send_message(user["jwt_token"], message)
        print(f"\nAgent:\n{reply}\n")


def main():
    users = load_users()
    user = pick_user(users)
    chat(user)

if __name__ == "__main__":
    main()
