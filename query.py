"""Grounded generation over retrieved course-guide chunks."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from embed_retrieve import DEFAULT_TOP_K, retrieve


MODEL_NAME = "llama-3.3-70b-versatile"
INSUFFICIENT_ANSWER = "I don't have enough information on that."
RELEVANCE_DISTANCE_THRESHOLD = 0.55

SYSTEM_PROMPT = f"""You are a grounded question-answering assistant for a Georgia Tech graduate CS course guide.

You must follow these rules:
1. Answer only from the retrieved document chunks provided in the user message.
2. Do not use outside knowledge, assumptions, or general advice.
3. If the retrieved chunks do not contain enough information to answer, respond exactly: "{INSUFFICIENT_ANSWER}"
4. If retrieved chunks disagree, say that the sources disagree and explain only the disagreement visible in the chunks.
5. Cite chunk labels like [S1] or [S2] for every factual claim.
6. Do not cite a source unless it directly supports the sentence.
"""


def source_label(chunk: dict[str, Any], index: int) -> str:
    """Return a compact source label for one retrieved chunk."""
    metadata = chunk["metadata"]
    source_file = metadata.get("source_file", "unknown source")
    chunk_id = metadata.get("chunk_id", "unknown chunk")
    distance = chunk.get("distance", 0.0)
    return f"S{index}: {source_file} | chunk {chunk_id} | distance {distance:.4f}"


def format_context(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks as labelled evidence for the LLM."""
    context_blocks = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        context_blocks.append(
            "\n".join(
                [
                    f"[S{index}]",
                    f"source_file: {metadata.get('source_file', '')}",
                    f"chunk_id: {metadata.get('chunk_id', '')}",
                    f"course_codes: {metadata.get('course_codes', '')}",
                    f"professor: {metadata.get('professor', '')}",
                    f"source_type: {metadata.get('source', '')}",
                    f"date: {metadata.get('date', '')}",
                    "text:",
                    chunk["text"],
                ]
            )
        )
    return "\n\n---\n\n".join(context_blocks)


def format_sources(chunks: list[dict[str, Any]]) -> list[str]:
    """Build source attribution from metadata, independent of the LLM."""
    return [source_label(chunk, index) for index, chunk in enumerate(chunks, start=1)]


def has_relevant_context(chunks: list[dict[str, Any]]) -> bool:
    """Return whether the top retrieval result is strong enough for generation."""
    return bool(chunks) and chunks[0]["distance"] <= RELEVANCE_DISTANCE_THRESHOLD


def build_user_prompt(question: str, chunks: list[dict[str, Any]]) -> str:
    """Build the grounded generation prompt."""
    return f"""Question:
{question}

Retrieved document chunks:
{format_context(chunks)}

Write a concise answer using only the retrieved document chunks. Include [S#] citations for claims. If the chunks do not answer the question, respond exactly:
{INSUFFICIENT_ANSWER}
"""


def ask(question: str, top_k: int = DEFAULT_TOP_K) -> dict[str, Any]:
    """Retrieve relevant chunks and generate a grounded answer."""
    question = question.strip()
    if not question:
        return {"answer": "Please enter a question.", "sources": [], "retrieved_chunks": []}

    chunks = retrieve(question, top_k=top_k)
    sources = format_sources(chunks)
    if not has_relevant_context(chunks):
        return {
            "answer": INSUFFICIENT_ANSWER,
            "sources": sources,
            "retrieved_chunks": chunks,
        }

    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to .env before running generation.")

    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(question, chunks)},
            ],
            temperature=0.0,
            max_tokens=700,
        )
    except Exception as exc:
        raise RuntimeError(
            "Groq generation failed. Check that GROQ_API_KEY in .env is valid."
        ) from exc
    answer = response.choices[0].message.content.strip()
    return {"answer": answer, "sources": sources, "retrieved_chunks": chunks}


def print_result(question: str, result: dict[str, Any]) -> None:
    """Print one grounded answer with its programmatic source list."""
    print(f"\n=== Question ===\n{question}")
    print(f"\n=== Answer ===\n{result['answer']}")
    print("\n=== Sources ===")
    for source in result["sources"]:
        print(f"- {source}")
    print("\n=== Retrieved Chunks ===")
    for index, chunk in enumerate(result["retrieved_chunks"], start=1):
        print(f"\n[S{index}] distance={chunk['distance']:.4f}")
        print(chunk["text"])


def run_tests() -> None:
    """Run grounded generation checks, including an out-of-scope query."""
    questions = [
        "Is CS 7641 worth taking if I'm on an industry track, and what should I expect?",
        "How do I recover if I bomb the first exam in CS 6505 Algorithms?",
        "What are the best dining halls at Georgia Tech?",
    ]
    for question in questions:
        print_result(question, ask(question))


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Ask grounded questions over retrieved chunks.")
    parser.add_argument("--question", help="Question to answer")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--test", action="store_true", help="Run 2 in-domain tests and 1 out-of-scope test")
    args = parser.parse_args()

    if args.test:
        try:
            run_tests()
        except RuntimeError as exc:
            print(exc, file=sys.stderr)
            sys.exit(1)
    elif args.question:
        try:
            print_result(args.question, ask(args.question, top_k=args.top_k))
        except RuntimeError as exc:
            print(exc, file=sys.stderr)
            sys.exit(1)
    else:
        parser.error("Provide --question or --test")


if __name__ == "__main__":
    main()
