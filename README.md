<div align="center">

# 🚀 Agentic AI Engineering: The 22-Day Production Mastery

**From building basic chatbots to deploying production-ready autonomous agents.**

[![Total Hours](https://img.shields.io/badge/Hours_Invested-800%2B-blueviolet?style=for-the-badge)]()
[![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)]()

*"Frameworks are just abstractions. If you don't understand the architecture underneath, you cannot build production-grade systems."*

</div>

---

## 📖 The Story Behind This Repository

Over the last few months, I dedicated **800+ hours** to an intensive, self-driven deep dive into Agentic AI Engineering. 

Instead of just copy-pasting tutorials using frameworks like LangChain or CrewAI, I started from absolute zero. I built multi-agent systems using pure Python `while` loops, manually managed state, handled API rate limits with custom fallbacks, and eventually transitioned into industry-standard frameworks.

**This repository is not a collection of certificates. It is a structured, day-by-day proof of work, building an entire ecosystem from scratch to a live, Dockerized cloud application.**

---

## 🏗️ The 4 Pillars of this Journey

Throughout these 22 days, every line of code was written with 4 core engineering principles in mind:
1.  **Architecture First:** Understanding state management, loops, and tool calling before using frameworks.
2.  **Production Reliability:** Implementing Timeouts, Retries, Multi-Key API Fallbacks, and Session Isolation.
3.  **Security:** Protecting against Prompt Injection, Path Traversal, and securing environment variables.
4.  **User Experience:** Using Server-Sent Events (SSE) to stream real-time agent thoughts to the frontend.

---

## 🗺️ The 22-Day Detailed Roadmap

Here is the breakdown of the 22-day curriculum I followed and implemented. Every folder contains the code and a detailed `README.md` explaining the concepts.

### 🏗️ Phase 1: The Foundation (Day 1 - 5)
*Building the core capabilities of LLMs.*
*   **Day 1: First AI Chatbot** – Local LLM setup using Ollama.
*   **Day 2: Conversation Memory** – Managing chat history to make LLMs stateful.
*   **Day 3: Multi-Role Assistant** – Using System Prompts to give agents personalities.
*   **Day 4: Tool Calling** – Teaching the LLM to use external capabilities (calculators, time, etc.).
*   **Day 5: Document AI** – Reading and summarizing local text files.

### 🧠 Phase 2: RAG & MCP (Day 6 - 8)
*Connecting LLMs to the outside world.*
*   **Day 6: Basic RAG** – Document chunking, embeddings (Ollama), and Cosine Similarity from scratch.
*   **Day 7: The AI Planner** – Moving from hardcoded `if/else` to LLM-based decision routing.
*   **Day 8: MCP (Model Context Protocol)** – Building a custom MCP Server and Client using `FastMCP`.

### 🔄 Phase 3: The Agent Loop & Memory (Day 9 - 11)
*Making the agent autonomous.*
*   **Day 9: The Agent Loop** – Building the `Think ➡️ Act ➡️ Observe` cycle. Implementing `max_steps` to prevent infinite loops.
*   **Day 10: Task Decomposition** – Breaking large goals into smaller tasks. Implementing Dynamic Re-planning.
*   **Day 11: Persistent Memory** – Upgrading from a Python list to a **SQLite** database. Semantic memory retrieval for multi-session chats.

### 🕸️ Phase 4: Advanced RAG & Multi-Agent (Day 12 - 14)
*Scaling up the complexity.*
*   **Day 12: Advanced RAG** – Building a production pipeline with **ChromaDB**, Hybrid Search (Keyword + Semantic), and LLM Re-ranking.
*   **Day 13: Advanced MCP Ecosystem** – Multi-Server Registry, Tool Arguments, and Remote HTTP transport.
*   **Day 14: Multi-Agent Architecture** – Building a custom Manager + Workers (Researcher, Coder, Reviewer) system.

### 🛡️ Phase 5: The Frameworks (Day 15 - 17)
*Learning industry-standard tools.*
*   **Day 15: Production Engineering** – Retry logic, Observability (Logging), and Security (RBAC, Path Traversal).
*   **Day 16: LangGraph** – Converting the manual loops into a StateGraph with Checkpointing and Human-in-the-Loop (Interrupts).
*   **Day 17: CrewAI** – Role-based multi-agent orchestration. Integrating MCP via the Adapter Pattern.

### 🏆 Phase 6: The Capstone & Deployment (Day 18 - 22)
*From code to a live product.*
*   **Day 18: The Research Agent (From Scratch)** – Building a complex agent with Planning, Tool Execution, and LLM-as-a-Judge Verification.
*   **Day 19: LangChain Mastery** – LCEL (Pipe operators), `@tool` decorators, AgentExecutor, and Agentic RAG.
*   **Day 20: Productionizing** – FastAPI integration, Pydantic validation, Health Checks, and Docker.
*   **Day 21: Local Full-Stack** – Serving a static frontend, SSE Streaming, and `asyncio.to_thread`.
*   **Day 22: Enterprise Deployment** – Groq API Fallbacks, Session Isolation (UUID), Docker Compose, and Render deployment.

---

## 🌟 The Final Capstone: Autonomous AI Research Agent

<div align="center">

[![Live Demo](https://img.shields.io/badge/Live_Demo-Click_Here-brightgreen?style=for-the-badge&logo=render)](https://autonomous-ai-research-agent-r3s9.onrender.com/)

</div>

The culmination of this 22-day journey is a production-grade Research Agent. 
*   **The Workflow:** User Query ➡️ Planner ➡️ State-Machine Enforcement ➡️ Web Search/Scrape ➡️ LLM-as-a-Judge Verification ➡️ Final Report.
*   **The Tech Stack:** FastAPI, Groq (Llama 3), ChromaDB, Docker, Server-Sent Events (SSE), Vanilla JS.

> **Why it stands out:** Instead of using an off-the-shelf framework, the core agent loop was built from scratch. This allowed the implementation of **Python-level guardrails** (`search_done`, `read_done`) to physically force the LLM to follow a strict workflow and prevent hallucination.

---

## 🛠️ Master Skills Matrix

By completing this journey, I have hands-on experience with:

| Category | Technologies & Concepts |
| :--- | :--- |
| **LLM Providers** | Ollama (Local), Groq (Cloud), Gemini, OpenAI SDK |
| **Frameworks** | LangChain, LangGraph, CrewAI, FastMCP |
| **Backend & APIs** | FastAPI, Pydantic, Uvicorn, Server-Sent Events (SSE) |
| **Databases & RAG** | SQLite, ChromaDB, FAISS, Vector Embeddings, Hybrid Search |
| **DevOps** | Docker, Docker Compose, Render, Git, Environment Variables |
| **Core Engineering** | State Machines, Async/Await (`asyncio`), Multi-Threading, API Fallbacks |

---

## 🧑‍💻 About the Author

**Oma Ram**
*B.S. Applied AI & Data Science @ IIT Jodhpur*

I am a builder who believes that true learning happens when you step away from tutorials and start debugging real-world failures. Building this ecosystem taught me how to handle API crashes, prevent data leaks between users, and optimize LLM context windows. 

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Om123Chodhary)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/oma-ram-choudhary-07532024a/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:omaramchoudhary418@gmail.com)

---
<div align="center">
  <i>"Building with curiosity. Learning through experimentation. Solving problems with AI."</i>
</div>
