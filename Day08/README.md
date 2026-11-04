# 📅 Day 08: Introduction to MCP (Model Context Protocol)

## 🎯 Objective
To eliminate hardcoded `if/else` statements for tool execution and build a scalable, standardized architecture. We introduced **MCP (Model Context Protocol)**, allowing our AI agent to dynamically discover and execute tools hosted on a separate server, paving the way for decentralized AI capabilities.

---

## 🧠 Core Concepts Learned

### 1. The "Hardcoded Tool" Problem
In Day 7, our `assistant.py` had code like: `if tool == "weather": run_weather()`.
If we had 100 tools, our Python code would become a nightmare to maintain. Furthermore, if Developer A builds a Weather tool and Developer B builds a Calendar tool, every AI application would have to write custom integration code to use them. 

### 2. What is MCP?
**Model Context Protocol (MCP)** is an open standard that allows AI models to discover and use external capabilities (tools, databases, APIs) in a consistent way. Think of it as a universal adapter. 
*   If a tool is built on an MCP server, *any* AI agent with an MCP client can use it, regardless of who built it.

### 3. The 3 Components of MCP Architecture
1.  **MCP Server:** The actual host that owns and executes the tools (e.g., Weather Server, Database Server).
2.  **MCP Client:** The translator/interpreter. It connects to the server, asks for the list of tools, and requests execution. (Does not contain AI logic).
3.  **AI Agent (Host):** Our main application. It asks the client for tools, uses the LLM (Planner) to decide, and generates the final answer.

### 4. The 6-Step MCP Workflow
When a user asks a question, our agent performs these steps:
1. Connect to the MCP Server.
2. Discover all available tools dynamically.
3. Extract tool descriptions.
4. Give descriptions to the LLM (Planner) and ask it to choose the best tool.
5. Execute the selected tool through the MCP Client.
6. Generate a natural language response based on the tool's output.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `server.py` (The External Server)
*   Uses the `FastMCP` library.
*   Initializes the server: `mcp = FastMCP("Time Server")`.
*   Uses the `@mcp.tool()` decorator to expose Python functions (like `current_time`, `roll_dice`, `generate_password`) to the outside world. 
*   **Crucial:** The docstrings inside these functions act as the *tool descriptions* for the AI.

### 2. `mcp_client.py` (The Interpreter)
Contains async functions using the `fastmcp` Client class:
*   **`connect()`**: Launches the server in the background and establishes a connection.
*   **`discover_tools(client)`**: Fetches the list of tools and their descriptions from the server.
*   **`execute_tool(client, tool_name)`**: Sends a request to the server to run a specific tool and returns the result.
*   **`disconnect(client)`**: Closes the connection and shuts down the server process.

### 3. `agent.py` (The Orchestrator)
This is where the magic happens. It combines the LLM with the MCP Client.
*   **`build_tool_descriptions(tools)`**: Takes the raw MCP tool objects and formats them into a clean text string for the LLM.
*   **`planner(user_request, tools)`**: Creates a dynamic prompt containing the tool descriptions and asks Ollama to *"Reply ONLY with the tool name."*
*   **`generate_response(user_request, tool_result)`**: Takes the raw output from the MCP server and uses the LLM to convert it into a natural, human-like sentence.
*   **`main()`**: Ties the whole 6-step workflow together.

---

## 💻 Implementation Highlights

### The Server Decorator (`server.py`)
```python
@mcp.tool()
def roll_dice():
    """Roll a six-sided dice.""" # <--- The LLM uses this description!
    return random.randint(1, 6)