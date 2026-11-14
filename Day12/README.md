# 📅 Day 12: Advanced RAG (Chunking, Hybrid Search & Re-ranking)

## 🎯 Objective
To upgrade our basic Day 6 RAG system into a production-grade **Advanced RAG** pipeline. Instead of embedding entire documents, we learned how to chunk documents, store them in a persistent Vector Database (**ChromaDB**), use **Hybrid Search** (combining semantic and keyword matching), and apply **Re-ranking** using an LLM to find the most accurate context for the user.

---

## 🧠 Core Concepts Learned

### 1. Chunking & Overlap
*   **Why Chunk?** Sending a 20-page document to an LLM is expensive and exceeds the context window. We break the document into smaller pieces (chunks) of fixed word counts (e.g., 200 words).
*   **Why Overlap?** If we split exactly at 200 words, we might cut a sentence in half, losing context. We add an overlap (e.g., 50 words) so the end of Chunk 1 is repeated at the start of Chunk 2.
*   **Rule of Thumb:** Overlap should be meaningful (10-20% of chunk size) but not excessive, otherwise, it defeats the purpose of chunking.

### 2. Metadata
Every chunk is stored with metadata: `source` (filename) and `chunk_id`. This is crucial for debugging and filtering (e.g., "Only search within `python.txt`").

### 3. Vector Databases (FAISS vs ChromaDB)
*   **FAISS:** A low-level library for fast vector indexing. Great for raw speed, but lacks database features.
*   **ChromaDB:** A complete, developer-friendly vector database. It handles embeddings, metadata, and persistence (saving to disk) out of the box.

### 4. The Three Types of Search
*   **Semantic Search:** Uses Cosine Similarity on embeddings. Great for understanding *meaning* (e.g., "car" matches "automobile").
*   **Keyword Search:** Exact word matching. Great for specific technical terms, IDs, or rare words (e.g., "generate_password").
*   **Hybrid Search:** Combines both! We calculate a weighted score: `(0.7 * Semantic_Score) + (0.3 * Keyword_Score)`.

### 5. Re-ranking (The Two-Stage Retrieval)
*   **Stage 1 (Retrieval):** Hybrid search quickly fetches the top 5-10 candidate chunks. It's fast but not perfectly accurate.
*   **Stage 2 (Re-ranking):** We pass the query and each candidate chunk to an LLM (or a specialized re-ranker model). The LLM gives a relevance score (0-100) for each. We re-sort the chunks based on this new score and keep only the top 3.

---

## 🏗️ Code Architecture (File by File Breakdown)

### 1. `chunker.py`
*   **`create_chunks()`**: Splits text into a list of words, then creates overlapping chunks using a `while` loop. Returns a list of dictionaries (`text`, `source`, `chunk_id`).

### 2. `embedding.py`
*   **`embed_chunks()`**: Takes the chunks, generates embeddings for each using Ollama (`nomic-embed-text`), and appends the `embedding` array to each chunk's dictionary.

### 3. `chroma_store.py` (The Database)
*   **`add_chunks()`**: Extracts the text, embeddings, IDs, and metadata from the chunks and uses `collection.upsert()` to store them persistently in ChromaDB.
*   **`search()`**: Takes a query embedding and returns the top-K nearest neighbors using `collection.query()`.

### 4. `retriever.py` (The Search Logic)
*   **`keyword_score()`**: Uses Python `set` intersection to calculate the percentage of query words that exactly match the text.
*   **`hybrid_search()`**: Combines semantic score (from cosine similarity) and keyword score using weighted averages.

### 5. `reranker.py` (The Refiner)
*   **`rerank()`**: Loops through the candidates from hybrid search. Prompts the LLM to rate the relevance of the candidate to the query (0-100). Sorts them and returns the top 3.

### 6. `advance_rag.py` (The Orchestrator)
*   **`build_rag()`**: Chunks -> Embeds -> Stores in ChromaDB.
*   **`retrieve()`**: Embeds query -> ChromaDB Search -> Calculates Hybrid Score -> Sorts -> Re-ranks -> Returns top 3.

---

## 💼 Most Asked Interview Questions (Day 12)

<details>
<summary><b>1. What is the difference between Semantic Search and Keyword Search? Why do we need Hybrid Search?</b></summary>
<br>
Semantic search understands <i>meaning</i> (e.g., "coding" matches "programming"), but fails on exact identifiers (e.g., "error_code_404"). Keyword search matches exact words but fails on synonyms. <b>Hybrid Search</b> combines both by calculating a weighted score, ensuring we capture both conceptual meaning and exact technical terms.
</details>

<details>
<summary><b>2. Why is Chunking necessary? What is "Chunk Overlap"?</b></summary>
<br>
Chunking breaks large documents into smaller pieces so they fit into the LLM's context window and don't dilute the embedding's meaning. <b>Overlap</b> ensures that sentences at the boundary of a chunk are not cut in half. We repeat a small portion (e.g., 50 words) at the start of the next chunk to preserve context.
</details>

<details>
<summary><b>3. What is Re-ranking and why is it used?</b></summary>
<br>
Re-ranking is a second-stage filtering process. The initial retrieval (Hybrid Search) fetches candidates quickly but might rank a slightly irrelevant chunk higher. The Re-ranker uses a heavier model (like an LLM) to deeply evaluate the exact relevance of each chunk to the query, ensuring only the absolute best context is sent to the final generator LLM.
</details>

<details>
<summary><b>4. Why did you choose ChromaDB over FAISS?</b></summary>
<br>
FAISS is a low-level indexing library—it's fast but requires manual management of metadata and persistence. <b>ChromaDB</b> provides a complete database abstraction (like SQL) for vector data. It handles metadata filtering, persistent storage (saving to disk), and document collection management out of the box, making it much faster to build production applications.
</details>

<details>
<summary><b>5. How do you evaluate if your RAG system is working well?</b></summary>
<br>
You cannot evaluate RAG just by looking at the final answer. You must evaluate the <b>Retrieval</b> phase. We create an evaluation dataset where we manually know the "Expected Chunk ID" for a query. We then run our retriever and check if the expected chunk is present in the top-K results (Hit Rate). If it's not, the retrieval failed, even if the LLM hallucinated a correct answer.
</details>

---

## 🔥 System Design & Architectural Insights (Senior Level)

<details>
<summary><b>1. How do you choose the optimal Chunk Size and Overlap?</b></summary>
<br>
There is no "one size fits all" answer. It is an empirical trade-off:
<ul>
  <li><b>Too small:</b> Chunks lose context, and the LLM gets fragmented information.</li>
  <li><b>Too large:</b> The embedding vector represents too many topics, making semantic search inaccurate.</li>
  <li><b>How to tune:</b> We must build an evaluation pipeline (e.g., using Ragas or custom hit-rate scripts) and test combinations (e.g., 200/50 vs. 300/100) against a golden dataset of queries.</li>
</ul>
</details>

<details>
<summary><b>2. Your Re-ranker uses an LLM to score each candidate (0-100). What is the scalability issue here?</b></summary>
<br>
This is a massive bottleneck. If you retrieve 20 candidates, you have to make <b>20 separate LLM calls</b> just for re-ranking. This adds latency (could take 10+ seconds) and high API costs. <b>Production Fix:</b> Use dedicated Cross-Encoder models (like Cohere Rerank or BGE-Reranker) which can score all 20 candidates in a single forward pass (or use a batched LLM request).
</details>

<details>
<summary><b>3. What happens if the Embedding Model changes (e.g., from nomic-embed to OpenAI)?</b></summary>
<br>
This is called <b>Embedding Drift</b>. If the document embeddings were created with Model A, but the user query is embedded with Model B, the vector spaces are incompatible. The similarity search will return garbage. <b>Fix:</b> The golden rule of RAG is that the document embedder and query embedder MUST be the exact same model. If you change the model, you must re-embed the entire database from scratch.
</details>

<details>
<summary><b>4. How does ChromaDB perform under heavy load (millions of chunks)?</b></summary>
<br>
ChromaDB is great for local development and small-to-medium apps. However, for millions of vectors, it lacks distributed indexing and horizontal scaling. In an enterprise environment, you would migrate to a distributed Vector DB like <b>Milvus, Pinecone, or Qdrant</b>, which use advanced algorithms like HNSW (Hierarchical Navigable Small World) to keep search times under 50ms.
</details>

<details>
<summary><b>5. Explain the concept of Metadata Filtering in Vector Databases.</b></summary>
<br>
Metadata filtering allows you to pre-filter the search space before vector similarity is calculated. For example, if a user asks a question, you can instruct ChromaDB: <code>where={"source": "python.txt"}</code>. ChromaDB will only calculate cosine similarity for chunks that belong to <code>python.txt</code>. This significantly improves speed and accuracy by preventing cross-document hallucinations.
</details>

## 🚀 Next Steps
In Day 13, we will go deeper into **MCP (Model Context Protocol)** and move beyond a single local server, exploring advanced tool integration for AI Agents.