# Milestone 5 Generation And Interface Review

## AI Prompt Used

The prompt used for generation/interface scaffolding is saved in `PROMPT_FOR_AI_MILESTONE5.md`. It included the architecture diagram from `planning.md`, the grounding requirement, the desired answer-plus-sources output format, and a Gradio skeleton.

## Code Generated

- `query.py` wires retrieval to Groq `llama-3.3-70b-versatile`.
- `app.py` provides a Gradio interface with a question box, answer output, source list, and retrieved chunk preview.

## Grounding Review Before Running

The system prompt in `query.py` explicitly requires the model to:

1. Answer only from retrieved chunks.
2. Avoid outside knowledge, assumptions, and general advice.
3. Return exactly `I don't have enough information on that.` when context is insufficient.
4. Cite chunk labels such as `[S1]` for factual claims.

Source attribution is programmatically guaranteed by `format_sources()`, which builds the source list from retrieved metadata rather than relying on the LLM to name sources.

## Tests

- Out-of-scope query tested: `What are the best dining halls at Georgia Tech?`
- Result: returned `I don't have enough information on that.`
- Retrieved chunks were visibly unrelated and had weak distances: top distance `0.5965`.

In-domain generation could not be completed because the current `GROQ_API_KEY` in `.env` was rejected by Groq with `401 invalid_api_key`. The retrieval and prompt-building path is ready; a valid Groq key is needed to complete the live LLM test.
