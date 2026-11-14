# 📅 Day 11: Persistent Memory & Semantic Retrieval

## 🎯 Objective
To solve the "Forgetfulness" problem of our Agent. Until Day 10, the agent's state was temporary (lost on program exit). Today, we implemented **Persistent Memory** using **SQLite** and **Vector Embeddings**. The agent can now remember user facts across different executions, retrieve relevant memories semantically, and filter out useless information using an LLM-based Memory Extractor.

---

## 🧠 Core Concepts Learned

### 1. State vs. Memory
*   **State (Temporary):** Represents what is happening *right now* (current step, current task, current observations). It lives in Python memory (RAM) and is destroyed when the program ends.
*   **Memory (Persistent):** Represents useful facts about the user (name, preferences, goals). It is stored in a database (SQLite) on the hard drive. It survives program restarts.

### 2. Why SQLite?
SQLite is a lightweight, file-based Relational Database Management System (RDBMS) that comes built-in with Python. Unlike PostgreSQL or MySQL, it doesn't require a separate server process. It is perfect for local AI agents.

### 3. Semantic Memory Retrieval
We don't want to retrieve *all* memories; we only want the ones relevant to the current question.
*   **Workflow:** User asks a question ➡️ Convert question to Embedding ➡️ Compare with all stored memory embeddings using **Cosine Similarity** ➡️ Return the top-K most similar memories above a certain threshold.

### 4. The Memory Extractor (LLM as a Filter)
Should we save every conversation to the database? No. If a user asks "What is the time?", saving that to permanent memory is useless.
*   **Solution:** We use an LLM (`memory_extractor.py`) to read the user-assistant conversation and decide: *"Is this a permanent fact about the user, or just temporary chatter?"* If it's a fact, it returns a summarized string. If not, it returns `None`.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `memory.py` (The Memory Manager)
*   **`create_database()`**: Creates a SQLite database file (`memory.db`) with a table named `memories`. It contains columns: `id`, `user_message`, `assistant_message`, `embedding` (stored as JSON string), and `created_at`.
*   **`save_memory()`**: Generates the embedding for a conversation and inserts it into the database. Uses `?` placeholders in SQL to prevent **SQL Injection**.
*   **`search_semantic_memories()`**: Takes a query, generates its embedding, fetches all rows from SQLite, calculates cosine similarity for each, filters by `threshold`, sorts by score, and returns the `top_k` results.

### 2. `memory_extractor.py` (The Filter)
*   **`extract_memory(user_message, assistant_message)`**: Asks the LLM: *"Does this conversation contain long-term useful information (preferences, skills, facts)? If yes, return the fact. If no, return None."*

### 3. `state.py` (Updated)
*   Added `memories: []` to the state dictionary.
*   Added `add_memory(state, memory)` function to append retrieved memories to the state.

### 4. `loop.py` (The Agent Loop - Updated)
*   **Memory Retrieval:** At the very beginning of the loop, before task decomposition, it calls `search_semantic_memories()` and adds the results to the state.
*   **Memory Saving:** At the end (when `FINISH` is reached), it calls `save_memory()` to save the conversation.
*   *(Optional)* Calls `extract_memory()` to save a condensed semantic fact if applicable.

### 5. `planner.py` & `answer.py` (Updated Prompts)
*   The `planner` now receives the `state["memories"]` and uses them to decide the next action.
*   The `answer` prompt now includes the `state["memories"]` and instructs the LLM: *"Use relevant previous memories when answering."*

### 6. `task_planner.py` (Updated Prompts)
*   Added a **Critical Rule**: If the user request is a greeting, casual conversation, a personal introduction ("My name is X"), or a general knowledge question, **do not decompose it into tasks** (return `NONE`). This prevents the agent from breaking into an infinite loop when having a normal conversation.

---

## 💼 Most Asked Interview Questions (Day 11)

<details>
<summary><b>1. What is the difference between State and Memory in your AI Agent?</b></summary>
<br>
State is the short-term working memory for the *current* execution (tracking tasks, actions, and observations). It is volatile and stored in Python RAM. Memory is the long-term storage of facts and previous conversations. It is persistent, stored in SQLite, and survives program restarts.
</details>

<details>
<summary><b>2. How does Semantic Search work in your memory module?</b></summary>
<br>
When a user asks a question, we convert the text into a vector embedding using <code>nomic-embed-text</code>. We then retrieve all stored memory embeddings from SQLite and calculate the **Cosine Similarity** between the query embedding and each stored embedding. We sort the results by the highest score and return only the top-K results that cross a minimum threshold.
</details>

<details>
<summary><b>3. Why did you use a separate LLM call (Memory Extractor) instead of saving everything to the database?</b></summary>
<br>
Saving every conversation (e.g., "What is the time?", "Roll a dice") pollutes the memory with useless data. The Memory Extractor acts as a filter. It reads the conversation and only outputs a summarized "fact" if it's useful (e.g., "The user is learning MCP"). This keeps the database clean and ensures retrieval is highly relevant.
</details>

<details>
<summary><b>4. How do you prevent SQL Injection in your SQLite implementation?</b></summary>
<br>
Instead of using Python's f-strings to directly insert variables into the SQL query (which is dangerous), I use parameterized queries with <code>?</code> placeholders. The values are passed as a separate tuple: <code>cursor.execute("INSERT INTO memories VALUES (?, ?, ?)", (val1, val2, val3))</code>. SQLite automatically escapes these values, preventing injection attacks.
</details>

<details>
<summary><b>5. What is the purpose of the "Critical Rule" added to the task planner?</b></summary>
<br>
In Day 10, if a user said "Hello" or "My name is X", the Task Decomposer would still try to break it into tasks (like "Acknowledge user"). This confused the Planner. On Day 11, we added a rule: <i>"If the request is a greeting, introduction, or memory-based question, return NONE."</i> This allows the agent to handle casual conversations gracefully without trying to execute tools.
</details>

---

## 🧠 System Design & Architectural Insights (Senior Level)

<details>
<summary><b>1. How do you handle context window limitations when retrieving memories?</b></summary>
<br>
If a user has 10,000 memories, we cannot inject all of them into the LLM prompt. That is exactly why we use **Semantic Search + Top-K**. We only fetch the top 3-5 most relevant memories. If the history is very large, we also use a <b>Memory Summarizer</b> (an LLM that condenses old memories into a shorter paragraph) before saving it to the database.
</details>

<details>
<summary><b>2. What happens if the Embedding Model changes? All previous embeddings in the database become invalid.</b></summary>
<br>
This is a real production problem called **Embedding Drift**. If we change from <code>nomic-embed-text</code> to OpenAI's <code>text-embedding-3-small</code>, the vector space changes entirely. The old vectors become useless. In production, we would need to run a background migration script to re-embed all historical memories using the new model.
</details>

<details>
<summary><b>3. This implementation uses SQLite and fetches ALL rows to calculate cosine similarity. How does this scale?</b></summary>
<br>
It doesn't scale beyond a few thousand rows. SQLite doesn't have native vector support. To scale, we must use a **Vector Database** (like FAISS, Pinecone, or ChromaDB). A Vector DB indexes embeddings using algorithms like HNSW (Hierarchical Navigable Small World), allowing it to find the nearest neighbors in milliseconds even across millions of vectors.
</details>

<details>
<summary><b>4. How do you handle conflicting memories? (e.g., User says "I live in Delhi" today, but last year said "I live in Mumbai.")</b></summary>
<br>
This requires a **Memory Update Strategy**. We can't just blindly append. Options include:
<ul>
  <li><b>Timestamp Prioritization:</b> The planner LLM is instructed to prioritize the memory with the most recent <code>created_at</code> timestamp.</li>
  <li><b>Fact Overwrite:</b> During the Memory Extraction phase, we search for existing similar memories. If a contradiction is found, we DELETE the old memory and INSERT the new one.</li>
</ul>
</details>

## 🚀 Next Steps
In Day 12, we will improve our Retrieval-Augmented Generation (RAG) system by introducing **Re-ranking** and chunking strategies, ensuring the agent finds the most accurate information from large documents.