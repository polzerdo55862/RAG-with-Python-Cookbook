# Book Example 2: Multiple MCP Servers
import asyncio
from agents.mcp import MCPServerStdio


async def connect_multiple_servers():
    # Filesystem server
    files_params = {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
    }
    # Web browsing server
    browser_params = {"command": "npx", "args": ["@playwright/mcp@latest"]}

    async with MCPServerStdio(
        params=files_params, client_session_timeout_seconds=60
    ) as files:
        async with MCPServerStdio(
            params=browser_params, client_session_timeout_seconds=60
        ) as browser:

            file_tools = await files.list_tools()
            browser_tools = await browser.list_tools()

            print(f"File tools: {len(file_tools)}")
            print(f"Browser tools: {len(browser_tools)}")


if __name__ == "__main__":
    asyncio.run(connect_multiple_servers())
