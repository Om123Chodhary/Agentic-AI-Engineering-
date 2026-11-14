# 📅 Day 13: Advanced MCP Ecosystem (Multi-Server, Registry & Remote)

## 🎯 Objective
To scale our Agent from using a single MCP server to a complete **MCP Ecosystem**. We built a **Tool Registry** to dynamically route tool calls to multiple different MCP servers, upgraded our Planner to output structured JSON with tool arguments, explored MCP Primitives (Tools, Resources, Prompts), and learned how to connect to **Remote MCP servers** over HTTP securely.

---

## 🧠 Core Concepts Learned

### 1. The Tool Registry (Multi-Server Routing)
*   **The Problem:** In Day 8, our agent was hardcoded to talk to one `server.py`. Real-world apps need multiple servers (Weather, Database, Email).
*   **The Solution (`mcp_manager.py`):** We created a central Registry (a Python dictionary). When all servers connect, the manager asks each server for its tools and maps: `tool_name -> {client, tool_object}`. When the Planner requests a tool, the Registry automatically knows *which* server to send the request to.

### 2. Structured Tool Arguments
*   **Day 8 Limitation:** Tools like `roll_dice` didn't take arguments.
*   **Day 13 Upgrade:** Our new `get_weather(city)` tool requires an argument. We upgraded the Planner prompt to return a **JSON dictionary** (`{"tool": "get_weather", "arguments": {"city": "Delhi"}}`) instead of a raw string. The Executor parses this JSON and passes it to the correct MCP client.

### 3. The 3 MCP Primitives
*   **Tools (Action):** Executes a function and returns a result (e.g., `get_weather`).
*   **Resources (Data):** Exposes static or dynamic data via a URI (e.g., `weather://cities` returns a list of supported cities). No operation is performed, just data retrieval.
*   **Prompts (Templates):** Exposes reusable prompt templates. Instead of writing complex prompts in the app, the MCP server can serve them (e.g., `weather_report(city)` returns a pre-formatted instruction block for the LLM).

### 4. Remote MCP (HTTP Transport)
*   MCP servers don't have to run locally. We changed `mcp.run(transport="http", host="127.0.0.1", port=8000)`.
*   The client now connects via URL (`http://127.0.0.1:8000`) instead of a local file path. This enables agents to use tools hosted on completely different machines across the internet.

### 5. Security (AuthN vs AuthZ)
*   **Authentication:** "Who are you?" (Verified via Bearer Tokens/API Keys).
*   **Authorization:** "What are you allowed to do?" (e.g., Client A can `read_file`, but cannot `delete_file`).
*   **Production Checklist:** HTTPS, Auth, Authorization, Secrets Management (`.env`), Logging, and Timeouts.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `weather-mcp-server/server.py`
*   A new MCP server hosting the `get_weather(city)` tool.
*   Uses `weather_data.get(city, "not available")` to mock weather data.

### 2. `mcp_client.py` (Updated)
*   `connect(server)`: Now takes a dynamic `server` path/URL as an argument instead of being hardcoded to `server.py`.

### 3. `mcp_manager.py` (The Core New Feature)
*   **`create_tool_registry(servers)`**: Takes a list of server paths. Connects to each, discovers tools, and builds the `tool_registry` dictionary mapping tool names to their respective clients.
*   **`run_tool(tool_registry, tool_name, arguments)`**: Looks up the tool in the registry, gets the correct client, and executes the tool.

### 4. `planner.py` (Updated)
*   The prompt now instructs the LLM to return **JSON**.
*   We use `json.loads(result)` to parse the LLM's string output into a Python dictionary. This handles complex arguments perfectly.

### 5. `executor.py`
*   Extracts `tool` and `arguments` from the planner's JSON response.
*   Calls `mcp_manager.run_tool()` instead of talking to a single client directly.

### 6. `loop.py` & `runner.py`
*   `loop.py` now accepts the `tool_registry` and uses `action["tool"]` to check for "FINISH".
*   `runner.py` initializes the `servers` list, builds the registry, runs the agent loop, and safely closes all connections.

---

## 💼 Most Asked Questions (Day 13)

<details>
<summary><b>1. Why do we need an MCP Tool Registry? Can't the Agent just call the server directly?</b></summary>
<br>
If we have 5 different MCP servers (Time, Weather, DB, Email, Slack), the Agent doesn't know which server hosts which tool. The Tool Registry acts as a DNS/Load Balancer. It maps a tool name (e.g., <code>get_weather</code>) to the specific MCP client connected to the Weather Server. The Agent just says "I need <code>get_weather</code>", and the registry handles the routing.
</details>

<details>
<summary><b>2. How did you handle tools that require arguments (like passing a city name to get_weather)?</b></summary>
<br>
We upgraded the Planner to output structured JSON instead of raw text. The LLM now returns <code>{"tool": "get_weather", "arguments": {"city": "Delhi"}}</code>. In Python, we use <code>json.loads()</code> to parse this. The Executor extracts the arguments and passes them directly to the MCP client using <code>client.call_tool(tool_name, arguments)</code>.
</details>

<details>
<summary><b>3. What is the difference between a Tool, a Resource, and a Prompt in MCP?</b></summary>
<br>
<ul>
  <li><b>Tool:</b> An executable function that performs an action (e.g., <code>generate_password()</code>).</li>
  <li><b>Resource:</b> Read-only data exposed via a URI (e.g., <code>file://documents/python.txt</code>). It doesn't execute logic; it just provides context.</li>
  <li><b>Prompt:</b> A reusable template/instruction provided by the server (e.g., <code>mcp.prompt()</code>). It helps standardize how the LLM is prompted.</li>
</ul>
</details>

<details>
<summary><b>4. How do you secure a Remote MCP Server?</b></summary>
<br>
We use two concepts:
<ul>
  <li><b>Authentication (AuthN):</b> Verifying the client via Bearer Tokens or API Keys (e.g., checking <code>MCP_TOKEN</code>).</li>
  <li><b>Authorization (AuthZ):</b> Limiting access (e.g., Client A can read data, but Client B can delete data).</li>
</ul>
Additionally, production MCP requires HTTPS (encrypted transport), timeouts to prevent hanging, and structured logging.
</details>

---

## 🔥 System Design & Architectural Insights (Senior Level)

<details>
<summary><b>1. If you have 50 MCP servers, connecting to all of them at startup will be slow. How do you optimize this?</b></summary>
<br>
<b>The Bottleneck:</b> Sequential connection and <code>list_tools()</code> calls will take minutes.<br>
<b>The Solution:</b> Use <b>AsyncIO concurrency</b> (e.g., <code>asyncio.gather()</code>) to connect to all 50 servers in parallel. Additionally, we should implement <b>Lazy Loading</b>: only connect to a server when a tool from that specific server is actually requested by the Planner.
</details>

<details>
<summary><b>2. The Planner now returns JSON. What happens if the LLM returns invalid JSON (a syntax error) and the code crashes?</b></summary>
<br>
This is a major reliability issue. If <code>json.loads()</code> fails, the agent loop breaks. In production, we must wrap the parsing in a <code>try-except</code> block. If it fails, we should catch the error, append a system message to the chat history (<i>"Invalid JSON format. Please return valid JSON."</i>), and re-prompt the LLM to try again without crashing the loop.
</details>

<details>
<summary><b>3. When should you use an MCP Resource instead of an MCP Tool?</b></summary>
<br>
Use a <b>Resource</b> when the data is static or requires no server-side computation (e.g., reading a configuration file, fetching a list of supported cities). Use a <b>Tool</b> when the user's request requires an active operation, API call, or database query that changes state or computes a result.
</details>

<details>
<summary><b>4. The `create_tool_registry` maps tool names to clients. What happens if two different MCP servers expose a tool with the exact same name?</b></summary>
<br>
Our current dictionary approach will cause a <b>Collision</b> (the second server's tool will overwrite the first one). In a production system, we must namespace the tools (e.g., <code>weather__get_weather</code> and <code>time__get_weather</code>) or store the registry as a list of tuples and handle the disambiguation at the Planner level.
</details>

<details>
<summary><b>5. How do you handle timeouts if a Remote MCP server goes down?</b></summary>
<br>
If an MCP server is unresponsive, the agent will hang indefinitely if we don't implement timeouts. We should wrap the <code>client.call_tool()</code> in <code>asyncio.wait_for(timeout=10.0)</code>. If it times out, the registry should return an error observation ("Server Timeout") to the state, allowing the agent to re-plan and try a different approach.
</details>

## 🚀 Next Steps
In Day 14, we will build our own **Multi-Agent Architecture (Manager, Researcher, Coder, Reviewer)** from scratch, combining everything we've learned about tools, memory, and orchestration.