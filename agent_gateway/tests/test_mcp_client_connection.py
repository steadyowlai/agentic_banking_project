"""
Test MCP Client for Agent Gateway

Connects to the running mcp_server over SSE and reads policy resources.
"""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_read_policies():
    server_url = "http://127.0.0.1:8000/sse"
    print(f"Connecting to MCP Server at {server_url}...")

    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session handshake with MCP server
            await session.initialize()
            print("Connected to MCP Server!")

            # 1. List all resources exposed by MCP server
            resources_result = await session.list_resources()
            print("\n--- Available MCP Resources ---")
            for res in resources_result.resources:
                print(f"  • URI: {res.uri} | Name: {res.name}")

            # 2. Read retail policy content
            print("\n--- Fetching policy://retail ---")
            retail_content = await session.read_resource("policy://retail")
            print(retail_content.contents[0].text)

            # 3. Read corporate policy content
            print("\n--- Fetching policy://corporate ---")
            corp_content = await session.read_resource("policy://corporate")
            print(corp_content.contents[0].text)


if __name__ == "__main__":
    asyncio.run(test_read_policies())
