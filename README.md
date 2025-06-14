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
  curl -LsSf https://astral.sh/uv/install.sh | sh
  git clone <your-repo-url>
  cd mcp-chinookdb-server
  ```
- **Install Python dependencies using uv:**
  ```bash
  uv sync
  ```
  Ensure you have Python 3.8+ installed and [uv](https://github.com/astral-sh/uv) available in your environment.

### 2. Running the MCP Server

- **Start the server:**
  ```bash
  uv run chinook_mcp_server.py
  ```
  The server will automatically download the Chinook database if needed and start listening for MCP requests (default: stdio transport).

### 3. Using the Agno Test Client

- **Start the interactive client:**
  ```bash
  uv run agno_test_client.py
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

## Chinook Database Overview

The Chinook SQLite database is a sample database that models a digital music store, similar to iTunes. It is widely used for SQL learning and demonstrations. The schema is designed to represent the core entities and relationships found in an online music store, including customers, employees, artists, albums, tracks, invoices, and more.

### Concept Overview
- **Artists** release **albums**.
- **Albums** contain multiple **tracks** (songs or audio files).
- **Tracks** are categorized by **genre** and **media type**.
- **Customers** purchase tracks via **invoices**.
- **Employees** represent staff, including sales support.
- **Invoice lines** detail each track purchased in an invoice.
- **Playlists** allow grouping of tracks for listening.

### Main Tables and Columns

- **Artist**
  - `ArtistId` (INTEGER, PK): Unique artist identifier
  - `Name` (NVARCHAR): Artist name

- **Album**
  - `AlbumId` (INTEGER, PK): Unique album identifier
  - `Title` (NVARCHAR): Album title
  - `ArtistId` (INTEGER, FK): Reference to the artist

- **Track**
  - `TrackId` (INTEGER, PK): Unique track identifier
  - `Name` (NVARCHAR): Track name
  - `AlbumId` (INTEGER, FK): Reference to the album
  - `MediaTypeId` (INTEGER, FK): Reference to the media type
  - `GenreId` (INTEGER, FK): Reference to the genre
  - `Composer` (NVARCHAR): Composer name
  - `Milliseconds` (INTEGER): Track length
  - `Bytes` (INTEGER): File size
  - `UnitPrice` (NUMERIC): Price per track

- **Genre**
  - `GenreId` (INTEGER, PK): Unique genre identifier
  - `Name` (NVARCHAR): Genre name

- **MediaType**
  - `MediaTypeId` (INTEGER, PK): Unique media type identifier
  - `Name` (NVARCHAR): Media type name (e.g., MPEG audio, AAC audio)

- **Customer**
  - `CustomerId` (INTEGER, PK): Unique customer identifier
  - `FirstName`, `LastName` (NVARCHAR): Customer name
  - `Company`, `Address`, `City`, `State`, `Country`, `PostalCode` (NVARCHAR): Contact info
  - `Phone`, `Fax`, `Email` (NVARCHAR): Contact info
  - `SupportRepId` (INTEGER, FK): Employee assigned to the customer

- **Employee**
  - `EmployeeId` (INTEGER, PK): Unique employee identifier
  - `LastName`, `FirstName` (NVARCHAR): Employee name
  - `Title` (NVARCHAR): Job title
  - `ReportsTo` (INTEGER, FK): Manager
  - `BirthDate`, `HireDate` (DATETIME): Dates
  - `Address`, `City`, `State`, `Country`, `PostalCode`, `Phone`, `Fax`, `Email` (NVARCHAR): Contact info

- **Invoice**
  - `InvoiceId` (INTEGER, PK): Unique invoice identifier
  - `CustomerId` (INTEGER, FK): Customer making the purchase
  - `InvoiceDate` (DATETIME): Date of invoice
  - `BillingAddress`, `BillingCity`, `BillingState`, `BillingCountry`, `BillingPostalCode` (NVARCHAR): Billing info
  - `Total` (NUMERIC): Total amount

- **InvoiceLine**
  - `InvoiceLineId` (INTEGER, PK): Unique line item identifier
  - `InvoiceId` (INTEGER, FK): Reference to invoice
  - `TrackId` (INTEGER, FK): Reference to track
  - `UnitPrice` (NUMERIC): Price per track
  - `Quantity` (INTEGER): Number of tracks purchased

- **Playlist**
  - `PlaylistId` (INTEGER, PK): Unique playlist identifier
  - `Name` (NVARCHAR): Playlist name

- **PlaylistTrack**
  - `PlaylistId` (INTEGER, FK): Reference to playlist
  - `TrackId` (INTEGER, FK): Reference to track

This schema enables a wide range of queries and analytics, such as finding top artists, most popular genres, customer purchase history, and more.

---
