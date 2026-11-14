# 📅 Day 21: Local Full-Stack AI Agent (FastAPI + Ollama)

## 🎯 Objective
To transition our autonomous AI Research Agent (from Day 18) from a terminal-based script into a **Local Web Service**. We used **FastAPI** to create an HTTP backend, **Pydantic** for strict request validation, and served a static HTML/CSS frontend. Most importantly, we converted our synchronous agent loop into an **asynchronous** architecture to ensure heavy tasks (like web scraping) don't freeze the server.

---

## 🧠 Core Concepts Learned

### 1. The FastAPI Boundary
*   **The Problem:** Running `python main.py` requires a terminal. We want users to interact with the agent via a browser.
*   **The Solution:** `main.py` sets up a FastAPI server. It exposes a `POST /chat` endpoint that accepts a JSON payload (`{"message": "..."}`).
*   **Static File Serving:** We used `app.mount("/static", StaticFiles(directory="frontend"))` to serve `index.html`, `style.css`, and `app.js` to the browser.

### 2. Strict Input Validation (`schemas.py`)
*   We defined `ChatRequest` and `ChatResponse` using Pydantic.
*   If a user sends an empty message or invalid JSON, FastAPI automatically returns a `422 Unprocessable Entity` error. We also added a manual check (`if not request.message.strip()`) to raise an `HTTP 400` to save LLM compute costs.

### 3. The Shift to Asynchronous Execution
*   **Agent Loop (`agent.py`):** We changed `def research_agent` to `async def research_agent`. We used `await tool_function(**arguments)` inside the loop.
*   **Non-Blocking Tools (`tools.py`):** The `search_web` function relies on a synchronous library (`webless`). We wrapped it in `asyncio.to_thread()`. This prevents the search operation from blocking the FastAPI event loop, allowing the server to respond to `/health` checks while a search is happening.

### 4. Local Ollama Integration
*   Both `agent.py` and `tools.py` use the local `ollama.chat` client.
*   The verifier uses `format="json"` to force the LLM to return structured JSON for evidence verification.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `main.py` (The Web Server)
*   **`lifespan`**: Handles startup and shutdown (prints logs).
*   **`/`**: Returns the `index.html` file.
*   **`/health`**: Liveness check.
*   **`/chat`**: The core endpoint. Validates input, awaits `run_agent()`, and catches exceptions to return a clean `HTTP 500` instead of a Python traceback.

### 2. `agent.py` (The Orchestrator)
*   `create_research_plan()`: Synchronous LLM call to generate the plan.
*   `research_agent()`: Now `async`. Includes the `search_done` and `read_done` enforcement logic to prevent hallucination.
*   `run_agent()`: Await the research agent, fetch verified notes, and generate the final report.

### 3. `tools.py` (The Capabilities)
*   `search_web()`: Now `async`. Uses `asyncio.to_thread(search_sync, ...)` to offload the blocking search to a background thread.
*   `read_webpage()`: Synchronous `requests.get` with BeautifulSoup to extract text.
*   `verify_finding()`: Synchronous `ollama.chat` call with `format="json"` to ensure strict boolean output.

### 4. `frontend/` (The UI)
*   **`index.html`**: Contains the text area and "Start Research" button.
*   **`style.css`**: Basic clean styling.
*   **`app.js`**: **Currently a placeholder.** It has a click listener that just prints "Ready to start research...". (The actual `fetch()` API call to the `/chat` endpoint will be added in the next step/Day 22).

---

## 💼 Most Asked Interview Questions (Day 21)

<details>
<summary><b>1. Why did you make `search_web` asynchronous using `asyncio.to_thread`?</b></summary>
<br>
FastAPI runs on an asynchronous event loop. If a synchronous network call (like <code>requests.get</code> or the <code>webless</code> search) is executed directly, it blocks the entire event loop. During that time, no other users can connect to the server. <code>asyncio.to_thread</code> moves the blocking call to a separate thread pool, keeping the FastAPI server responsive.
</details>

<details>
<summary><b>2. What is the role of Pydantic in `schemas.py`?</b></summary>
<br>
Pydantic enforces type safety and data validation. By defining <code>ChatRequest(BaseModel)</code>, we tell FastAPI: "The incoming JSON must have a 'message' field, and it must be a string." If the frontend sends `{"msg": "hello"}` instead of `{"message": "hello"}`, FastAPI rejects it immediately.
</details>

<details>
<summary><b>3. How does the API handle errors if the local Ollama server is turned off?</b></summary>
<br>
In <code>main.py</code>, the <code>run_agent()</code> call is wrapped in a <code>try-except</code> block. If Ollama is down, the code throws an exception. We catch it and raise an <code>HTTPException(status_code=500)</code>. The browser receives a clean JSON error, not a massive Python stack trace.
</details>

---

## 🔥 System Design & Architectural Insights (Senior Level)

<details>
<summary><b>1. If 3 users hit the `/chat` endpoint at the exact same time using Local Ollama, what will happen?</b></summary>
<br>
<b>The Bottleneck:</b> FastAPI will accept all 3 requests asynchronously. However, the local Ollama instance (running on a single GPU/CPU) processes inferences sequentially. The first request will get the LLM, while the other two will experience massive delays (queuing) until the GPU is free. <br>
<b>The Fix:</b> For true concurrency, you cannot rely on a single local LLM. You need a cloud provider (like Groq or OpenAI) or a multi-GPU inference server.
</details>

<details>
<summary><b>2. The `/chat` endpoint currently waits for the entire 60-second agent process to finish before returning a response. How do you fix this bad user experience?</b></summary>
<br>
This architecture will likely hit an HTTP timeout. The solution is to implement <b>Server-Sent Events (SSE)</b>. Instead of waiting for the final report, the backend should yield progress updates (e.g., "Searching...", "Reading...", "Verifying...") so the user sees live activity on the frontend.
</details>

<details>
<summary><b>3. Why is serving the frontend via FastAPI (`app.mount`) better than opening `index.html` directly?</b></summary>
<br>
If you double-click <code>index.html</code>, the browser opens it via the <code>file://</code> protocol. If the JavaScript tries to make a <code>fetch()</code> call to <code>http://localhost:8000/chat</code>, the browser will block it due to <b>CORS (Cross-Origin Resource Sharing)</b> policies. Serving the frontend from the same FastAPI server ensures the frontend and backend share the same origin (<code>http://localhost:8000</code>).
</details>