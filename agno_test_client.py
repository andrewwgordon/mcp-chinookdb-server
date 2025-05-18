import asyncio
import os
from textwrap import dedent

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters
from agno.models.openai import OpenAIChat

# --- Main Agent Runner ---
async def run_agent(message: str) -> None:
    """
    Run the Chinook database agent with the given message.
    This function starts the MCP server (chinook_mcp_server.py) as a subprocess,
    connects to it using MCPTools, and creates an Agno agent with OpenAIChat as the LLM.
    The agent is configured to use the MCP server as a tool for answering queries about the Chinook database.
    Args:
        message (str): The user query to send to the agent.
    """

    # Initialize the MCP server parameters for stdio transport.
    # Uses 'uv' to run the server for fast startup and reloads.
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "chinook_mcp_server.py"]
    )

    # Create a client session to connect to the MCP server as a tool.
    async with MCPTools(server_params=server_params) as mcp_tools:
        # Set up the Agno agent with the OpenAIChat model and MCP tools.
        agent = Agent(
            model=OpenAIChat(id="gpt-4.1-mini"),
            tools=[mcp_tools],
            instructions=dedent("""
                You are an assistant for querying the Chinook Online Music Store database. Help users explore the database and execute queries.
            """),
            markdown=True,           # Format output as Markdown
            show_tool_calls=True,    # Show tool calls in the output
        )

        # Run the agent and print the response to the user, streaming output as it arrives.
        await agent.aprint_response(message, stream=True)


# --- Interactive CLI Loop ---
if __name__ == "__main__":
    # Simple REPL loop for user queries
    while True:
        query = input("> ")
        if query == "q" or query == "quit" or query == "exit":
            os._exit(0)  # Exit the process immediately
        # Run the agent for the user's query (asyncio.run ensures event loop is managed)
        asyncio.run(
            run_agent(query)
        )