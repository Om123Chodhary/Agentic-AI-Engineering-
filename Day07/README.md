# 📅 Day 07: Building the Agent's Brain (The Planner)

## 🎯 Objective
To transition our application from a reactive **AI Assistant** to an autonomous **AI Agent**. Up until Day 6, our Python code used hardcoded `if/else` statements to decide which tool to use. Today, we build an **AI Planner** (a separate LLM call) that acts as the "brain" to dynamically decide the best tool for a given user request, separating the decision-making from the execution.

---

## 🧠 Core Concepts Learned

### 1. Assistant vs. Agent (The Paradigm Shift)
*   **AI Assistant (Previous Days):** Follows instructions. It uses tools only when we explicitly write a Python `if` statement (e.g., `if "time" in question: use_time_tool()`). It is reactive.
*   **AI Agent (Today):** Makes its own decisions. The user gives a goal, and the Agent chooses the tools required to achieve that goal autonomously.
*   **The Key Difference:** An assistant *responds*, an agent *decides*.

### 2. Why `if/else` Fails
Imagine a user asks: *"How many days are left until New Year's Day?"* 
You cannot write an `if` statement for this. The agent needs to plan: `get_current_date()` ➡️ `calculate_difference()` ➡️ `generate_answer()`. Writing `if/else` for every possible combination of tools is impossible. Hence, we need an LLM to orchestrate the tools.

### 3. The Role of the Planner
The Planner is the brain of the agent. Its job is **NOT** to answer the user's question. Its job is to answer a completely different question: *"What should I do next?"*.
*   **Input:** User Request + List of Available Tools.
*   **Output:** The exact name of the tool to execute (or "None" if no tool is needed).

### 4. Separation of Responsibilities
This is the most important architectural pattern of modern AI Agents:
1.  **Planner (LLM):** Decides *what* to do.
2.  **Python Code:** Executes the chosen tool (because LLMs cannot execute code).
3.  **Assistant (LLM):** Takes the raw tool result and converts it into a natural, human-like response.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `tools.py` (The Capabilities)
Contains the actual Python functions the agent can use:
*   `get_current_time()`
*   `roll_dice()`
*   `generate_password(length)`

### 2. `planner.py` (The Decision Maker)
This file contains the `choose_tool(user_request)` function. 
*   It uses a specialized **System Prompt** that tells the LLM: *"You are an AI planner. Here are the available tools. If no tool is required, return None. Return ONLY the tool name."*
*   It acts as the first LLM call in our pipeline.

### 3. `assistant.py` (The Orchestrator)
This is the main loop of our application. Here is the exact flow:
1.  **Takes User Input.**
2.  **Calls `choose_tool()`:** Passes the user input to the planner.
3.  **Executes the Tool:** Uses `if/elif` to match the string returned by the planner to the actual Python function in `tools.py`. *(Note: The `if/elif` here is just for mapping the string to a function, the actual decision of WHICH tool to use was already made by the AI).*
4.  **Generates Natural Response:** Takes the raw result from the tool and the original user question, creates a prompt, and sends it to the LLM (second LLM call) to get a natural-sounding answer.

---

## 💻 Implementation Details

### The Planner Prompt (In `planner.py`)
```python
"""
You are an AI planner.
Available tools:
1. get_current_time - Use when the user asks for the current date or time.
2. roll_dice - Use when the user asks to roll a dice.
3. generate_password - Use when user wants a secure password.
If no tool required, return: None
Return ONLY the tool name
"""