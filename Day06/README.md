# 📅 Day 06: Building RAG (Retrieval-Augmented Generation) From Scratch

## 🎯 Objective
To understand the fundamental problem of Context Windows in LLMs and build an end-to-end **Retrieval-Augmented Generation (RAG)** system purely in Python, without relying on heavy frameworks like LangChain. We evolved our retrieval system from basic keyword matching to advanced semantic search using Vector Embeddings.

---

## 🧠 Core Concepts Learned

### 1. The "Too Much Data" Problem
In Day 5, our AI could read a single document. But in the real world, a company might have 10,000+ documents. 
*   **Why can't we just send everything to the LLM?**
    *   It's too slow.
    *   It's too expensive (API costs).
    *   It exceeds the LLM's Context Window (token limit).
*   **The Solution:** **RAG (Retrieval-Augmented Generation)**. We retrieve only the *relevant* pieces of information and send them to the LLM to generate the answer.

### 2. RAG Workflow (The Big Picture)
`User Question` ➡️ `Find Relevant Info (Retriever)` ➡️ `Send ONLY relevant info to LLM` ➡️ `Generate Final Answer`.

### 3. Evolution of Retrievers
*   **V1: Keyword Search (Naive Approach):** Matching exact words. (e.g., If a user searches "coding language" but the document says "programming language", it fails).
*   **V2: Semantic Search (The Pro Approach):** Understanding the *meaning* behind the words.

### 4. Embeddings & Vector Search
*   **What is an Embedding?** Converting text into a list of numbers (Vectors). Text with similar meanings will have similar numerical vectors.
*   **Model Used:** `nomic-embed-text` via Ollama (Creates 768-dimensional vectors).
*   **Similarity Score:** **Cosine Similarity** is used to measure the angle between two vectors. 
    *   Score `1.0` = Identical meaning.
    *   Score `0.0` = Unrelated.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `knowledge/` Directory (The Knowledge Base)
We created a folder with 4 text files: `python.txt`, `mysql.txt`, `machine_learning.txt`, and `weather.txt`. This acts as our custom, external database.

### 2. `retriever.py` (Loading & Basic Retrieval)
*   **`load_documents()`**: Uses `pathlib` to scan the `knowledge/` folder, read all `.txt` files, and store them in a Python dictionary `{filename: content}`.
*   **`retrieve(question)`**: A basic keyword search. It checks if the exact question string exists in the document's content. (Limitation: Fails on synonyms).

### 3. `similarity.py` (The Math)
*   **`cosine_similarity(vec1, vec2)`**: Uses `numpy` to calculate the dot product of two vectors divided by the product of their magnitudes. This gives us the semantic similarity score.

### 4. `embedding.py` (The Vector Converter)
*   **`create_embedding(content)`**: Initializes the OpenAI client (pointing to Ollama's local server) and calls `client.embeddings.create()` using the `nomic-embed-text` model. It extracts and returns the 768-dimension vector list.

### 5. `Rag.py` (The Main Orchestrator)
This is the heart of the application:
1.  Loads all documents.
2.  Pre-computes embeddings for all documents (to save time in the loop).
3.  Takes user input.
4.  Creates an embedding for the user's question.
5.  Loops through all document embeddings, calculating the Cosine Similarity.
6.  Finds the `best_score` and `best_document`.
7.  Retrieves the content of the best document (The Context).
8.  Builds a Prompt: *"Answer the question using only the following information. context: {context} question: {user_input}"*
9.  Sends the prompt to the LLM (Ollama) and prints the response.

---

## ⚠️ Limitations of our V1 RAG System
Instructor highlighted what we are still missing (which will be solved in future days):
1.  **Returns only ONE document:** What if the answer is spread across 3 documents?
2.  **Embeds the entire document:** If a document is 200 pages, the embedding becomes useless because the vector represents the *average* meaning of the whole book, not specific chapters.
3.  **No Persistence:** It rebuilds embeddings every time the script starts. (In production, we use Vector Databases like FAISS/ChromaDB).
4.  **No Chunking:** We don't split large texts into smaller paragraphs.

---

## 💼 Interview Takeaways
*   **How does RAG work?** It solves the LLM context limit problem by retrieving relevant data externally and augmenting the prompt.
*   **Keyword Search vs Semantic Search:** Keyword search looks for exact string matches, while semantic search uses embeddings to understand the conceptual meaning (e.g., "car" and "automobile" are close in vector space).
*   **What is Cosine Similarity?** A mathematical metric to measure how similar two vectors are, used to find the best matching document for a user's query.

## 🚀 Next Steps
Move from local `.txt` files and naive loops to **Advanced RAG** using Text Splitters (Chunking) and Vector Databases (FAISS).