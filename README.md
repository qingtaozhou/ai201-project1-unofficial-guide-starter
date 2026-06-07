# The Unofficial Guide — Project 1

## Domain

This system covers Georgia Tech graduate CS/ML course reviews and course-selection guidance. It focuses on practical student-facing questions that official course descriptions do not answer well: workload, exam style, professor differences, course sequencing, career relevance, and what to do when a course goes badly.

This knowledge is valuable because Master's students often make expensive semester-planning decisions with incomplete information. The useful advice is scattered across Rate My Professors, Reddit, Discord-style discussions, Piazza posts, student blogs, survey summaries, and career forums. The goal of this project is to retrieve and synthesize those informal perspectives while keeping answers tied to visible source chunks.

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Prof. Isbell CS 7641 review | Rate My Professors-style review | `documents/01_ratemyprofs_CS7641_Isbell.txt` |
| 2 | Prof. Bhatia CS 7646 review | Rate My Professors-style review | `documents/02_ratemyprofs_CS7646_Bhatia.txt` |
| 3 | Prof. Doroudi CS 6340 review | Rate My Professors-style review | `documents/03_ratemyprofs_CS6340_Doroudi.txt` |
| 4 | Grad ML course comparison thread | Reddit-style discussion | `documents/04_reddit_gatechcs_gradcoursecomparison.txt` |
| 5 | CS 6505 recovery thread | Reddit-style discussion | `documents/05_reddit_gatech_CS6505_struggling.txt` |
| 6 | Master's course-planning guide | Student blog | `documents/06_blog_MastersProgram_CoursePlanning.txt` |
| 7 | CS 7641 vs CS 6340 discussion | Discord-style transcript | `documents/07_discord_CS_7641_Discussion.txt` |
| 8 | CS 7641 exam tips | Reddit-style discussion | `documents/08_reddit_CS7641_ExamTips.txt` |
| 9 | CS 7641 study guidance | Piazza-style instructor post | `documents/09_piazza_CS7641_StudyGuidance.txt` |
| 10 | Master's course-selection survey | Survey compilation | `documents/10_survey_MS_CourseSelectionGuide.txt` |
| 11 | CS 7641 vs CS 6340 comparison | Student blog | `documents/11_blog_7641_vs_6340.txt` |
| 12 | MS career reality discussion | Blind-style career forum post | `documents/12_blind_MS_CareerReality.txt` |

## Chunking Strategy

**Chunk size:** 600 characters.

**Overlap:** 100 characters.

**Why these choices fit your documents:** The corpus is made of short professor reviews plus medium-length discussions, surveys, and blog posts. My first version used 300-character chunks with 50 characters of overlap, but testing showed that advice sequences were sometimes split too aggressively. For example, the CS 6505 recovery thread separated the student's problem, the instructor's recommendations, and peer recovery advice into fragments. Increasing to 600 characters with 100 characters of overlap kept the question and useful advice together while still keeping chunks small enough for targeted retrieval.

The chunker also tries to preserve tier/ranking sections and numbered-list blocks, because many source documents use ranked course lists or step-by-step recovery advice. Documents are cleaned during ingestion and each chunk keeps metadata including source filename, chunk id, character positions, course codes, professor, source type, and date.

**Final chunk count:** 65 chunks across 12 documents.

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` from `sentence-transformers`.

I chose this model because it runs locally, does not require an embedding API key, is fast enough for repeated experimentation, and produces 384-dimensional embeddings that work well for small educational/advice corpora. The vector store is ChromaDB, stored locally in `chroma_db/`.

**Production tradeoff reflection:** If this were deployed for real users and cost were not a constraint, I would compare larger embedding models with better retrieval accuracy on nuanced advising questions. I would care about whether the model handles course codes, professor names, and short informal comments well. I would also weigh latency and hosting complexity: a local model is simple and private, but an API-hosted embedding model might produce better semantic matches and support future multilingual queries or longer chunks.

## Grounded Generation

**System prompt grounding instruction:** `query.py` uses a strict system prompt:

```text
Answer only from the retrieved document chunks provided in the user message.
Do not use outside knowledge, assumptions, or general advice.
If the retrieved chunks do not contain enough information to answer, respond exactly:
"I don't have enough information on that."
If retrieved chunks disagree, say that the sources disagree and explain only the disagreement visible in the chunks.
Cite chunk labels like [S1] or [S2] for every factual claim.
Do not cite a source unless it directly supports the sentence.
```

The generation step also has a retrieval-distance guard. If the top retrieved chunk has a distance above `0.55`, the system returns `I don't have enough information on that.` before calling Groq. This prevents unrelated questions, such as dining hall recommendations, from being answered with plausible but unsupported general knowledge.

**How source attribution is surfaced in the response:** Retrieved chunks are formatted as `[S1]`, `[S2]`, etc. inside the prompt, and the model is instructed to cite those labels. More importantly, the UI and CLI build a separate source list programmatically from Chroma metadata. That source list includes source filename, chunk id, and distance score, so attribution is visible even if the model forgets to name a source in the prose.

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Is CS 7641 worth taking if I'm on an industry track, and what should I expect? | 7641 is essential for industry ML roles; expect rigorous ML foundations, heavy math, difficult exams, and significant weekly workload. | The system said CS 7641 is worth taking for industry ML because it provides ML foundations and is necessary for ML roles. It described supervised/unsupervised/RL/neural nets, 8/10 difficulty, about 15 hrs/week, and emphasized conceptual understanding. Sources included `11_blog_7641_vs_6340.txt`, `04_reddit_gatechcs_gradcoursecomparison.txt`, and `08_reddit_CS7641_ExamTips.txt`. | Relevant | Accurate |
| 2 | What is the difference between CS 7641 and CS 6340, and which should I take first? | 7641 is ML/data-learning and more math-heavy/career-critical for ML; 6340 is broader AI/search/planning and lighter. Take 7641 first if industry ML is the goal, then 6340 as a complement. | The system said 7641 covers supervised, unsupervised, RL, neural networks, and deep learning, while 6340 focuses on AI topics like game AI, robotics, and classical AI. It recommended taking 7641 first and 6340 second depending on interests. | Relevant | Accurate |
| 3 | How do I recover if I bomb the first exam in CS 6505 Algorithms? | Form study groups, read CLRS proofs deeply, attend office hours, practice proofs/old exams, trust the curve, and decide whether dropping makes sense based on goals. | The system recommended study groups, deep CLRS proof reading, office hours, and not panicking about raw scores because the curve exists. It also noted conflicting student advice: one student dropped/retook, while another said pushing through created durable understanding. | Relevant | Accurate |
| 4 | What is the recommended course load strategy for a Master's student, and which courses should I prioritize? | Take 2 hard + 1 medium course per semester; prioritize CS 7641, then CS 6340 or CS 6200 depending on goals; avoid stacking CS 7641 + CS 6505 + CS 7646. | The system recommended 2 hard + 1 medium course per semester, prioritizing CS 7641, then domain/elective choices. It cited CS 6340 and CS 6200 as useful breadth/foundation courses and warned against CS 6505 + CS 7641 + CS 7646 together. | Relevant | Accurate |
| 5 | Which professors should I seek out for CS 7641 and CS 6340, and what are the downsides of other professors? | Seek Isbell for CS 7641 and Doroudi for CS 6340; Isbell is rigorous/fair and Doroudi is clear/well-paced. Bhatia/CS 7646 is described as disorganized with subjective grading. | The system said no specific professor was recommended for CS 7641 in the retrieved chunks and only identified Doroudi for CS 6340. It did not retrieve the Rate My Professors chunk that clearly recommends Isbell, and it did not discuss Bhatia's downsides. | Partially relevant | Inaccurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

## Failure Case Analysis

**Question that failed:** Which professors should I seek out for CS 7641 and CS 6340, and what are the downsides of other professors?

**What the system returned:** The system answered that no specific professor was recommended for CS 7641 in the retrieved chunks. It identified Doroudi for CS 6340 but did not mention that the corpus has a direct Rate My Professors-style review recommending Isbell for CS 7641. It also did not retrieve the Bhatia review that discusses disorganized grading and subjective rubric issues.

**Root cause (tied to a specific pipeline stage):** This was a retrieval failure. The embedding search matched broad course-comparison chunks about CS 7641 vs CS 6340 more strongly than the shorter professor-review chunks. The query mixed several intents: identify recommended professors for two courses and describe downsides of other professors. Because the retriever uses one embedding query and top-k retrieval, it favored chunks about the course pair rather than separately retrieving professor-specific documents for Isbell, Doroudi, and Bhatia. Generation actually behaved correctly by refusing to invent unsupported professor recommendations; the missing information was caused upstream by retrieval.

**What you would change to fix it:** I would add metadata-aware retrieval for professor/course queries. If the query includes "professor" or asks "which professors," the retriever should boost Rate My Professors-style documents and maybe issue multiple subqueries: one for `CS 7641 Isbell`, one for `CS 6340 Doroudi`, and one for known downside terms such as "disorganized" or "grading." A hybrid BM25 + vector retrieval pass would also help because exact professor names and course codes matter more here than pure semantic similarity.

## Spec Reflection

**One way the spec helped you during implementation:** The planning document forced me to define the architecture before coding: ingestion, chunking, embedding, vector storage, retrieval, generation, and response attribution. That made it much easier to prompt AI tools for specific pieces instead of asking for a vague "RAG app." The evaluation questions in `planning.md` also gave me concrete acceptance tests, which revealed the chunk-size problem in the CS 6505 recovery query.

**One way your implementation diverged from the spec, and why:** The original spec used 300-character chunks with 50-character overlap and mentioned `mixtral-8x7b` for Groq generation. During testing, 300-character chunks were too small for recovery/advice posts, so I changed the implementation to 600-character chunks with 100-character overlap. I also used Groq's `llama-3.3-70b-versatile` because it was the recommended default for this milestone and produced stronger grounded answers than the older model choice in the initial diagram.

## AI Usage

**Instance 1**

- *What I gave the AI:* I gave the AI my `planning.md` retrieval approach and pipeline diagram, including the requirement to use `all-MiniLM-L6-v2`, ChromaDB, source metadata, and top-k retrieval.
- *What it produced:* It produced `embed_retrieve.py`, which loads `chunks.json`, embeds chunks, stores them in a persistent ChromaDB collection, and exposes a `retrieve()` function with distances and metadata.
- *What I changed or overrode:* I added cached/offline model loading so repeat runs do not stall on Hugging Face metadata checks. I also added course-code-aware candidate reranking and changed chunking from 300/50 to 600/100 after evaluation showed the CS 6505 recovery advice was split too thinly.

**Instance 2**

- *What I gave the AI:* I gave the AI the pipeline diagram, grounding requirement, desired answer-plus-source output format, and a Gradio skeleton for Milestone 5.
- *What it produced:* It produced `query.py` for Groq-backed grounded generation and `app.py` for a Gradio interface.
- *What I changed or overrode:* I made source attribution programmatic with `format_sources()` instead of relying only on the LLM to cite documents. I also added a relevance-distance guard so out-of-scope questions return `I don't have enough information on that.` before generation.

## How To Run

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Add a Groq key to `.env`:

```bash
GROQ_API_KEY=gsk_your_real_key_here
```

3. Build or rebuild the vector store:

```bash
python3 embed_retrieve.py --build
```

4. Run the CLI:

```bash
python3 query.py --question "Is CS 7641 worth taking for industry ML?"
```

5. Run the Gradio app:

```bash
python3 app.py
```

If the default Gradio port range is busy, run with an explicit port:

```bash
GRADIO_SERVER_PORT=9000 python3 app.py
```

## Demo Video Plan

The demo should show the Gradio interface and source list. I used `http://localhost:9000` when the default Gradio port range was unavailable.

Recommended demo flow:

1. Ask: `Is CS 7641 worth taking if I'm on an industry track?` Show that the answer cites retrieved chunks about 7641's ML foundation, difficulty, and industry relevance.
2. Ask: `How do I recover if I bomb the first exam in CS 6505?` Show that the answer cites the instructor-response chunk and recovery advice.
3. Ask: `Which professors should I seek out for CS 7641 and CS 6340?` Explain the failure: retrieval returns broad course-comparison chunks instead of the Isbell/Bhatia professor-review chunks.
4. Briefly scroll through this README's evaluation report and failure-case analysis.
