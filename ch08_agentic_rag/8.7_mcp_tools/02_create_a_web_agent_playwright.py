import asyncio
from agents.mcp import MCPServerStdio
from agents import Agent, Runner


async def create_cookie_research_agent():
    # MCP server configurations
    files_params = {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
    }
    browser_params = {"command": "npx", "args": ["@playwright/mcp@latest"]}

    # Agent instructions
    instructions = "You can browse websites and save information to files."

    async with MCPServerStdio(
        params=files_params, client_session_timeout_seconds=60
    ) as files:
        async with MCPServerStdio(
            params=browser_params, client_session_timeout_seconds=60
        ) as browser:

            # Create agent
            agent = Agent(
                name="research_agent",
                instructions=instructions,
                model="gpt-4o-mini",
                mcp_servers=[files, browser],
            )

            # Run task
            result = await Runner.run(
                agent, "Find a chocolate chip cookie recipe and save it to recipe.md"
            )

            print(result.final_output)


if __name__ == "__main__":
    asyncio.run(create_cookie_research_agent())
