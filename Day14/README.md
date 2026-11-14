# 📅 Day 14: Multi-Agent Architecture (Manager & Workers)

## 🎯 Objective
To build a scalable **Multi-Agent System** where a central **Manager Agent** orchestrates specialized workers (Researcher, Coder, Reviewer) to complete a complex task. We moved away from a single monolithic prompt to a modular architecture where each agent has a specific role. We also explored how to optimize execution using **Parallel Processing** (`asyncio.gather`).

---

## 🧠 Core Concepts Learned

### 1. The Multi-Agent Pattern
*   **The Problem:** A single LLM prompt doing research, coding, and reviewing often gets confused and hallucinates.
*   **The Solution:** Split the task into specialized agents (Workers) with a central Manager. This follows the **Single Responsibility Principle**.
    *   **Manager:** Decides *what* to do next.
    *   **Researcher:** Finds facts.
    *   **Coder:** Writes the code.
    *   **Reviewer:** Checks the code for bugs.

### 2. The Manager Loop & LLM Routing
*   The `manager.py` acts as the orchestrator. It uses an LLM (`choose_worker`) to look at the current **State** and decide the next worker.
*   **Fallback Logic:** Since LLMs can output garbage, we implemented a validation check: if the LLM doesn't output one of the `VALID_WORKERS`, the Python code falls back to a deterministic decision based on what is empty in the state.

### 3. State Management
*   We use a shared `state` dictionary (`state.py`) to pass information between agents.
*   `history` list tracks which agents have already run, preventing infinite loops and redundant work.

### 4. Sequential vs. Parallel Execution
*   **Sequential:** Task A ➡️ Task B ➡️ Task C. (Total time = A+B+C).
*   **Parallel:** Task A, B, and C run at the same time using `asyncio.gather()`. (Total time = Max(A, B, C)). We demonstrated this with `parallel_demo.py` to show how independent tasks should run concurrently to save time.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `state.py` (The Shared Memory)
*   A simple dictionary containing `task`, `research`, `code`, `review`, and `history`. This acts as the communication bridge between the Manager and the Workers.

### 2. `manager.py` (The Orchestrator)
*   **`choose_worker()`**: Creates a prompt for the LLM. It passes the current state (what's done, what's empty) and asks the LLM to reply with exactly one word: `research`, `coding`, `review`, or `finish`.
*   **`run_manager()`**: The main loop (`max_steps = 10`). It calls `choose_worker()`, executes the chosen agent, updates the state, and repeats until "finish".
*   *Guardrails:* Added checks to ensure if a worker already did its job, it doesn't run again (e.g., if `state["research"]` is not empty, skip research).

### 3. The Workers (`research_agent.py`, `coding_agent.py`, `reviewer_agent.py`)
*   Each file contains a simple function (`research`, `write_code`, `review`).
*   They take the relevant data from the state (e.g., Coder takes `task` and `research`), construct a specific prompt, call the LLM, and return the result.

### 4. `parallel_demo.py` (Optimization Concept)
*   A standalone script demonstrating `asyncio.gather()`.
*   It runs 3 mock agents (Research, Technology, Market) sequentially (takes 9 seconds) and then in parallel (takes 4 seconds). This proves the performance benefit of async concurrency.

---

## 💼 Most Asked Interview Questions (Day 14)

<details>
<summary><b>1. What is a Multi-Agent System, and why use it instead of a single agent?</b></summary>
<br>
A Multi-Agent System uses multiple specialized LLM instances (Workers) controlled by an orchestrator (Manager). A single agent often struggles with complex, multi-step tasks because the prompt becomes too large and contradictory. By splitting into specialized agents, each prompt is focused (e.g., "Write code" vs. "Review code"), resulting in higher accuracy and easier debugging.
</details>

<details>
<summary><b>2. How does the Manager Agent know which worker to call next?</b></summary>
<br>
The Manager uses an LLM as a router. In <code>choose_worker()</code>, we pass the current state (Research done? Code done?) to the LLM and ask it to return exactly one of the valid worker names. To prevent crashes, we added a <b>Python fallback</b> that checks the state directly if the LLM outputs an invalid word.
</details>

<details>
<summary><b>3. How did you prevent the Manager from getting stuck in an infinite loop?</b></summary>
<br>
We implemented two safeguards:
<ol>
  <li><b>Max Steps Limit:</b> The loop runs a maximum of 10 times.</li>
  <li><b>State Guardrails:</b> Before running a worker, the code checks if that worker's output already exists in the state. If it does, it skips it and moves to the next task.</li>
</ol>
</details>

<details>
<summary><b>4. Explain the difference between Sequential and Parallel execution in the context of AI agents.</b></summary>
<br>
Sequential execution means Agent B waits for Agent A to finish (e.g., Coder waits for Researcher). Parallel execution means independent tasks run simultaneously. If a Manager needs weather data, stock data, and news, these can be fetched in parallel using <code>asyncio.gather()</code>, reducing total execution time from 9 seconds to 4 seconds.
</details>

---

## 🔥 System Design & Architectural Insights (Senior Level)

<details>
<summary><b>1. The Manager uses an LLM to route tasks. What is the biggest risk with this approach?</b></summary>
<br>
<b>The Risk:</b> Non-determinism. The Manager LLM might make a wrong routing decision (e.g., calling the Reviewer before the Coder has written any code) or get stuck in a loop.
<br><b>The Production Fix:</b> We shouldn't rely entirely on the LLM. We need <b>Hardcoded State Machine Guardrails</b> (which we partially implemented). For example, Python should physically block the Reviewer from running if <code>state["code"]</code> is empty, regardless of what the LLM says.
</details>

<details>
<summary><b>2. In a Multi-Agent system, how do you manage the Context Window? Every agent adds to the state.</b></summary>
<br>
As the state grows (Research ➡️ Code ➡️ Review), passing the entire history to every agent exceeds the token limit. <b>The Fix:</b> Agents should only receive the <i>specific</i> context they need. The Coder only needs the Task + Research (not the review history). The Reviewer only needs the Code + Task. We achieve this by passing specific state keys, not the whole dictionary.
</details>

<details>
<summary><b>3. When should you use Parallel execution in an Agentic workflow? What are the pitfalls?</b></summary>
<br>
<b>When to use:</b> When tasks are completely independent (e.g., fetching data from 3 different APIs).
<br><b>The Pitfall:</b> <b>Rate Limits.</b> If you spawn 10 parallel LLM calls to OpenAI/Groq, you will instantly hit the Rate Limit (429 Error). Parallel execution also consumes more RAM and requires robust error handling (if one task fails, how do you handle the partial failure?).
</details>

<details>
<summary><b>4. If I want to add a "Testing Agent" to this architecture, how would you modify the code?</b></summary>
<br>
<ol>
  <li>Create <code>testing_agent.py</code> with a function <code>test_code(task, code)</code>.</li>
  <li>Update <code>state.py</code> to include <code>"tests": ""</code>.</li>
  <li>Update <code>VALID_WORKERS</code> in <code>manager.py</code> to include <code>"testing"</code>.</li>
  <li>Update the Manager's prompt rules: <i>"If Code exists but Tests are empty -> choose 'testing'"</i>.</li>
  <li>Add the execution block for the testing agent in the <code>run_manager</code> loop.</li>
</ol>
</details>

## 🚀 Next Steps
In Day 15, we will take this Multi-Agent system and make it **Production Ready** by adding Security (Path Traversal protection), Observability (Logging), and Reliability (Retry logic).