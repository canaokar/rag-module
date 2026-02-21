# Lab 05: Smart Retrieval

Build progressively smarter retrieval strategies for PolicyChat, starting with
basic vector search and advancing through metadata filtering, threshold gating,
and hybrid (vector + full-text) search.

## Objectives
- Perform cosine-similarity search on embedded policy chunks
- Filter results by document metadata using parameterized queries
- Apply a confidence threshold to avoid returning irrelevant matches
- Combine vector similarity with PostgreSQL full-text search for hybrid retrieval

---

## Prerequisites
- Docker containers running (PostgreSQL with pgvector, Ollama)
- Labs 01-04 completed (data ingested into pgvector)

---

## Step 1: Basic Vector Similarity Search

The simplest form of semantic search: embed a query and find the closest
policy chunks in vector space.

Open `start/step1.py` and implement the TODO sections.

### What you are building
- A function that takes a query string, embeds it with Ollama (bge-m3),
  and queries `policy_chunks` using the `<=>` cosine distance operator.
- Results are ordered by similarity, and the score is computed as
  `1 - (embedding <=> query_vector)`.

### Checkpoint
Run the script and verify that you get 5 results for the query
"What are the KYC requirements?" with similarity scores between 0 and 1.

```
python start/step1.py
```

---

## Step 2: Metadata-Filtered Vector Search

Real-world retrieval often needs to narrow results by document attributes such
as type, regulatory body, or effective date.

Open `start/step2.py` and implement the TODO sections.

### What you are building
- A function that accepts optional filters: `doc_type`, `regulatory_body`,
  and `effective_after`.
- It joins `policy_chunks` with `policy_documents` and dynamically builds a
  WHERE clause using parameterized queries (never string formatting).

### Checkpoint
Run the script and confirm that:
- Unfiltered search returns results from multiple document types.
- Filtering by `doc_type="AML"` returns only AML documents.
- Filtering by `effective_after="2024-01-01"` returns only recent documents.

```
python start/step2.py
```

---

## Step 3: Similarity Score Threshold

Not every query has a good match in the database. A threshold prevents the
system from returning low-confidence results.

Open `start/step3.py` and implement the TODO sections.

### What you are building
- A wrapper around vector search that checks the best result score against
  a configurable threshold (default 0.3).
- If the best score falls below the threshold, the function returns an
  empty list and a warning message instead of unreliable results.

### Checkpoint
Run the script and verify that:
- "What are the KYC requirements?" returns results above the threshold.
- "What is the weather today?" triggers the "No confident match" message.

```
python start/step3.py
```

---

## Step 4: Hybrid Search (Vector + Full-Text)

Pure vector search captures semantic meaning, but keyword-heavy queries can
benefit from traditional full-text search. Combining both gives the best of
both worlds.

Open `start/step4.py` and implement the TODO sections.

### What you are building
- A hybrid search function that computes two scores per chunk:
  - `vector_score`: cosine similarity from the embedding
  - `text_score`: `ts_rank` against the `search_vector` tsvector column
- The final score is a weighted combination: `0.7 * vector + 0.3 * text`.
- Results are ordered by the combined score.

### Checkpoint
Run the script and observe that results show both vector and text scores.
Try adjusting the weights to see how results change.

```
python start/step4.py
```

---

## Recap

| Step | What You Did |
|------|-------------|
| Step 1 | Basic vector similarity search with cosine distance |
| Step 2 | Added metadata filtering with dynamic WHERE clauses |
| Step 3 | Implemented a confidence threshold to guard against bad matches |
| Step 4 | Combined vector and full-text search into hybrid retrieval |

---

## Stretch Goals
- Open `start/stepx.py` and implement simple re-ranking. After initial retrieval, boost results by recency (newer documents score higher) and exact keyword overlap. Compare the ranking before and after re-ranking to see how the order shifts.
- Experiment with different vector/text weight ratios in hybrid search and note when keyword matching helps most.
- Try adding a "diversity" penalty that reduces scores for chunks from the same document, encouraging broader coverage across documents.
