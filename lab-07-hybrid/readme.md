# Lab 07: Hybrid Data Queries

Explore the power of combining vector similarity search with PostgreSQL
relational filters and JSONB metadata queries. This lab shows how structured
metadata can sharpen retrieval precision beyond what vector search alone provides.

## Objectives
- Enrich policy chunks with structured JSONB metadata (tags, review status)
- Query chunks using JSONB containment and equality operators
- Combine vector search with JSONB and relational filters in a single query
- Measure the performance impact of GIN indexes on JSONB queries

---

## Prerequisites
- Docker containers running (PostgreSQL with pgvector, Ollama)
- Labs 01-04 completed (data ingested into pgvector)

---

## Step 1: Enrich Chunks with JSONB Metadata

Before we can filter by metadata, we need to populate the metadata JSONB
column with structured fields.

Open `start/step1.py` and implement the TODO sections.

### What you are building
- `derive_tags()`: scans chunk content for keywords and maps them to tags
  like "aml", "kyc", "lending", "compliance".
- `derive_review_status()`: assigns one of "current", "under_review", or
  "archived" to simulate real-world document lifecycle.
- `enrich_metadata()`: updates every row in policy_chunks with the derived
  metadata fields.

### Checkpoint
Run the script and verify that all chunks have been enriched. Check a few
rows in the database to confirm the metadata JSONB contains tags and
review_status.

```
python start/step1.py
```

---

## Step 2: Pure JSONB Queries

PostgreSQL JSONB supports powerful query operators. In this step you will
query chunks purely by their metadata, without any vector search.

Open `start/step2.py` and implement the TODO sections.

### What you are building
- `find_by_tag()`: uses the `@>` containment operator to find chunks
  tagged with a specific label.
- `find_by_review_status()`: uses the `->>` text extraction operator for
  equality matching on review_status.
- `find_by_multiple_conditions()`: combines multiple JSONB conditions
  with AND logic.

### Checkpoint
Run the script and verify that each query returns a reasonable count
of matching chunks with the correct tags and statuses.

```
python start/step2.py
```

---

## Step 3: Hybrid Queries (Vector + Relational + JSONB)

This is where everything comes together. Combine semantic similarity with
structured filters to get precise, relevant results.

Open `start/step3.py` and implement the TODO sections.

### What you are building
- `vector_only_search()`: a baseline search with no filters.
- `hybrid_filtered_search()`: the same vector search but with optional
  JSONB tag, review_status, and relational doc_type filters.
- A comparison showing how filters narrow the result set.

### Checkpoint
Run the script and observe that:
- Vector-only search returns a broad set of results.
- Adding tag and status filters significantly narrows the results.
- The filtered results are more precisely targeted to the query intent.

```
python start/step3.py
```

---

## Step 4: GIN Indexes and Performance

JSONB queries on large tables can be slow without proper indexing. GIN
(Generalized Inverted Index) indexes make containment queries fast.

Open `start/step4.py` and implement the TODO sections.

### What you are building
- Functions to create and drop GIN/B-tree indexes on JSONB paths.
- A benchmark that runs EXPLAIN ANALYZE on JSONB queries before and after
  index creation.
- A comparison of query plans showing whether PostgreSQL uses sequential
  scan vs. index scan.

### Checkpoint
Run the script and compare the EXPLAIN ANALYZE output. With small datasets
the time difference may be minimal, but look for changes in the query plan
(sequential scan vs. index scan) that would matter at scale.

```
python start/step4.py
```

---

## Recap

| Step | What You Did |
|------|-------------|
| Step 1 | Enriched policy chunks with JSONB metadata (tags, review status) |
| Step 2 | Queried metadata using JSONB containment and equality operators |
| Step 3 | Combined vector search with JSONB and relational filters |
| Step 4 | Created GIN indexes and measured performance with EXPLAIN ANALYZE |

---

## Stretch Goals
- Add a "regulatory_body" field to the JSONB metadata and filter by it in hybrid queries.
- Implement a faceted search that returns result counts grouped by tag, giving users an overview before they drill down.
- Experiment with GIN indexes using the jsonb_path_ops operator class and compare performance against the default operator class.
