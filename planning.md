# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

**Georgia Tech graduate CS/ML course reviews and selection guidance** — Master's students face critical course-selection decisions with limited visibility into actual workload, professor quality, and career relevance. Official course descriptions don't capture: which hard courses (7641, 6505) are worth the pain; how to balance workload across semesters; which professors teach the same course drastically differently; whether a course helps industry recruiting vs research. This knowledge is scattered across Rate My Professors, Reddit threads, Discord servers, student blogs, and Piazza posts. A searchable guide consolidates real graduate student experiences to help peers make informed decisions about course timing, professor choice, and study strategies.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Prof. Isbell (CS 7641 ML) review — rigorous, comprehensive, fair | documents/01_ratemyprofs_CS7641_Isbell.txt |
| 2 | Rate My Professors | Prof. Bhatia (CS 7646 Trading) review — interesting but disorganized | documents/02_ratemyprofs_CS7646_Bhatia.txt |
| 3 | Rate My Professors | Prof. Doroudi (CS 6340 AI) review — excellent teaching, well-paced | documents/03_ratemyprofs_CS6340_Doroudi.txt |
| 4 | r/GATechCS | Thread: "Grad ML course ranking: 7641 vs 6340 vs 7646 vs 6505" | documents/04_reddit_gatechcs_gradcoursecomparison.txt |
| 5 | r/gatech | Thread: "CS 6505 Algorithms destroying me — recovery strategies" | documents/05_reddit_gatech_CS6505_struggling.txt |
| 6 | Blog (Medium-style) | "Master's program survival guide — course planning and time management" | documents/06_blog_MastersProgram_CoursePlanning.txt |
| 7 | Discord | GT CS Master's server — 7641 vs 6340 discussion and pairing advice | documents/07_discord_CS_7641_Discussion.txt |
| 8 | Reddit | High-engagement post: "CS 7641 exams — what matters and how to study" | documents/08_reddit_CS7641_ExamTips.txt |
| 9 | Piazza | Instructor (Prof. Isbell): "Memorization vs understanding on exams" | documents/09_piazza_CS7641_StudyGuidance.txt |
| 10 | Survey compilation | "CS Master's students rate courses" — 62 responses, course selection patterns | documents/10_survey_MS_CourseSelectionGuide.txt |
| 11 | Blog | "CS 7641 vs CS 6340: Which ML/AI course to prioritize" — detailed comparison | documents/11_blog_7641_vs_6340.txt |
| 12 | Blind | Tech industry perspective: "MS degree worth it? Career outcomes and course strategy" | documents/12_blind_MS_CareerReality.txt |


---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->
**Document structure observations:**
- **Short professor reviews** (docs 1-3): 150–350 words, concentrated key insights (pros/cons, workload, difficulty rating)
- **Detailed course comparison threads** (docs 4, 8, 11): 800–1500 words, narrative with ranked tiers and specific recommendations
- **Recovery/study guide posts** (docs 5, 8, 9): 600–1200 words, problem + solution structure with actionable steps
- **Long-form blog posts** (docs 6, 11): 1200–2000 words, structured sections (course overview, workload, pros/cons, decision trees)
- **Survey/compilation** (doc 10): 700–900 words, Q&A format with bullet-pointed responses
- **Career perspective** (doc 12): 1000–1400 words, narrative with embedded decision tables

**Chunk size:** 600 characters (~150-200 tokens) with 100-character overlap

**Overlap:** 100 characters to bridge sentence boundaries and preserve context across section breaks

**Reasoning:**
- Most reviews fit in 1-3 chunks; chunks remain small enough for targeted retrieval while carrying enough semantic context for exam-recovery and course-planning advice.
- Comparison posts have tiers/rankings (e.g., "Tier 1: 7641, 6505") that must stay together; overlap preserves these across chunks.
- Retrieval testing with 300-character chunks pulled loosely related exam-prep content for the CS 6505 recovery query. Increasing to 600 characters kept the question, instructor response, and recovery steps together, improving relevance.



---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MinLM-L6-v2` (via sentence-transfomers) - optimized for speed and semantic understanding on technical/educational text

**Top-k:** 5 chunks per query

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | "Is CS 7641 (Machine Learning) worth taking if I'm on an industry track, and what should I expect?" | 7641 is non-negotiable for industry ML roles; Isbell's course is rigorous with harsh exams (median ~54% raw) but fair curve (median ~65% after curve); workload is 14-16 hrs/week; understanding concepts > memorization; curve brings 55-60% raw scores to B range. |
| 2 | "What's the difference between CS 7641 and CS 6340, and which should I take first?" | 7641 is ML/supervised learning (math-heavy, essential); 6340 is AI/search algorithms (lighter math, broader). Take 7641 first if industry-track (essential). 6340 as complementary second course. 7641 harder (difficulty 8/10) but more directly relevant to ML careers. |
| 3 | "How do I recover if I bomb the first exam in CS 6505 (Algorithms)?" | Formation study groups with struggling peers; read CLRS textbook deeply (not skim); attend office hours weekly; solve old exams under timed conditions; focus on proofs and intuition (not memorization). 6505 has generous curve (median 52→68%); recovery is possible but requires consistent effort. |
| 4 | "What's the recommended course load strategy for a Master's student, and which courses should I prioritize?" | Take 2 hard + 1 medium course per semester (18 credits). Prioritize: 7641 (ML) > 6340 (AI) or 6200 (OS) > specialty electives. Avoid stacking (7641 + 6505 + 7646). DO NOT take 3 hard courses. 7641 should be semester 1 when fresh. |
| 5 | "Which professors should I seek out for CS 7641 and CS 6340, and what are the downsides of other professors?" | Seek: Isbell (7641, 4.5/5 — comprehensive, fair, good curve); Doroudi (6340, 4.7/5 — excellent teacher, organized). Avoid: Bhatia (7646, 3.2/5 — disorganized grading, subjective rubric). Professor quality significantly impacts grade and learning (~1 letter grade difference). |


## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Outdated course structure**: Graduate courses evolve rapidly. A 2024 review of CS 7641 may describe assignments or exam formats that changed in 2026. The system might give outdated advice ("bring a cheat sheet" when the policy changed). Solution: Include timestamps in all chunks; add a disclaimer that course structure changes; prioritize recent posts.

2. **Opinion vs consensus difficulty**: Students write subjective reviews ("7641 is impossible" vs "7641 is doable if you try"). Embedding may conflate extreme opinions with consensus, leading to answers like "opinions are split" when really 80% agree it's hard. Solution: Retrieval should favor high-engagement posts (many upvotes) which reflect consensus, and grounding instructions should distinguish opinion from data.

3. **Course code conflicts and professor ambiguity**: Multiple instructors teach the same course (CS 7641 by Isbell vs hypothetical alternative prof). A query "Is CS 7641 hard?" retrieves both, but answers should be professor-specific. Risk: system conflates reviews of different professors. Solution: Chunk format must include (Professor Name, Course Code, Semester/Year) metadata; reranking to filter for the current/popular instructor.

4. **Relevance drift on "hard" queries**: Query "hardest classes at Tech" could retrieve unrelated documents about difficult undergrad courses (stored in documents if ever added back). Semantic similarity might confuse "hard" across different difficulty contexts (undergrad vs grad, theoretical vs implementation-hard). Solution: Explicit negative keyword filtering (e.g., exclude chunks without "master" or "graduate" keywords).

5. **Context loss in chunking advice sequences**: Posts like "recovery strategies for CS 6505" have numbered steps (1: form study groups, 2: read CLRS, 3: office hours). Splitting these 300-char chunks might separate steps, losing sequence meaning. A query "how do I study for 6505" might retrieve step 2 without step 1. Solution: Preprocess to keep numbered lists intact, or increase overlap to 75 chars for list-heavy sections.

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->
- Tool: GitHub Copilot
- I will give Cladude my Chunking Stratefy section and ask it to implement chunk text with my specified chunk_size = 300 and overlap=50. 

- input:
sample documents:04_reddit_gatechcs_gradcoursecomparison.txt
Requirements: Preserve souce metadata (filanem, course code, professor name)
- Expected output:

ingest.py: load_documents(docs_dir) function to read all .txt files
chunk.py: chunk_text(text, chunk_size=300, overlap=50, preserve_tiers=True) that:
Splits into 300-char chunks with 50-char overlap
Detects tier headers (regex: Tier \d+:) and avoids splitting mid-tier
Returns chunks with metadata: {text, source_file, chunk_id, start_char, end_char}


## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
```
Document Ingestion (Python File 1/O)
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
Response (with soure citations)
```

---

**Pipeline details:**
1. **Ingestion**: Load `.txt` files from `documents/` folder; preserve source metadata (Professor, Course, Date, Source type)
2. **Chunking**: Split by 600-character windows with 100-char overlap; try list-aware splitting (keep numbered steps together)
3. **Embedding**: Convert chunks → 384-dim vectors using MiniLM
4. **Storage**: Index in ChromaDB with metadata (source, course code, professor name, date)
5. **Retrieval**: Given user query, embed query, search top-5 chunks by cosine similarity
6. **Generation**: Pass retrieved chunks + query to Groq LLM with grounding prompt (e.g., "Use only the following documents to answer. If conflicting opinions exist, note that multiple students reported different experiences.")
7. **Response**: Return LLM answer with per-chunk source citations (e.g., "[Source: r/GATechCS, 287 upvotes]")
---

**Milestone 3 — Ingestion and chunking:**


**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
