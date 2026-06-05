# Prompt for AI Tool: Grounded Generation And Interface

## Context

You are helping build an Unofficial Guide to Georgia Tech graduate CS/ML courses. The existing pipeline already supports:

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
Generation (Groq LLM llama-3.3-70b-versatile)
          ↓
Response (answer + source list)
```

`embed_retrieve.py` exposes `retrieve(query, top_k=4)` and returns dictionaries with:

- `text`
- `metadata`
- `distance`

Metadata includes `source_file`, `chunk_id`, `start_char`, `end_char`, `course_codes`, `professor`, `source`, and `date`.

## Grounding Requirement

Implement generation so answers are grounded in retrieved context only.

The system prompt must enforce:

- Answer only using the provided retrieved chunks.
- Do not use outside knowledge, assumptions, or general advice.
- If the retrieved chunks do not contain enough information, answer exactly: `I don't have enough information on that.`
- If sources conflict, state that the retrieved sources disagree.
- Cite chunk IDs like `[S1]`, `[S2]` when making claims.

Source attribution must be programmatically guaranteed. Do not rely only on the LLM to add source names. The returned object should include a separate `sources` list built from retrieved metadata.

## Output Format

The end-to-end function should return:

```python
{
    "answer": "grounded answer text",
    "sources": [
        "11_blog_7641_vs_6340.txt | chunk 11_001 | distance 0.3737",
        "04_reddit_gatechcs_gradcoursecomparison.txt | chunk 04_004 | distance 0.4200",
    ],
    "retrieved_chunks": [...]
}
```

## LLM Connection

Use Groq:

```python
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
```

Use model `llama-3.3-70b-versatile`.

## Files To Produce

1. `query.py`
   - `format_context(retrieved_chunks)`
   - `format_sources(retrieved_chunks)`
   - `ask(question, top_k=4)`
   - CLI support for `python3 query.py --question "..."`
   - CLI support for `python3 query.py --test`

2. `app.py`
   - Gradio UI with a question box, Ask button, answer textbox, retrieved source textbox, and retrieved chunk preview.

## Gradio Skeleton

```python
import gradio as gr
from query import ask

def handle_query(question):
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    chunks = "\n\n".join(...)
    return result["answer"], sources, chunks

with gr.Blocks() as demo:
    inp = gr.Textbox(label="Your question")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    chunks = gr.Textbox(label="Retrieved chunks", lines=10)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources, chunks])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources, chunks])

demo.launch()
```

## Verification

Before running the code, read it and confirm the grounding prompt is strict and source attribution is returned programmatically. Then test:

1. A CS 7641 industry-track query.
2. A CS 6505 exam-recovery query.
3. An out-of-scope query such as: `What are the best dining halls at Georgia Tech?`

The out-of-scope query should return `I don't have enough information on that.`
