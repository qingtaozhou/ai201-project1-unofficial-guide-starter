# Prompt for AI Tool: Embedding & Retrieval Code Generation

## Context

You are helping build an Unofficial Guide to Georgia Tech graduate CS/ML courses. Milestone 3 already produced `chunks.json`, a list of chunk dictionaries with `text`, `chunk_id`, `source_file`, `document_sequence`, `start_char`, `end_char`, course metadata, and source metadata.

## Retrieval Approach From planning.md

- Embedding model: `all-MiniLM-L6-v2` via `sentence-transformers`
- Top-k: 5 chunks per query
- Rationale: MiniLM is fast, local, and suitable for technical/educational course-review text. Top-5 balances coverage with not diluting context too much.

## Pipeline Diagram

```text
Document Ingestion (Python File I/O)
          ↓
Chunking (600 char chunks, 100 char overlap)
          ↓
Embedding (sentence-transformers all-MiniLM-L6-v2)
          ↓
Vector Store (ChromaDB)
          ↓
Retrieval (Top-5 similarity search)
          ↓
Generation (Groq LLM mixtral-8x7b)
          ↓
Response (with source citations)
```

## Task

Implement the embedding and retrieval stage:

1. Load chunks from `chunks.json`.
2. Load `SentenceTransformer("all-MiniLM-L6-v2")`.
3. Embed every chunk's `text`.
4. Store each embedding in ChromaDB with metadata:
   - source document filename
   - chunk id
   - document sequence
   - start and end character positions
   - course codes
   - professor, source, and date when available
5. Write a retrieval function that accepts a query string and returns the top-k most relevant chunks with source metadata and distance scores.
6. Include a CLI test path that runs at least three evaluation queries and prints retrieved chunks and distances.

## ChromaDB API Pattern To Explain

Use `chromadb.PersistentClient(path="chroma_db")` so the vector store is saved locally. Use `get_or_create_collection()` for reusable collections. Use `collection.add(ids=..., documents=..., embeddings=..., metadatas=...)` to insert chunks, and `collection.query(query_embeddings=..., n_results=k, include=["documents", "metadatas", "distances"])` to retrieve nearest neighbors.
