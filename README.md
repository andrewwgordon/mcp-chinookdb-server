# mcp-chinookdb-server

Example MCP Server to provide LLM MCP access to the example sqlite3 Chinook database

## Overview

This project provides an MCP (Model Context Protocol) server for the [Chinook SQLite database](https://www.sqlitetutorial.net/sqlite-sample-database/) and a sample Agno agent client for interactive querying. It enables LLMs and other MCP-compatible clients to safely explore and query the Chinook database using a standardized protocol.

## Key Features
- **Automatic Database Download:**
  - Downloads and extracts the Chinook SQLite database if not present.
- **Resource Endpoints:**
  - `schema://chinook/tables`: Returns the schema for all tables in the database.
  - `schema://chinook/table/{table_name}`: Returns the schema for a specific table.
- **SQL Query Tool:**
  - `run_sql_query`: Allows execution of read-only (SELECT) SQL queries. Only SELECT statements are permitted for safety.
- **Prompt Templates:**
  - Provides prompt templates for common tasks, such as listing tables, showing table schemas, counting rows, and querying top artists.
- **Safe SQL Identifier Escaping:**
  - Includes a local function to safely escape SQL identifiers for SQLite.
- **Agno Agent Integration:**
  - Includes a sample client (`agno_test_client.py`) that demonstrates how to connect to the MCP server and interact with it using an LLM agent.

## How to Get Started

### 1. Installation

- **Clone the repository:**
  ```bash
  git clone <your-repo-url>
  cd mcp-chinookdb-server
  ```
- **Install Python dependencies:**
  ```bash
  pip install -r requirements.txt
  # or, if using Poetry:
  poetry install
  ```
  Ensure you have Python 3.8+ installed.

### 2. Running the MCP Server

- **Start the server:**
  ```bash
  python chinook_mcp_server.py
  ```
  The server will automatically download the Chinook database if needed and start listening for MCP requests (default: stdio transport).

### 3. Using the Agno Test Client

- **Start the interactive client:**
  ```bash
  python agno_test_client.py
  ```
  This will launch a REPL where you can type natural language queries about the Chinook database. The client will start the MCP server (if not already running) and use an LLM (e.g., OpenAI GPT-4) to interpret your queries and interact with the database via MCP tools.

- **Example queries:**
  - `List all tables.`
  - `Show the schema for the Album table.`
  - `How many tracks are there in the database?`
  - `Who are the top 5 artists by number of tracks?`

- **To exit:** Type `q`, `quit`, or `exit` at the prompt.

## How the Programs Work

### chinook_mcp_server.py
- Implements an MCP server that exposes the Chinook database via resource endpoints, tools, and prompt templates.
- Handles automatic download and extraction of the database.
- Provides safe, read-only access to schema and data.
- Designed to be used by LLMs or any MCP-compatible client.

### agno_test_client.py
- Demonstrates how to connect to the MCP server using the Agno agent framework.
- Starts the MCP server as a subprocess (using `uv run chinook_mcp_server.py` for fast startup).
- Uses an LLM (e.g., OpenAI GPT-4) to interpret user queries and call MCP tools/resources.
- Provides a simple REPL for interactive exploration.

## Security Notes
- Only SELECT queries are allowed via the `run_sql_query` tool.
- SQL identifiers are safely escaped to prevent injection.

## Customization
- You can add more MCP resources, tools, or prompts by following the patterns in `chinook_mcp_server.py`.
- The client can be extended to use different LLMs or provide more advanced conversational features.

## References
- [Chinook Database Schema](https://www.sqlitetutorial.net/sqlite-sample-database/)
- [MCP Protocol](https://github.com/modelcontext/protocol)
- [Agno Agent Framework](https://github.com/modelcontext/agno)

---
