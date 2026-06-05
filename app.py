"""Gradio interface for the grounded course-guide QA system."""

from __future__ import annotations

import gradio as gr

from query import ask


def format_chunk_preview(result: dict) -> str:
    """Format retrieved chunk text for transparent inspection in the UI."""
    previews = []
    for index, chunk in enumerate(result["retrieved_chunks"], start=1):
        metadata = chunk["metadata"]
        source = metadata.get("source_file", "unknown source")
        chunk_id = metadata.get("chunk_id", "unknown chunk")
        previews.append(
            f"[S{index}] {source} | chunk {chunk_id} | distance {chunk['distance']:.4f}\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(previews)


def handle_query(question: str) -> tuple[str, str, str]:
    """Run retrieval and grounded generation for the UI."""
    try:
        result = ask(question)
    except Exception as exc:
        return str(exc), "", ""
    sources = "\n".join(f"- {source}" for source in result["sources"])
    chunks = format_chunk_preview(result)
    return result["answer"], sources, chunks


with gr.Blocks(title="Unofficial GT CS Course Guide") as demo:
    gr.Markdown("# Unofficial GT CS Course Guide")
    inp = gr.Textbox(label="Your question", lines=2)
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=5)
    chunks = gr.Textbox(label="Retrieved chunks", lines=12)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources, chunks])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources, chunks])


if __name__ == "__main__":
    demo.launch()
