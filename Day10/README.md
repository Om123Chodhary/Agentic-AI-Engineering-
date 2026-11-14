# 📅 Day 10: Task Decomposition & Dynamic Re-planning

## 🎯 Objective
To upgrade our Agent Loop from handling single-action requests to solving **Complex Multi-Step Goals**. We introduced **Task Decomposition** (breaking a large user goal into smaller, actionable tasks) and upgraded the **Planner** to be "State-Aware," ensuring it selects tasks sequentially and handles failures dynamically (Dynamic Re-planning).

---

## 🧠 Core Concepts Learned

### 1. Task Decomposition
In Day 9, if a user asked *"Generate a password and tell me the time"*, the planner would just pick one tool and stop. 
*   **The Solution:** We built a `task_planner.py` that uses an LLM to break the user's goal into a numbered list of smaller tasks. (e.g., Task 1: Generate a password, Task 2: Get current time).
*   **Why it matters:** LLMs perform much better when given small, focused tasks rather than one massive, complex instruction.

### 2. The New State Architecture
Our `state.py` was expanded to hold working memory for the new architecture. It now tracks:
*   `tasks`: A list of dictionaries containing the task name and its status (`pending` or `completed`).
*   `current_task`: The specific task the agent is currently working on.
*   `results`: Intermediate outputs of the tasks.

### 3. State-Aware Planner
The Planner LLM no longer just guesses the next action. Its prompt is now dynamic. It receives the list of tasks (with their statuses), completed actions, and previous observations. It outputs **two lines**:
*   `TASK: <The exact pending task>`
*   `TOOL: <The best tool to complete it>`

### 4. Dynamic Re-planning (Handling Failures)
What if a tool fails (e.g., MCP Server is down)? 
*   We added a rule to the Planner's prompt: *"If an action failed, reconsider the current plan."* 
*   If the observation starts with the word `Error`, the system does not mark the task as completed. It adds a "failed result" to the state and loops back. The planner sees the failure and can choose a different approach.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `task_planner.py` (The Decomposer)
*   **`decompose_task(user_request)`**: Uses an LLM to break the user's goal into a list of strings. It instructs the LLM: *"Return one task per line. Do not number them."*
*   The Python code then splits the response by lines to create a clean Python list of tasks.

### 2. `state.py` (The Memory Manager)
*   **`add_task()`**: Adds a new task dictionary to the state with `status: pending`.
*   **`complete_task()`**: Marks a task as `completed` (uses fuzzy matching to ensure the LLM's task string matches the stored task string).
*   **`get_pending_tasks()` / `all_tasks_completed()`**: Helper functions to check the current progress.

### 3. `planner.py` (The Orchestrator)
*   **The Prompt**: Given the pending tasks and observations, the LLM decides the next move.
*   **Output Format**: Forces the LLM to output strictly `TASK: ...` and `TOOL: ...`.

### 4. `loop.py` (The Agent Loop)
1.  Takes the `user_request`.
2.  Calls `decompose_task()` to get the task list.
3.  Adds all tasks to the state.
4.  Enters the `while can_continue(state)` loop.
5.  Calls `planner()` to get the next TASK and TOOL.
6.  **`parse_decision()`**: A utility function that parses the LLM's raw text output. It uses regex/string splitting to safely extract the task and tool name, handling cases where the LLM puts them on the same line.
7.  Executes the tool, updates state, and marks the task as completed (if successful).

### 5. `answer.py` (The Final Synthesizer)
*   Takes the final state (all tasks, actions, and observations) and generates a natural language response. 
*   Prompting rule: *"Do not mention internal state, planner, MCP, or tools."*

---

## 💻 Implementation Highlights

### The Dynamic `parse_decision` Function (`loop.py`)
LLMs are unpredictable. Sometimes they format the output perfectly; sometimes they put TASK and TOOL on the same line. We built a robust parser to handle this:

```python
def parse_decision(decision):
    task = None
    tool = None

    # Handle standard two-line format
    for line in decision.splitlines():
        line = line.strip()
        if line.startswith("TASK:"):
            task = line[5:].strip()
        elif line.startswith("TOOL:"):
            tool = line[5:].strip()

    # Handle case where LLM puts both on one line
    if task and "TOOL:" in task:
        parts = task.split("TOOL:", 1)
        task = parts[0].strip()
        if not tool:
            tool = parts[1].strip()

    return task, tool

## 🧠 System Design & Architectural Insights 

*The following questions go beyond basic definitions and explore the architectural trade-offs, failure modes, and scalability of this Agentic system.*

<details>
<summary><b>1. Why do we need a separate Task Decomposer? Why not give the whole goal directly to the Planner?</b></summary>
<br>

**The Context:** If the main Planner LLM is given a complex goal directly (e.g., "Generate a report on AI"), it suffers from **Instruction Drift**. Over multiple loops, the LLM forgets previous steps or hallucinates that it has already completed a task it hasn't.

**The Solution:** By creating a separate `task_planner.py`, we create a **static "Source of Truth"** upfront. The Decomposer breaks the goal into a structured list. The main Planner's job becomes much simpler: it only looks at the `state["tasks"]` list, finds the first `pending` task, and selects the tool. 

**Trade-off:** It adds one extra LLM call at the beginning, but drastically increases the reliability and determinism of the execution loop.
</details>

<details>
<summary><b>2. Task Decomposition creates a static list. What happens if the agent discovers a new requirement mid-execution?</b></summary>
<br>

**The Challenge:** Real-world tasks are dynamic. If a tool returns an unexpected result, the original plan might become obsolete.

**The Solution (Dynamic Re-planning):** Our architecture is designed to support this. If a tool fails or returns a sub-goal, the agent can be instructed to re-invoke the `decompose_task()` function mid-loop. It can append new tasks to the state with a `pending` status. Because the Planner always looks at the state dynamically, it will automatically pick up these new tasks without breaking the loop.
</details>

<details>
<summary><b>3. How does the system handle it if the LLM misinterprets the user's goal or generates a flawed plan?</b></summary>
<br>

**The Challenge:** LLMs are probabilistic. A bad decomposition will lead to a failed execution.

**The Engineering Solutions:**
1. **Human-in-the-Loop (HITL):** In a production environment, we would add an `interrupt()` step after decomposition to ask the user: *"I have planned these 3 tasks. Shall I proceed?"*
2. **Prompt Guardrails:** We instruct the Decomposer: *"Only create tasks directly necessary for the request. If the prompt is ambiguous, create a task to ask the user for clarification."*
3. **Max Steps Limit:** The `can_continue()` function acts as a safety valve. If the plan is fundamentally flawed and loops infinitely, the `max_steps` limit gracefully terminates the process.
</details>

<details>
<summary><b>4. This architecture relies on 2+ LLM calls per loop (Planner + Executor). Doesn't this cause high latency and cost?</b></summary>
<br>

**The Challenge:** LLM calls are expensive and slow. A multi-agent/multi-step loop multiplies this cost.

**The Solution & Trade-offs:** This is a classic **Speed vs. Accuracy** trade-off. For a simple query (e.g., "What is the time?"), this architecture is overkill. However, for complex tasks, the accuracy gained by sequential planning justifies the cost. 
To optimize in production, we can:
*   **LLM Routing:** Use a smaller, cheaper model (like Gemini Flash Lite) for the Planner, and a larger model (like GPT-4/Claude) for the final Answer generation.
*   **Caching:** Cache frequent tool outputs so the agent doesn't call the MCP server repeatedly for the same data.
</details>

<details>
<summary><b>5. If the MCP Server goes down mid-loop, how does the agent recover? Explain the state changes.</b></summary>
<br>

**The Challenge:** External dependencies (MCP, APIs) are prone to failure. The agent should not crash.

**The Solution (Graceful Degradation):** 
1. The `execute_action()` function is wrapped in error handling. If the MCP server is down, it returns an error string.
2. The loop detects this (e.g., `if observation.startswith("error")`). 
3. **Crucially, it does NOT mark the task as completed.** It appends the error to `state["results"]` and loops back.
4. The Planner sees this error in its context. It can now dynamically **re-plan**, perhaps by choosing a fallback tool or retrying the task.
</details>

<details>
<summary><b>6. Why use a custom text parser (`parse_decision`) instead of forcing the LLM to output JSON?</b></summary>
<br>

**The Context:** In this educational implementation, we used a custom two-line format (`TASK: ... \n TOOL: ...`) and built a Python parser to extract the data.

**Production Best Practice:** In an enterprise setting, **JSON is strictly preferred.** We would use OpenAI's `response_format={"type": "json_object"}` or Function Calling. This forces the LLM to output a strictly validated schema (e.g., `{"task": "...", "tool": "..."}`). It eliminates the need for custom string parsing and makes the system virtually immune to formatting hallucinations.
</details>

<details>
<summary><b>7. How would you test this agent architecture to ensure it's reliable?</b></summary>
<br>

**The Challenge:** Manual testing ("seeing if the output looks right") is not scalable or reliable.

**The Testing Strategy:**
1. **Unit Tests (State):** Mock a state and assert that `add_task()`, `complete_task()`, and `can_continue()` work exactly as expected.
2. **Parser Tests:** Feed `parse_decision()` various messy LLM outputs (one-line, two-line, missing spaces) and assert it correctly extracts the Task and Tool.
3. **Integration Tests (Loop):** Mock the `planner()` to return a fixed sequence of tasks, and mock the `execute_action()` to return fake data. Assert that the loop terminates successfully and updates the state correctly.
</details>

<details>
<summary><b>8. This runs as a single Python process. How would you scale this to handle 1000 concurrent users?</b></summary>
<br>

**The Challenge:** A single Python process with synchronous state management will crash under heavy load.

**The Scalability Architecture:**
1. **Decouple State:** Move the `state` dictionary out of Python memory and into a fast in-memory database like **Redis**. This allows multiple server instances to access the same session state.
2. **Asynchronous Queues:** Use a task queue like **Celery + RabbitMQ (or Redis)**. When a user submits a request, push it to the queue. A background worker picks it up, runs the agent loop, and streams the result back via WebSockets or SSE.
3. **Async I/O:** Python's `asyncio` (which we already use) can handle thousands of concurrent connections if the heavy lifting is offloaded to background workers.
</details>

<details>
<summary><b>9. Could you replace the LLM-based Task Decomposer with a traditional Python approach?</b></summary>
<br>

**The Insight:** Yes, absolutely. If the user's request maps to a known, deterministic workflow, an LLM is unnecessary.
*   **Deterministic Workflows:** You can define workflows as static configurations (e.g., `["search", "read", "summarize"]`). If the user asks for a "Report," just execute that list.
*   **When to use LLM:** The LLM Decomposer is only necessary for **open-ended, dynamic requests** where the exact sequence of tools cannot be predicted in advance.
</details>