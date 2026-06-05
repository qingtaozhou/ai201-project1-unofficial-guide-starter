"""Embedding and retrieval pipeline using SentenceTransformers and ChromaDB."""

from pathlib import Path
import argparse
import json
import re

import chromadb
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"
CHUNKS_PATH = "chunks.json"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "gt_course_guide_chunks"
DEFAULT_TOP_K = 4
COURSE_CODE_RE = re.compile(r"\b(?:CS|MGT)\s*-?\s*\d{4}\b", re.IGNORECASE)


def load_chunks(chunks_path=CHUNKS_PATH):
    """Load chunk dictionaries produced by the Milestone 3 chunking pipeline."""
    path = Path(chunks_path)
    if not path.exists():
        raise FileNotFoundError(
            f"{chunks_path} not found. Run `python3 chunk.py --output chunks.json` first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_embedding_model(model_name=MODEL_NAME):
    """Load the local sentence-transformers embedding model."""
    try:
        return SentenceTransformer(model_name, local_files_only=True)
    except Exception:
        return SentenceTransformer(model_name)


def normalize_course_code(course_code):
    """Normalize course-code spellings like 'CS 6505' and 'cs-6505'."""
    return re.sub(r"[\s-]+", "", course_code).upper()


def query_course_codes(query):
    """Extract explicit course codes from a user query."""
    return {normalize_course_code(match.group(0)) for match in COURSE_CODE_RE.finditer(query)}


def metadata_course_codes(metadata):
    """Return normalized course codes stored on a Chroma metadata row."""
    course_codes = metadata.get("course_codes", "")
    return {
        normalize_course_code(course_code)
        for course_code in course_codes.split(",")
        if course_code.strip()
    }


def chunk_to_metadata(chunk):
    """Convert chunk metadata to Chroma-compatible scalar values."""
    course_codes = chunk.get("course_codes") or []
    if isinstance(course_codes, list):
        course_codes = ", ".join(course_codes)

    return {
        "source_file": chunk.get("source_file", ""),
        "source_path": chunk.get("source_path", ""),
        "chunk_id": chunk.get("chunk_id", ""),
        "document_sequence": int(chunk.get("document_sequence", 0)),
        "start_char": int(chunk.get("start_char", 0)),
        "end_char": int(chunk.get("end_char", 0)),
        "course_codes": course_codes,
        "professor": chunk.get("professor") or "",
        "source": chunk.get("source") or "",
        "date": chunk.get("date") or "",
    }


def get_collection(chroma_path=CHROMA_PATH, collection_name=COLLECTION_NAME):
    """Open or create the persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path=chroma_path)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def rebuild_collection(chunks_path=CHUNKS_PATH, chroma_path=CHROMA_PATH):
    """Embed all chunks and rebuild the ChromaDB collection from scratch."""
    chunks = load_chunks(chunks_path)
    model = load_embedding_model()

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    ids = [chunk["chunk_id"] for chunk in chunks]
    metadatas = [chunk_to_metadata(chunk) for chunk in chunks]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return collection, len(chunks)


def retrieve(query, top_k=DEFAULT_TOP_K, chroma_path=CHROMA_PATH):
    """Return the top-k most relevant chunks for a query with source metadata."""
    model = load_embedding_model()
    collection = get_collection(chroma_path=chroma_path)
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()[0]
    requested_course_codes = query_course_codes(query)
    candidate_count = max(top_k, top_k * 4) if requested_course_codes else top_k

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_count,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    for doc, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append(
            {
                "text": doc,
                "metadata": metadata,
                "distance": distance,
            }
        )

    if requested_course_codes:
        retrieved.sort(
            key=lambda result: (
                not bool(requested_course_codes & metadata_course_codes(result["metadata"])),
                result["distance"],
            )
        )
    return retrieved[:top_k]


def print_results(query, results):
    """Print retrieval results in a compact inspection format."""
    print(f"\n=== Query: {query} ===")
    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]
        print(f"\n[{index}] distance={result['distance']:.4f}")
        print(
            f"source={metadata.get('source_file')} "
            f"chunk={metadata.get('chunk_id')} "
            f"chars={metadata.get('start_char')}-{metadata.get('end_char')} "
            f"courses={metadata.get('course_codes')}"
        )
        print(result["text"])


def run_evaluation_queries(top_k=DEFAULT_TOP_K, chroma_path=CHROMA_PATH):
    """Run three planning.md evaluation queries and print retrieval results."""
    queries = [
        "Is CS 7641 Machine Learning worth taking if I'm on an industry track, and what should I expect?",
        "What's the difference between CS 7641 and CS 6340, and which should I take first?",
        "How do I recover if I bomb the first exam in CS 6505 Algorithms?",
    ]
    for query in queries:
        print_results(query, retrieve(query, top_k=top_k, chroma_path=chroma_path))


def main():
    """CLI entrypoint for building the index and testing retrieval."""
    parser = argparse.ArgumentParser(description="Embed chunks and query ChromaDB.")
    parser.add_argument("--chunks", default=CHUNKS_PATH)
    parser.add_argument("--chroma-path", default=CHROMA_PATH)
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--build", action="store_true", help="Rebuild the ChromaDB index")
    parser.add_argument("--query", help="Run one query after optionally building")
    parser.add_argument("--test", action="store_true", help="Run three evaluation queries")
    args = parser.parse_args()

    if args.build:
        collection, count = rebuild_collection(args.chunks, args.chroma_path)
        print(f"Embedded and stored {count} chunks in ChromaDB collection '{collection.name}'.")

    if args.query:
        print_results(args.query, retrieve(args.query, top_k=args.top_k, chroma_path=args.chroma_path))

    if args.test:
        run_evaluation_queries(top_k=args.top_k, chroma_path=args.chroma_path)


if __name__ == "__main__":
    main()
