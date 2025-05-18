"""
chinook_mcp_server.py

MCP (Model Context Protocol) server for the Chinook SQLite database.
Provides safe, read-only access to the Chinook database schema and data for LLMs and MCP clients.

Features:
- Automatic download and extraction of the Chinook sample database if not present.
- Resource endpoints for listing all tables and their schemas, or a specific table's schema.
- Tool endpoint for executing SELECT queries (read-only).
- Prompt templates for common LLM tasks (list tables, show schema, count rows, query top artists).
- Safe SQL identifier escaping for SQLite.
- Designed for use with Agno agents or other MCP-compatible clients.
"""

import sqlite3
import asyncio
from pathlib import Path
import httpx # For downloading the database
import zipfile # For unzipping
import logging
from mcp.server.fastmcp import FastMCP, Context
import mcp.server.fastmcp.prompts.base as mcp_prompts


# --- Database Setup ---
# Path to the local SQLite database file
DB_FILE = Path("Chinook.db")
# URL to download the Chinook sample database zip
DB_URL = "https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip"

def get_db_connection():
    """
    Helper to get a SQLite connection with row factory set for dict-like access.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

async def download_chinook_db():
    """
    Download and extract the Chinook SQLite database if not already present.
    """
    if DB_FILE.exists():
        logging.info(f"{DB_FILE} already exists. Skipping download.")
        return

    logging.info(f"Downloading Chinook database from {DB_URL}...")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(DB_URL)
        response.raise_for_status() 
        
        zip_path = Path("chinook.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        
        logging.info(f"Downloaded chinook.zip. Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            db_file_name = None
            # Find the .db file in the zip archive
            for member in zip_ref.namelist():
                if member.endswith(".db"):
                    db_file_name = member
                    break
            if db_file_name:
                zip_ref.extract(db_file_name, path=".")
                extracted_db_path = Path(db_file_name)
                # Handle cases where the db file might be in a subdirectory within the zip
                if extracted_db_path.name != DB_FILE.name:
                    target_path = DB_FILE.parent / extracted_db_path.name
                    if target_path.exists() and target_path.is_dir():
                         (target_path / DB_FILE.name).rename(DB_FILE)
                         target_path.rmdir()
                    elif extracted_db_path.exists():
                        extracted_db_path.rename(DB_FILE)
                logging.info(f"Extracted {DB_FILE}")
            else:
                raise FileNotFoundError("Could not find .db file in downloaded zip.")
        zip_path.unlink() 
        logging.info("Chinook database setup complete.")

# --- Local SQL Identifier Escaping Function ---
def escape_sql_identifier_local(identifier: str) -> str:
    """
    Basic SQL identifier escaping for SQLite.
    Wraps in double quotes and escapes internal double quotes by doubling them.
    """
    if not isinstance(identifier, str):
        raise TypeError("Identifier must be a string")
    escaped_identifier = identifier.replace('"', '""')
    return f'"{escaped_identifier}"'

# --- MCP Server Initialization ---
# Create the MCP server instance with metadata and dependencies
mcp_server = FastMCP(
    "ChinookDBExplorer",
    description="MCP Server for exploring the Chinook SQLite database.",
    dependencies=["sqlite3", "httpx"]
)

def _get_table_names(conn: sqlite3.Connection) -> list[str]:
    """
    Returns a list of user table names in the database (excluding SQLite internal tables).
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    return [row["name"] for row in cursor.fetchall()]

def _get_table_schema(conn: sqlite3.Connection, table_name: str) -> str:
    """
    Returns a formatted string describing the schema of a specific table.
    """
    cursor = conn.cursor()
    try:
        if table_name not in _get_table_names(conn):
            return f"Table '{table_name}' not found."
        cursor.execute(f"PRAGMA table_info('{table_name}');")
    except sqlite3.Error as e:
        return f"Error fetching schema for table '{table_name}': {e}"
    columns = cursor.fetchall()
    if not columns:
        return f"Table '{table_name}' not found or has no columns."
    schema_str = f"Schema for table {table_name}:\n"
    for col in columns:
        schema_str += f"  - {col['name']} ({col['type']})"
        if col['pk']:
            schema_str += " PRIMARY KEY"
        if col['notnull']:
            schema_str += " NOT NULL"
        if col['dflt_value'] is not None:
            schema_str += f" DEFAULT {col['dflt_value']}"
        schema_str += "\n"
    return schema_str

# --- Resources ---
@mcp_server.resource("schema://chinook/tables")
async def list_tables_schema() -> str:
    """
    Provides the schema for all tables in the Chinook database.
    Returns a formatted string with the schema of each table.
    """
    with get_db_connection() as conn:
        table_names = _get_table_names(conn)
        full_schema = "Database Schema:\n\n"
        for table_name in table_names:
            full_schema += _get_table_schema(conn, table_name) + "\n---\n\n"
        return full_schema.strip()

@mcp_server.resource("schema://chinook/table/{table_name}")
async def get_specific_table_schema(table_name: str) -> str:
    """
    Provides the schema for a specific table in the Chinook database.
    Example usage: schema://chinook/table/Artist
    Returns a formatted string describing the table's schema.
    """
    with get_db_connection() as conn:
        table_schema = _get_table_schema(conn, table_name)
        return table_schema.strip()

# --- Tools ---
@mcp_server.tool()
async def run_sql_query(sql_query: str) -> str:
    """
    Executes a read-only (SELECT) SQL query against the Chinook database.
    Only SELECT statements are allowed for safety.
    Args:
        sql_query: The SQL SELECT query to execute.
    Returns:
        Query results as a formatted string, or an error message.
    """
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            if not rows:
                return "Query executed successfully, but returned no results."
            column_names = [description[0] for description in cursor.description]
            result_str = "Query Results:\n"
            result_str += ", ".join(column_names) + "\n"
            result_str += "-" * (len(", ".join(column_names))) + "\n"
            for row in rows:
                result_str += ", ".join(map(str, row)) + "\n"
            return result_str
    except sqlite3.Error as e:
        return f"SQL Error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Prompts ---
@mcp_server.prompt()
async def list_all_tables() -> list[mcp_prompts.Message]:
    """
    Generate a prompt to list all tables in the database using the schema resource.
    Returns a list of MCP prompt messages for LLMs.
    """
    return [
        mcp_prompts.UserMessage(
            "How can I see all the tables and their schemas in the Chinook database?"
        ),
        mcp_prompts.AssistantMessage(
            "You can inspect the `schema://chinook/tables` resource. "
            "It contains the schema for all tables. "
            "Alternatively, you can ask me to query specific information using SQL."
        )
    ]

@mcp_server.prompt()
async def show_table_schema(table_name: str) -> str:
    """
    Generate a prompt to show the schema for a specific table.
    Args:
        table_name: The name of the table to show the schema for.
    Returns:
        A string prompt for the LLM.
    """
    return (
        f"Please show me the schema for the '{table_name}' table. "
        f"You can use the `schema://chinook/table/{table_name}` resource."
    )

@mcp_server.prompt()
async def count_table_rows(table_name: str) -> str:
    """
    Generate a prompt to count the number of rows in a specific table.
    Args:
        table_name: The name of the table to count rows from.
    Returns:
        A string prompt for the LLM.
    """
    safe_table_name_for_prompt = escape_sql_identifier_local(table_name)
    return (
        f"How many rows are in the '{table_name}' table? "
        f"You can use the `run_sql_query` tool with a query like: "
        f"'SELECT COUNT(*) FROM {safe_table_name_for_prompt};'"
    )

@mcp_server.prompt()
async def query_top_artists(limit: int = 5) -> str:
    """
    Generate a prompt to find the top N artists by the number of tracks they have.
    Args:
        limit: The number of top artists to retrieve (default is 5).
    Returns:
        A string prompt for the LLM.
    """
    if not isinstance(limit, int) or limit < 1:
        return "Error: limit must be a positive integer."
    return (
        f"Can you show me the top {limit} artists with the most tracks? "
        "You'll likely need to join the 'Artist' and 'Album' tables, then 'Track' table, "
        "group by artist, count tracks, and order by the count descending, limiting to "
        f"{limit} results using the `run_sql_query` tool."
    )

# --- Main Execution ---
if __name__ == "__main__":
    # Download the Chinook database if needed before starting the MCP server
    async def pre_run_setup():
        await download_chinook_db()

    asyncio.run(pre_run_setup())
    
    # Start the MCP server using stdio transport
    mcp_server.run(transport="stdio")