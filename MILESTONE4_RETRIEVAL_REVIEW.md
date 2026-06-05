# Milestone 4 Embedding And Retrieval Review

## AI Prompt Used

The prompt used for the AI tool is saved in `PROMPT_FOR_AI_MILESTONE4.md`. It included the Retrieval Approach from `planning.md`, the full pipeline diagram, and a request to implement embedding with `SentenceTransformer("all-MiniLM-L6-v2")`, storage in ChromaDB, and a top-k retrieval function.

## Code Generated

- `embed_retrieve.py` loads `chunks.json`, embeds chunk text with `all-MiniLM-L6-v2`, stores embeddings in a persistent ChromaDB collection, and retrieves top-k chunks with source metadata and distance scores.

## ChromaDB API Explanation

- `chromadb.PersistentClient(path="chroma_db")`: opens a local persistent Chroma database stored on disk instead of an in-memory database.
- `get_or_create_collection(...)`: returns an existing named collection if it exists, or creates it if it does not.
- `collection.add(...)`: inserts ids, original chunk text, vector embeddings, and metadata into the collection.
- `collection.query(...)`: searches the collection using a query embedding and returns nearest chunks. The code requests `documents`, `metadatas`, and `distances` so retrieval can be inspected and cited later.

## Review Notes

The generated code matches the planned architecture: chunk loading -> MiniLM embedding -> ChromaDB vector store -> top-5 retrieval. Metadata is stored with each chunk, including source filename, chunk id, document sequence, character position, course codes, professor, source, and date.

One correction was made while writing the code: ChromaDB metadata values must be scalar types, so the chunk's `course_codes` list is converted to a comma-separated string before storage.

## Retrieval Test Results

Tested three evaluation-plan queries with top-k = 5:

1. CS 7641 industry-track value: relevant results from the 7641 vs 6340 blog, course comparison thread, and CS 7641 exam tips. Distances were mostly 0.39-0.47.
2. CS 7641 vs CS 6340: strong results from the comparison blog and Discord/course-comparison sources. Distances were mostly 0.30-0.55.
3. CS 6505 exam recovery: initial 300-character chunks retrieved the right source but missed some recovery advice in the top 5. Increasing chunks to 600 characters with 100-character overlap brought the instructor response and "bombed exam 1" recovery advice into the top 5.

The retrieval function also now fetches a wider candidate set and prioritizes chunks whose metadata matches an explicit course code in the query, so a query naming `CS 6505` is less likely to be diluted by semantically similar `CS 7641` exam-prep chunks.
