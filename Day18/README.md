# 📅 Day 18: Capstone Project - The AI Research Agent

## 🎯 Objective
To build a complete, production-grade **AI Research Agent** from scratch without relying on heavy agent frameworks (like LangGraph or CrewAI). The agent takes a broad research topic, creates a plan, searches the web, reads articles, extracts structured notes, verifies the evidence using an LLM-as-a-Judge, and synthesizes a final research report.

---

## 🧠 Core Concepts Learned

### 1. The Agentic Workflow (Plan ➡️ Act ➡️ Verify)
Unlike simple chatbots, a Research Agent follows a strict loop:
*   **Planner:** Breaks the user's broad topic into a 3-5 step research plan.
*   **Agent Loop:** Uses tools (`search_web`, `read_webpage`) to gather information.
*   **Memory/State:** Saves findings into a structured notebook (`research_notes`).
*   **Verifier:** Uses a secondary LLM call to ensure the extracted evidence actually supports the finding (eliminating hallucinations).
*   **Synthesizer:** Converts verified notes into a professional Markdown report.

### 2. Code-Level Enforcement (State-Machine)
Small LLMs often get lazy and skip steps. We built strict Python guardrails using boolean flags (`search_done`, `read_done`, `note_added`, `pending_verification`). If the LLM tries to skip reading a page or verifying a note, the Python code intercepts it and forces it back on track.

### 3. LLM-as-a-Judge (Verification)
To prevent the agent from writing fake facts, we implemented an automated verifier. The verifier LLM receives the `source`, `finding`, and `evidence`. It returns a strict JSON response (`{"supported": true/false}`). If `true`, the note is marked as verified in our database.

### 4. Context Window & Token Optimization
*   **Text Truncation:** When scraping web pages, we limited the text to the first 12,000 characters to save tokens.
*   **Structured Notes:** Instead of keeping entire web pages in memory, we only kept concise findings and evidence.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `tools.py` (The Capabilities)
*   **`search_web(query)`**: Uses DuckDuckGo (via `webless` or custom scraper) to find relevant URLs. Strips out PDFs to avoid parsing errors.
*   **`read_webpage(url)`**: Uses `requests` and `BeautifulSoup` to extract readable text from HTML.
*   **`add_research_note()`**: Saves a structured finding (`source`, `finding`, `evidence`) into a global list with `verified: False`.
*   **`verify_finding()`**: Calls the LLM to act as a judge and check if the evidence supports the finding.
*   **`get_verified_research_notes()`**: Returns only the notes that passed verification.

### 2. `agent.py` (The Core Loop)
*   **`create_research_plan()`**: The first LLM call. Generates a numbered research plan.
*   **`research_agent()`**: The main `for` loop (max 6-8 steps). It dynamically calls the tools, handles state, and includes the **Enforcement Logic**.
*   **`generate_report()`**: The final LLM call. Takes the verified notes and synthesizes a professional report.

### 3. `main.py` (Execution & UI)
*   Connects to the MCP Server (if using Day 8/13 tools).
*   Takes the user's input, runs the agent loop, and prints the final report.

---

## 💼 Most Asked Interview Questions (Day 18)

<details>
<summary><b>1. Why did you build the Agent from scratch instead of using LangGraph or CrewAI?</b></summary>
<br>
To demonstrate a deep understanding of the underlying mechanics. Frameworks abstract away the state and loop management. By building it manually, I proved that I can handle complex state transitions, conditional routing, and API error handling using pure Python. Frameworks are easy to learn once you understand the core architecture.
</details>

<details>
<summary><b>2. What is "LLM-as-a-Judge" and how does it prevent hallucinations?</b></summary>
<br>
LLMs often generate plausible-sounding but false statements. "LLM-as-a-Judge" uses a secondary, independent LLM call to verify the primary agent's work. We prompt the judge to look at the raw evidence and the generated finding, and output a strict JSON boolean (`supported: true/false`). If false, we reject the finding.
</details>

<details>
<summary><b>3. How does the Python code handle a "lazy" LLM that skips steps?</b></summary>
<br>
We implement <b>Code-Level Enforcement</b>. We track the agent's progress with boolean flags (e.g., <code>search_done</code>, <code>read_done</code>). Before accepting a final answer, the Python code checks if all flags are true. If the LLM tries to finish without reading a webpage, the code injects a system message: <i>"You must read a webpage first"</i> and forces it to continue.
</details>

<details>
<summary><b>4. Why did you use DuckDuckGo instead of Google Search API?</b></summary>
<br>
Google Search API (Custom Search JSON API) requires a paid API key and has strict rate limits. DuckDuckGo provides a free, scraping-friendly HTML interface that is perfect for building cost-effective autonomous agents.
</details>

---

## 🔥 System Design & Architectural Insights (Senior Level)

<details>
<summary><b>1. You used a global Python list `research_notes` to store state. Why is this dangerous in production?</b></summary>
<br>
<b>The Multi-User Bug:</b> A global list is shared across all users. If User A and User B run research simultaneously, their notes will mix together, producing a garbage report.<br>
<b>The Production Fix:</b> We must use <b>Session-Based State Isolation</b>. Pass a unique `session_id` (UUID) with every request. Store notes in a dictionary: `{session_id: [notes]}`. Or better yet, use a persistent database like Redis or Postgres mapped to the user ID.
</details>

<details>
<summary><b>2. How do you handle a scenario where the user's input requires 20 tools to execute, but the `max_steps` is only 6?</b></summary>
<br>
The agent will hit the `max_steps` limit and fail to generate a complete report. To fix this, we need to implement <b>Recursive Summarization</b> or <b>Dynamic Re-planning</b>. The agent should be smart enough to realize it's running out of steps, summarize what it has, and ask the user to continue in the next turn (using the saved state/checkpoint).
</details>

<details>
<summary><b>3. Web scraping (BeautifulSoup) is slow and often gets blocked by anti-bot systems. How do you scale this?</b></summary>
<br>
<b>The Bottleneck:</b> Synchronous scraping blocks the event loop. Many sites return 403 Forbidden for standard Python requests.<br>
<b>The Production Fix:</b> 
1. Use <b>Playwright</b> or <b>Selenium</b> (headless browsers) to bypass bot detection.
2. Offload scraping to a background worker queue (like <b>Celery</b>) or use <code>asyncio.to_thread()</code> for concurrency.
3. Use paid APIs like <b>Tavily</b> or <b>Serper.dev</b> which handle bot protection and return clean JSON.
</details>

<details>
<summary><b>4. Explain how you would evaluate this Research Agent's performance.</b></summary>
<br>
You cannot evaluate it with simple unit tests (e.g., <code>assert output == "expected"</code>) because LLM outputs are non-deterministic. We need <b>Agent Evaluation Frameworks</b> (like Ragas or DeepEval) to measure:
<ul>
  <li><b>Faithfulness:</b> Is the report grounded in the retrieved facts (no hallucinations)?</li>
  <li><b>Answer Relevance:</b> Does the report actually answer the user's prompt?</li>
  <li><b>Tool Hit Rate:</b> Did the agent use the search tool when necessary?</li>
</ul>
</details>

## 🚀 Next Steps
In Day 19, we will transition from building manual tools to using **LangChain**, and see how it provides standard abstractions for models, tools, and memory.