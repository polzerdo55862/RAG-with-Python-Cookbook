import asyncio
from agents.mcp import MCPServerStdio


async def connect_to_playwright():
    # Define connection parameters
    # "npx" runs Node.js packages, "@playwright/mcp@latest" specifies the package
    params = {"command": "npx", "args": ["@playwright/mcp@latest"]}

    # Create server connection with extended timeout
    async with MCPServerStdio(
        params=params, client_session_timeout_seconds=30  # Increased from default 5s
    ) as server:
        # List available tools from the server
        tools = await server.list_tools()
        print("Available tools:", tools)


# Run the async function
if __name__ == "__main__":
    asyncio.run(connect_to_playwright())
