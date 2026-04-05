# Nexus Memory Architecture: Tiered Memory Protocol

## L0 - Short-term (Session Memory)
- **Tool:** Redis / In-memory cache. 
- **Latency:** <10ms. 
- **Purpose:** Store the last few conversation turns and immediate state (e.g., current task ID).

## L1 - Working (Contextual Memory)
- **Tool:** ChromaDB / Pinecone. 
- **Mechanism:** Semantic search (Vectored retrieval). 
- **Purpose:** Recall relevant past discussions or documents related to the current task.

## L2 - Persistent (Episodic Memory)
- **Tool:** PostgreSQL / MongoDB. 
- **Mechanism:** Relational / Document search. 
- **Purpose:** Store facts, confirmed user preferences, and high-level summaries.
- **Why:** To avoid "vector hallucination" (Vektör tabanlarının kesin verilerdeki hataları).

## Smart Summarization Protocol
- **No Raw Logs:** Do not store raw conversation logs in the vector database.
- **Entity Extraction:** Extract meaning (e.g., "User prefers Python for data tasks") and store as persistent facts.
- **Temporal Tagging:** Every memory entry must have a timestamp to prevent stale advice.
