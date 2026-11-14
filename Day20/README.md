# 📅 Day 20: Productionizing AI Agents (Deployment, Reliability & Observability)

## 🎯 Objective
To transform our local, terminal-based AI Agent into a **Production-Ready Web Service**. We wrapped the agent inside a FastAPI server, containerized it using Docker, and implemented critical production features like Rate Limiting, Timeout handling, Structured Logging (UUID), and Automated Evaluation. We learned that "working code" is not the same as "production code."

---

## 🧠 Core Concepts Learned

### 1. The API Layer (FastAPI & Pydantic)
*   **The Boundary:** FastAPI acts as the secure boundary between the outside world (users/browsers) and our internal AI agent.
*   **Pydantic Validation (`schemas.py`):** We enforce strict data types. If a user sends an empty payload, FastAPI automatically returns a `422 Unprocessable Entity` error *before* it reaches the expensive LLM.
*   **Lifespan (`@asynccontextmanager`):** Instead of initializing the agent on every request, we initialize it once during the server startup (`yield`), saving memory and latency.

### 2. The 3 Layers of Reliability
LLMs can fail, network glitches can happen, and servers can hang. We implemented:
*   **Timeout (`asyncio.wait_for`):** If the LLM takes more than 60 seconds, the request is cancelled. This prevents the server from hanging indefinitely.
*   **Retry (`tenacity`):** If a temporary network glitch occurs, the system retries up to 2 times using Exponential Backoff (waiting 1s, then 4s) to give the API time to recover.
*   **Rate Limiting (Sliding Window Algorithm):** Prevents spam and DDoS attacks. We used `collections.deque` to track timestamps. If an IP makes more than 10 requests per minute, they receive a `429 Too Many Requests` error.

### 3. Observability (Structured Logging)
*   `print()` is useless in production. We used Python's `logging` module.
*   **Request IDs (UUID):** Every incoming request gets a unique `uuid.uuid4()`. This ID is injected into every log. If an error occurs, we can trace the exact journey of that specific request using the UUID.
*   **Timing:** Used `time.perf_counter()` to measure exactly how long the agent took to respond.

### 4. Containerization (Docker)
*   **Dockerfile:** Packaged the app, Python version, and requirements into a reproducible image.
*   **The Networking Gotcha:** Inside a Docker container, `localhost` means the container itself, not your Windows machine. To connect to Ollama running on the host, we used **`host.docker.internal`** in the `.env` file.

### 5. Automated Agent Evaluation
*   **API Success ≠ Agent Success:** Just because the API returned `200 OK` doesn't mean the agent did the right thing (it might have called the wrong tool).
*   **Deterministic Tests (`run_evaluation.py`):** We created a dataset of questions and `expected_tools`. The evaluation script inspects the `result["messages"]` to ensure the correct tool was invoked and calculates a Pass/Fail score.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `main.py` (The Orchestrator)
*   Sets up the FastAPI app.
*   Implements `/health` (Liveness) and `/ready` (Readiness checking Ollama via `httpx`).
*   Implements `/chat` endpoint with Rate Limiting, Retry, Timeout, and UUID logging.

### 2. `agent.py` (The Brain)
*   `create_agent_instance()`: Initializes the LangChain agent with MCP tools (`current_time`, `roll_dice`) and the RAG tool (`search_knowledge`).

### 3. `evaluate.py`, `run_evaluation.py`, `test_cases.py` (The Test Suite)
*   `test_cases.py`: Contains questions and expected tools.
*   `run_evaluation.py`: Runs the agent against all test cases.
*   `evaluate.py`: Inspects the `tool_calls` in the agent's message history to verify if the agent used the right tool.

### 4. `Dockerfile` & `docker-compose.yml` (The Infrastructure)
*   Packages the app and exposes port 8000.
*   `docker-compose.yml` adds the `extra_hosts` flag to enable `host.docker.internal` communication.

---

## 💼 Most Asked Interview Questions (Day 20)

<details>
<summary><b>1. What is the difference between Liveness and Readiness checks?</b></summary>
<br>
<ul>
  <li><b>Liveness (/health):</b> Answers "Is the FastAPI process running?" If this fails, the orchestrator (Docker/Kubernetes) restarts the container.</li>
  <li><b>Readiness (/ready):</b> Answers "Is the application ready to handle traffic?" It checks dependencies (like the Ollama LLM). If Ollama is down, it returns <code>not_ready</code>, and the load balancer stops sending traffic to this instance.</li>
</ul>
</details>

<details>
<summary><b>2. Why do we use `host.docker.internal` instead of `localhost` in Docker?</b></summary>
<br>
When an app runs inside a Docker container, its network is isolated. <code>localhost</code> inside the container refers to the container itself, not your host Windows/Mac machine. Since Ollama runs on the host machine, the container must use <code>host.docker.internal</code> to route the request outside the container to the host.
</details>

<details>
<summary><b>3. How does the Sliding Window Rate Limiter work?</b></summary>
<br>
We use a dictionary of deques (<code>request_times</code>) mapped by the client's IP. On every request, we remove timestamps older than 60 seconds (<code>while times and now - times[0] > 60: times.popleft()</code>). If the length of the deque exceeds 10, we block the request. Using <code>deque</code> is crucial because removing from the left is O(1) time complexity.
</details>

<details>
<summary><b>4. Why wrap the LLM call in `asyncio.wait_for()`?</b></summary>
<br>
LLMs can sometimes hang (e.g., if the server is overloaded). Without a timeout, the FastAPI worker will wait indefinitely, consuming memory and blocking other users. <code>asyncio.wait_for()</code> kills the coroutine after a fixed time (e.g., 60s), raising a <code>TimeoutError</code> which we catch and return as a clean <code>504 Gateway Timeout</code>.
</details>

<details>
<summary><b>5. How did you evaluate the agent? Can it be done manually?</b></summary>
<br>
Manual evaluation ("asking questions and seeing if it looks right") doesn't scale. We built an automated evaluation script. For every test case, we inspect the agent's internal <code>messages</code> history to see if it called the expected tool. We calculate a pass/fail score. In production, this runs in CI/CD, and if the score drops, deployment is blocked.
</details>

---

## 🔥 System Design & Architectural Insights (Senior Level)

<details>
<summary><b>1. Your Retry logic uses `tenacity` with Exponential Backoff. Why not just retry immediately?</b></summary>
<br>
<b>The Thundering Herd Problem:</b> If an LLM API fails and 1,000 clients instantly retry at the exact same millisecond, the API will crash again. Exponential backoff (waiting 1s, then 2s, then 4s) spreads out the retry traffic, giving the failing server time to recover.
</details>

<details>
<summary><b>2. The Rate Limiter uses an in-memory Python dictionary. What happens if you deploy 3 instances of this app behind a Load Balancer?</b></summary>
<br>
<b>The Flaw:</b> Each instance has its own memory. If User A hits Instance 1 five times, and Instance 2 five times, the rate limiter will allow it (total 10), bypassing the limit.<br>
<b>The Production Fix:</b> The rate limit state must be stored in a centralized cache like <b>Redis</b>. Redis supports atomic increment and expiration operations, ensuring accurate rate limiting across all distributed server instances.
</details>

<details>
<summary><b>3. What are "Zombie Tasks" in FastAPI, and how do you prevent them?</b></summary>
<br>
If a user disconnects (closes the browser) while the LLM is still processing, FastAPI doesn't automatically kill the background task. The server keeps computing, wasting API tokens.<br>
<b>The Fix:</b> We need to check <code>await request.is_disconnected()</code> inside the chat loop. If disconnected, we must call <code>task.cancel()</code> to abort the LLM call.
</details>

<details>
<summary><b>4. How do you prevent internal Python errors (like Database/LLM stack traces) from leaking to the user?</b></summary>
<br>
We wrap the endpoint in a <code>try-except</code> block. If an exception occurs, we log the full stack trace internally using <code>logger.exception()</code>. But to the client, we return a generic <code>HTTPException(status_code=500, detail="Agent execution failed")</code>. This prevents hackers from exploiting internal system details.
</details>

<details>
<summary><b>5. How does Docker Compose help in a local multi-container setup?</b></summary>
<br>
Our app needs a database (or Ollama) running alongside it. Instead of running <code>docker run</code> commands separately, Docker Compose defines the services, their networks, and volumes in a single YAML file. It ensures that the app container can securely communicate with the DB container using internal DNS names.
</details>

## 🚀 Next Steps
In Day 21, we will build the Frontend (UI) for this service, connecting it via Server-Sent Events (SSE) to show real-time progress to the user.