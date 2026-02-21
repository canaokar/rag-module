# Lab 02: pgvector Setup and Storage

Set up a PostgreSQL database with the pgvector extension to store and query policy document embeddings using vector similarity search.

## Objectives

By the end of this lab, you will:
- Connect to PostgreSQL and verify the pgvector extension
- Create a table with a vector column for storing embeddings
- Insert embeddings generated from policy text
- Create HNSW and IVFFlat indexes for fast similarity search
- Benchmark query performance with and without indexes

---

## Prerequisites

- Docker containers running (shared/compose.yml)
- Lab 01 completed (familiarity with embeddings)
- Python packages: `psycopg2-binary`, `requests`

---

## Step 1: Database Setup

Connect to PostgreSQL, verify the pgvector extension is available, and create the policy_chunks table.

Open `start/step1.py` and implement the `check_vector_extension` and `create_policy_chunks_table` functions.

### What you are building

A database table designed to store policy document chunks alongside their vector embeddings. The table includes columns for document tracking (document_id, chunk_index), the text content, its heading, a 1024-dimensional vector column, and a JSONB column for flexible metadata.

### Key concepts

- pgvector adds the `vector` data type to PostgreSQL
- The `vector(1024)` type stores 1024-dimensional float vectors
- JSONB columns allow flexible metadata storage without schema changes
- Always check that the vector extension is installed before creating vector columns

### Checkpoint

Run `python start/step1.py` and verify:
- The connection succeeds
- The pgvector extension is confirmed as installed
- The table columns are listed with correct types

---

## Step 2: Insert Embeddings

Generate embeddings for five sample policy sentences and store them in the database.

Open `start/step2.py` and implement the `insert_chunk` function.

### What you are building

An insertion function that takes a text chunk and its embedding vector, then writes both to the policy_chunks table. The embedding vector must be cast to the `vector` type when inserted.

### Key concepts

- Embeddings are stored as the `vector` type in pgvector
- Pass the embedding as a string representation (e.g., "[0.1, 0.2, ...]") with a `::vector` cast
- JSONB metadata is inserted using a `::jsonb` cast
- Each chunk is tied to its source document via document_id

### Checkpoint

Run `python start/step2.py` and verify:
- All 5 chunks are inserted successfully
- The total row count matches expectations

---

## Step 3: Create Indexes and Search

Create HNSW and IVFFlat indexes on the embedding column, then perform a vector similarity search.

Open `start/step3.py` and implement `create_hnsw_index`, `create_ivfflat_index`, and `similarity_search`.

### What you are building

Two different index types for approximate nearest neighbor (ANN) search, plus a query function that finds the most similar chunks to a given query embedding using cosine distance.

### Key concepts

- HNSW (Hierarchical Navigable Small World) provides high recall with tunable parameters (m, ef_construction)
- IVFFlat (Inverted File with Flat compression) partitions vectors into lists for faster search
- The `<=>` operator computes cosine distance in pgvector
- Cosine distance = 1 - cosine similarity, so lower distance means higher similarity
- Results are ordered by distance (ascending) to get the most similar first

### Checkpoint

Run `python start/step3.py` and verify:
- Both indexes are created without errors
- The similarity search returns 3 results
- The most relevant result matches the query topic (identity/KYC)

---

## Step 4: Index Performance Comparison

Use EXPLAIN ANALYZE to observe how indexes affect query execution plans and timing.

Open `start/step4.py` and implement `run_explain_analyze`, `drop_indexes`, and `create_hnsw_index`.

### What you are building

A benchmarking script that runs the same similarity query three times: with the index, without the index, and again with a freshly created index. EXPLAIN ANALYZE reveals whether PostgreSQL uses an index scan or a sequential scan.

### Key concepts

- EXPLAIN ANALYZE shows the actual query execution plan and timing
- Without an index, PostgreSQL performs a sequential scan over all rows
- With an HNSW or IVFFlat index, PostgreSQL performs an index scan
- The performance difference becomes dramatic at scale (thousands of rows)
- With only 5 rows the difference is negligible, but the scan type will change

### Checkpoint

Run `python start/step4.py` and verify:
- The first query (with index) shows an index scan in the plan
- After dropping indexes, the query shows a sequential scan
- After recreating the index, the query returns to an index scan

---

## Recap

| Step | What You Did |
|------|-------------|
| Step 1 | Connected to PostgreSQL and created the policy_chunks table with a vector(1024) column |
| Step 2 | Generated embeddings for 5 sample sentences and inserted them into the database |
| Step 3 | Created HNSW and IVFFlat indexes and ran a cosine similarity search |
| Step 4 | Compared EXPLAIN ANALYZE output with and without indexes |

---

## Stretch Goals

- Insert 100+ chunks and re-run the performance comparison to see a more significant difference
- Experiment with different HNSW parameters (m, ef_construction) and observe the trade-offs
- Try L2 distance (vector_l2_ops) instead of cosine distance and compare results
- Add a GIN index on the metadata JSONB column and query by metadata fields
