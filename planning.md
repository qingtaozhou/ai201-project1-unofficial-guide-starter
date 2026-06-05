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

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
