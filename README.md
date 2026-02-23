# PolicyChat RAG Labs -- Participant Guide

> Everything you need to set up, run, and complete all 11 labs.

---

## Table of Contents

- [Environment Setup](#environment-setup)
  - [1. Docker Services](#1-docker-services)
  - [2. Ollama Models](#2-ollama-models)
  - [3. Python Environment](#3-python-environment)
  - [4. Verify Everything](#4-verify-everything)
- [Quick Reference: Ports, URLs, Credentials](#quick-reference)
- [Lab Overview](#lab-overview)
- [Lab Details](#lab-details)
  - [Lab 01: Embeddings](#lab-01-embeddings)
  - [Lab 02: pgvector](#lab-02-pgvector)
  - [Lab 03: Chunking](#lab-03-chunking)
  - [Lab 04: Ingestion Pipeline](#lab-04-ingestion-pipeline)
  - [Lab 05: Smart Retrieval](#lab-05-smart-retrieval)
  - [Lab 06: RAG Generation](#lab-06-rag-generation)
  - [Lab 07: Hybrid Data Queries (Stretch)](#lab-07-hybrid-data-queries-stretch)
  - [Lab 08: PolicyChat API](#lab-08-policychat-api)
  - [Lab 09: RAG Evaluation (Stretch)](#lab-09-rag-evaluation-stretch)
  - [Lab 10: Production Hardening (Stretch)](#lab-10-production-hardening-stretch)
  - [Lab 11: Capstone (Stretch)](#lab-11-capstone-stretch)
- [Useful Commands](#useful-commands)
- [Troubleshooting](#troubleshooting)
- [Database Schema Reference](#database-schema-reference)
- [File Structure](#file-structure)

---

## Environment Setup

### 1. Docker Services

Start PostgreSQL (with pgvector) and Ollama:

```bash
docker compose -f labs/shared/compose.yml up -d
```

This starts two containers:

| Container | Image | Host Port | Purpose |
|-----------|-------|-----------|---------|
| `pgvector-db-policychat` | `pgvector/pgvector:pg17` | `5050` | PostgreSQL 17 with pgvector extension |
| `ollama-service-policychat` | `ollama/ollama:0.5.5` | `11434` | Ollama for embeddings and LLM |

Verify containers are running:

```bash
docker ps --filter "name=policychat"
```

Stop containers (when done):

```bash
docker compose -f labs/shared/compose.yml down
```

Stop and remove all data (fresh start):

```bash
docker compose -f labs/shared/compose.yml down -v
```

### 2. Ollama Models

Pull the two models used in the labs:

```bash
# Embedding model (used in Labs 01-11)
docker exec ollama-service-policychat ollama pull bge-m3

# Chat/LLM model (used in Labs 06-11)
docker exec ollama-service-policychat ollama pull llama3.2
```

Verify models are available:

```bash
docker exec ollama-service-policychat ollama list
```

Expected output should show both `bge-m3` and `llama3.2`.

#### Other Ollama Commands

```bash
# Check which models are loaded in memory
docker exec ollama-service-policychat ollama ps

# Get model details (size, parameters, etc.)
docker exec ollama-service-policychat ollama show bge-m3
docker exec ollama-service-policychat ollama show llama3.2

# Remove a model (if you need to free space)
docker exec ollama-service-policychat ollama rm <model-name>

# Pull a different embedding model (for experimentation)
docker exec ollama-service-policychat ollama pull nomic-embed-text
```

### 3. Python Environment

```bash
# Create virtual environment (from the 02-rag root directory)
python3 -m venv .venv

# Activate it
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r labs/shared/requirements.txt
```

**Required packages** (from `labs/shared/requirements.txt`):

| Package | Version | Used For |
|---------|---------|----------|
| `psycopg2-binary` | >= 2.9.9 | PostgreSQL driver |
| `requests` | >= 2.32.3 | HTTP calls to Ollama API |
| `flask` | >= 3.0.0 | REST API server (Lab 08) |

### 4. Verify Everything

```bash
# 1. Check containers are running
docker ps --filter "name=policychat"
# Should show: pgvector-db-policychat (port 5050) + ollama-service-policychat (port 11434)

# 2. Check models are pulled
docker exec ollama-service-policychat ollama list
# Should show: bge-m3 and llama3.2

# 3. Test Ollama embedding endpoint
curl -s http://localhost:11434/api/embed \
  -d '{"model": "bge-m3", "input": "test"}' | python3 -m json.tool | head -5

# 4. Test Ollama chat endpoint
curl -s http://localhost:11434/api/chat \
  -d '{"model": "llama3.2", "messages": [{"role": "user", "content": "Say hello"}], "stream": false}' \
  | python3 -m json.tool

# 5. Test PostgreSQL connection
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "SELECT 1 FROM pg_extension WHERE extname = 'vector';"

# 6. Test Python environment
source .venv/bin/activate
python3 -c "import requests, psycopg2; print('All packages OK')"
```

---

<a id="quick-reference"></a>
## Quick Reference: Ports, URLs, Credentials

| Service | Host | Port | URL |
|---------|------|------|-----|
| PostgreSQL | localhost | **5050** | - |
| Ollama Embed API | localhost | **11434** | `http://localhost:11434/api/embed` |
| Ollama Chat API | localhost | **11434** | `http://localhost:11434/api/chat` |
| Flask API (Lab 08) | localhost | **5001** | `http://localhost:5001/` |

**Database credentials:**

| Field | Value |
|-------|-------|
| Database | `pgvector` |
| User | `postgres` |
| Password | `postgres` |
| Host | `localhost` |
| Port | `5050` |

**Python DB_CONFIG (copy-paste into any script):**

```python
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}
```

**Ollama API examples:**

```python
import requests

# Generate an embedding
response = requests.post(
    "http://localhost:11434/api/embed",
    json={"model": "bge-m3", "input": "Your text here"}
)
embedding = response.json()["embeddings"][0]  # List of 1024 floats

# Chat with the LLM
response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3.2",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False
    }
)
answer = response.json()["message"]["content"]
```

---

## Lab Overview

| Lab | Topic | Type | Steps | Key Concept |
|-----|-------|------|-------|-------------|
| 01 | Embeddings | Core | 4 | Text to vectors, cosine similarity |
| 02 | pgvector | Core | 4 | Vector storage, `<=>` operator, indexing |
| 03 | Chunking | Core | 4 (+1 stretch) | Fixed-window vs heading-based vs recursive |
| 04 | Ingestion Pipeline | Core | 5 | Full pipeline: load, chunk, embed, store |
| 05 | Smart Retrieval | Core | 4 (+1 stretch) | Filters, thresholds, hybrid search |
| 06 | RAG Generation | Core | 5 | System prompts, context formatting, LLM calls |
| 07 | Hybrid Data Queries | **Stretch** | 4 | JSONB metadata, GIN indexes |
| 08 | PolicyChat API | Core | 4 | Flask REST API with 3 endpoints |
| 09 | RAG Evaluation | **Stretch** | 4 | Golden test sets, precision/recall, LLM-as-judge |
| 10 | Production Hardening | **Stretch** | 4 | Query rewriting, confidence tiers, audit logs, injection defense |
| 11 | Capstone | **Stretch** | 5 + tool wrapper | Multi-source RAG, conflict detection, agent bridge |

**If you fall behind:** grab the solution file from each lab's `solution/` folder and move on. Understanding beats typing every line.

---

## Lab Details

### Lab 01: Embeddings

**Folder:** `labs/lab-01-embeddings/`

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | `get_embedding()` function calling Ollama bge-m3 |
| 2 | `start/step2.py` | `cosine_similarity()` for pairwise comparison of 4 sentences |
| 3 | `start/step3.py` | Threshold-based classifier for related/unrelated term pairs |
| 4 | `start/step4.py` | Compare paragraph vs sentence embeddings |

**Run each step:**

```bash
cd labs/lab-01-embeddings
python start/step1.py    # Should print: "Embedding dimensions: 1024"
python start/step2.py    # Should print 6 pairwise similarity scores
python start/step3.py    # Should classify term pairs as related/unrelated
python start/step4.py    # Should compare paragraph vs sentence embeddings
```

**Heads up:** The first embedding call takes 10-30 seconds as the model loads into memory. Subsequent calls are fast.

---

### Lab 02: pgvector

**Folder:** `labs/lab-02-pgvector/`

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | Connect to PostgreSQL, verify pgvector extension, create table |
| 2 | `start/step2.py` | Generate embeddings and INSERT with `::vector` cast |
| 3 | `start/step3.py` | Create HNSW + IVFFlat indexes, run similarity search |
| 4 | `start/step4.py` | EXPLAIN ANALYZE with and without indexes |

**Run each step:**

```bash
cd labs/lab-02-pgvector
python start/step1.py    # Should confirm pgvector installed, table created
python start/step2.py    # Should insert 5 chunks
python start/step3.py    # Should return 3 similarity search results
python start/step4.py    # Should show index scan vs sequential scan
```

**Key SQL operators to know:**

| Operator | Meaning | Example |
|----------|---------|---------|
| `<=>` | Cosine distance | `ORDER BY embedding <=> query_vec` |
| `<->` | L2 (Euclidean) distance | `ORDER BY embedding <-> query_vec` |
| `<#>` | Negative inner product | `ORDER BY embedding <#> query_vec` |
| `::vector` | Cast to vector type | `%s::vector` |
| `::jsonb` | Cast to JSONB type | `%s::jsonb` |

---

### Lab 03: Chunking

**Folder:** `labs/lab-03-chunking/`

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | Fixed-window chunking (200 words) |
| 2 | `start/step2.py` | Heading-based Markdown chunking (split on `##`) |
| 3 | `start/step3.py` | Recursive chunking (paragraph -> sentence -> word) |
| 4 | `start/step4.py` | Compare all three strategies with statistics |
| x | `start/stepx.py` | *Stretch:* Semantic chunking using embedding similarity |

**Run each step:**

```bash
cd labs/lab-03-chunking
python start/step1.py    # Fixed-window chunks with word counts
python start/step2.py    # Heading-based chunks with section names
python start/step3.py    # Recursive chunks near 200-word target
python start/step4.py    # Side-by-side comparison table
```

**Data file:** `labs/lab-03-chunking/data/sample_policy.md`

---

### Lab 04: Ingestion Pipeline

**Folder:** `labs/lab-04-ingestion/`

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | Load Markdown files, parse YAML frontmatter |
| 2 | `start/step2.py` | Chunk all documents with heading-based splitting |
| 3 | `start/step3.py` | Embed all chunks with progress reporting |
| 4 | `start/step4.py` | Create tables, bulk insert documents + chunks, create indexes |
| 5 | `start/step5.py` | Verify with counts + test similarity query |

**Run each step:**

```bash
cd labs/lab-04-ingestion
python start/step1.py    # Should load 30 policy documents
python start/step2.py    # Should show total chunk count (150+)
python start/step3.py    # Slow! Progress prints every few chunks
python start/step4.py    # Creates tables, inserts everything
python start/step5.py    # Verify: counts + test query
```

**Data files:** `labs/data/policies/*.md` (30 Markdown policy documents)

**This lab populates the database for all remaining labs.** If you fall behind, run the solution files directly:

```bash
cd labs/lab-04-ingestion
python solution/step4.py   # Populates the entire database
python solution/step5.py   # Verify it worked
```

**Verify your data after this lab:**

```bash
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "SELECT COUNT(*) FROM policy_documents;"
# Should return 30

docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "SELECT COUNT(*) FROM policy_chunks;"
# Should return 150+
```

---

### Lab 05: Smart Retrieval

**Folder:** `labs/lab-05-retrieval/`

**Prerequisite:** Lab 04 completed (database populated)

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | Basic vector similarity search with `<=>` |
| 2 | `start/step2.py` | Metadata-filtered search (doc_type, regulatory_body, date) |
| 3 | `start/step3.py` | Similarity threshold to catch out-of-scope queries |
| 4 | `start/step4.py` | Hybrid search: vector + full-text (`ts_rank`) |
| x | `start/stepx.py` | *Stretch:* Re-ranking with recency + keyword boosts |

**Run each step:**

```bash
cd labs/lab-05-retrieval
python start/step1.py    # 5 results ranked by similarity
python start/step2.py    # Filtered results (AML only, recent only)
python start/step3.py    # "Weather" query should be caught by threshold
python start/step4.py    # Hybrid scores (vector + text)
```

---

### Lab 06: RAG Generation

**Folder:** `labs/lab-06-generation/`

**Prerequisite:** Labs 04-05 completed

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | Design the SYSTEM_PROMPT for grounded RAG |
| 2 | `start/step2.py` | `format_context()` and `build_messages()` |
| 3 | `start/step3.py` | Full retrieve -> format -> LLM pipeline |
| 4 | `start/step4.py` | Edge case handling (out-of-scope, low confidence) |
| 5 | `start/step5.py` | Unified `ask_policychat()` function |

**Run each step:**

```bash
cd labs/lab-06-generation
python start/step1.py    # Print and review your system prompt
python start/step2.py    # Formatted context with source labels
python start/step3.py    # First end-to-end RAG answer!
python start/step4.py    # Weather query should be refused
python start/step5.py    # Single function, structured output
```

**Important:** The chat API endpoint is `/api/chat` (not `/api/embed`). A common mistake is using the embed URL for generation.

---

### Lab 07: Hybrid Data Queries (Stretch)

**Folder:** `labs/lab-07-hybrid/`

**Prerequisite:** Lab 04 completed

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | Enrich chunks with JSONB metadata (tags, review_status) |
| 2 | `start/step2.py` | Pure JSONB queries (`@>` containment, `->>` extraction) |
| 3 | `start/step3.py` | Combined vector + JSONB + relational filters |
| 4 | `start/step4.py` | GIN index benchmarking with EXPLAIN ANALYZE |

**Run each step:**

```bash
cd labs/lab-07-hybrid
python start/step1.py    # Enriches all chunks with metadata
python start/step2.py    # JSONB queries by tag and status
python start/step3.py    # Hybrid vector + JSONB search
python start/step4.py    # GIN index performance comparison
```

**Key JSONB operators:**

| Operator | Meaning | Example |
|----------|---------|---------|
| `@>` | Contains | `metadata @> '{"tags": ["aml"]}'` |
| `->>` | Extract as text | `metadata->>'review_status' = 'current'` |
| `->` | Extract as JSON | `metadata->'tags'` |

---

### Lab 08: PolicyChat API

**Folder:** `labs/lab-08-api/`

**Prerequisite:** Labs 04-06 completed

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/utils.py` | **Provided complete** -- review shared config and helpers |
| 2 | `start/search.py` | Vector search with metadata filtering |
| 3 | `start/generate.py` | Context formatting + LLM generation |
| 4 | `start/app.py` | Flask app with 3 endpoints |

**Run the API:**

```bash
cd labs/lab-08-api/start
python app.py
# Server starts on http://localhost:5001
```

**Test with curl (in a second terminal):**

```bash
# Search endpoint
curl -s -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "KYC requirements"}' | python3 -m json.tool

# Ask endpoint (full RAG)
curl -s -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the AML reporting thresholds?"}' | python3 -m json.tool

# Search with filters
curl -s -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "reporting requirements", "filters": {"doc_type": "aml"}}' | python3 -m json.tool

# List all documents
curl -s http://localhost:5001/documents | python3 -m json.tool
```

**If port 5001 is already in use**, change the port in `app.py`:

```python
app.run(host="0.0.0.0", port=5002, debug=True)
```

---

### Lab 09: RAG Evaluation (Stretch)

**Folder:** `labs/lab-09-evaluation/`

**Prerequisite:** Labs 04-08 completed

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | Load golden test set, run retrieval, track hits/misses |
| 2 | `start/step2.py` | Implement precision@K and recall@K |
| 3 | `start/step3.py` | LLM-as-judge for faithfulness and relevance scoring |
| 4 | `start/step4.py` | Compare configs: different K values, vector vs hybrid |

**Run each step:**

```bash
cd labs/lab-09-evaluation
python start/step1.py    # Hit/miss table for golden test set
python start/step2.py    # Precision@5 and recall@5 per query
python start/step3.py    # Faithfulness and relevance scores (slow -- runs full RAG + judge)
python start/step4.py    # Comparison across K=3,5,10 and search modes
```

**Data file:** `labs/lab-09-evaluation/data/golden_test_set.json`

---

### Lab 10: Production Hardening (Stretch)

**Folder:** `labs/lab-10-hardening/`

**Prerequisite:** Labs 04-08 completed

| Step | File | What You Build |
|------|------|----------------|
| 1 | `start/step1.py` | LLM-based query rewriting (vague -> precise) |
| 2 | `start/step2.py` | Confidence tiers (high/medium/low) with tiered responses |
| 3 | `start/step3.py` | Audit logging in JSONL format |
| 4 | `start/step4.py` | Prompt injection detection and input sanitization |

**Run each step:**

```bash
cd labs/lab-10-hardening
python start/step1.py    # "AML stuff" -> precise AML question
python start/step2.py    # Tiered responses based on confidence
python start/step3.py    # Creates audit_log.jsonl
python start/step4.py    # Blocks "Ignore previous instructions..."
```

---

### Lab 11: Capstone (Stretch)

**Folder:** `labs/lab-11-capstone/`

**Prerequisite:** All previous labs completed

| Part | File | What You Build |
|------|------|----------------|
| Part 1 | `start/capstone.py` | Multi-source RAG: ingest regulatory updates, cross-source search, conflict detection |
| Part 2 | `start/tool_wrapper.py` | Agent-callable tool with JSON schema |

**Run:**

```bash
cd labs/lab-11-capstone
python start/capstone.py       # Ingest updates, multi-source search, conflict detection
python start/tool_wrapper.py   # Tool schema + simulated agent call
```

**Data files:** `labs/lab-11-capstone/data/regulatory_updates/*.md` (10 update documents)

---

## Useful Commands

### Docker

```bash
# Start services
docker compose -f labs/shared/compose.yml up -d

# Stop services (keep data)
docker compose -f labs/shared/compose.yml down

# Stop services and delete data (clean slate)
docker compose -f labs/shared/compose.yml down -v

# View container logs
docker logs pgvector-db-policychat
docker logs ollama-service-policychat

# Restart a specific container
docker restart pgvector-db-policychat
docker restart ollama-service-policychat

# Check container resource usage
docker stats --no-stream --filter "name=policychat"
```

### Ollama

```bash
# List available models
docker exec ollama-service-policychat ollama list

# Pull a model
docker exec ollama-service-policychat ollama pull bge-m3
docker exec ollama-service-policychat ollama pull llama3.2

# Show model info (size, parameters, quantization)
docker exec ollama-service-policychat ollama show bge-m3
docker exec ollama-service-policychat ollama show llama3.2

# Check which models are loaded in GPU/memory
docker exec ollama-service-policychat ollama ps

# Remove a model
docker exec ollama-service-policychat ollama rm <model-name>

# Test embedding from command line
curl -s http://localhost:11434/api/embed \
  -d '{"model": "bge-m3", "input": "test sentence"}' | python3 -m json.tool | head -5

# Test chat from command line
curl -s http://localhost:11434/api/chat \
  -d '{"model": "llama3.2", "messages": [{"role": "user", "content": "Say hello"}], "stream": false}' \
  | python3 -m json.tool
```

### PostgreSQL (via Docker)

```bash
# Open an interactive psql session
docker exec -it pgvector-db-policychat psql -U postgres -d pgvector

# Run a single SQL query
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "SELECT COUNT(*) FROM policy_chunks;"

# Check pgvector extension
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"

# List all tables
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "\dt"

# Describe a table
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "\d policy_chunks"

# Count documents and chunks
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "SELECT COUNT(*) AS docs FROM policy_documents; SELECT COUNT(*) AS chunks FROM policy_chunks;"

# List all indexes
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "\di"

# Drop all data (reset for re-ingestion)
docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "TRUNCATE policy_chunks, policy_documents CASCADE;"
```

### Python

```bash
# Activate virtual environment
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Verify packages
pip list | grep -E "psycopg2|requests|flask"

# Run a lab step
cd labs/lab-01-embeddings
python start/step1.py

# Run the solution if stuck
python solution/step1.py
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `Connection refused` on port 5050 | PostgreSQL container not running | `docker compose -f labs/shared/compose.yml up -d` |
| `Connection refused` on port 11434 | Ollama container not running | `docker compose -f labs/shared/compose.yml up -d` |
| `model 'bge-m3' not found` | Model not pulled | `docker exec ollama-service-policychat ollama pull bge-m3` |
| `model 'llama3.2' not found` | Model not pulled | `docker exec ollama-service-policychat ollama pull llama3.2` |
| First embedding call is very slow | Model loading into GPU/memory | Wait 10-30 seconds, it will be fast after |
| Pipeline seems hung | Ollama processing chunks slowly | Check progress output (prints every 25 chunks) |
| `type "vector" does not exist` | pgvector extension not enabled | `docker exec pgvector-db-policychat psql -U postgres -d pgvector -c "CREATE EXTENSION IF NOT EXISTS vector;"` |
| Empty query results | Database not populated | Run Lab 04 solution: `python labs/lab-04-ingestion/solution/step4.py` |
| `ModuleNotFoundError: psycopg2` | Virtual env not activated or packages not installed | `source .venv/bin/activate && pip install -r labs/shared/requirements.txt` |
| Flask port 5001 already in use | Another process on that port | Change to `app.run(port=5002)` in app.py |
| `ImportError` in Lab 08 | Wrong working directory | Must run from `labs/lab-08-api/start/` |
| Chat API returns error | Using `/api/embed` instead of `/api/chat` | Embed: `/api/embed`, Chat: `/api/chat` |
| `::vector` cast error | Embedding not converted to string | Use `str(embedding)` before passing to SQL |
| JSONB query returns nothing | Wrong operator | Use `@>` for containment, `->>` for text extraction |
| `ON CONFLICT` error | Column not UNIQUE | Ensure `doc_id TEXT UNIQUE NOT NULL` in table definition |

### Full Reset

If things are completely broken, start fresh:

```bash
# 1. Stop and remove containers + volumes
docker compose -f labs/shared/compose.yml down -v

# 2. Restart containers (database is recreated from schema.sql)
docker compose -f labs/shared/compose.yml up -d

# 3. Re-pull models
docker exec ollama-service-policychat ollama pull bge-m3
docker exec ollama-service-policychat ollama pull llama3.2

# 4. Re-run ingestion
source .venv/bin/activate
cd labs/lab-04-ingestion
python solution/step4.py
python solution/step5.py
```

---

## Database Schema Reference

The Docker setup automatically creates the schema from `labs/shared/postgres/schema.sql`.

### Table: `policy_documents`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Auto-incrementing ID |
| `doc_id` | TEXT UNIQUE NOT NULL | Policy document identifier (e.g., `POL-AML-001`) |
| `title` | TEXT NOT NULL | Document title |
| `doc_type` | TEXT NOT NULL | Category (e.g., `aml`, `kyc`, `lending`) |
| `effective_date` | DATE | When the policy takes effect |
| `regulatory_body` | TEXT | Regulator (e.g., `FCA`, `PRA`) |
| `content` | TEXT | Full document content |
| `metadata` | JSONB | All frontmatter as JSON |
| `created_at` | TIMESTAMP | Auto-set on insert |

### Table: `policy_chunks`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Auto-incrementing ID |
| `document_id` | INT REFERENCES policy_documents(id) | Foreign key to parent document |
| `chunk_index` | INT NOT NULL | Position within document |
| `content` | TEXT NOT NULL | Chunk text content |
| `heading` | TEXT | Section heading this chunk came from |
| `embedding` | vector(1024) | bge-m3 embedding (1024 dimensions) |
| `metadata` | JSONB | Document metadata carried to chunk level |
| `search_vector` | tsvector | Full-text search vector |
| `created_at` | TIMESTAMP | Auto-set on insert |

### Indexes

| Index | Type | On | Purpose |
|-------|------|----|---------|
| `idx_policy_chunks_embedding` | HNSW (vector_cosine_ops) | `policy_chunks.embedding` | Fast approximate nearest neighbor search |
| `idx_policy_chunks_metadata` | GIN | `policy_chunks.metadata` | Fast JSONB queries |
| `idx_policy_documents_metadata` | GIN | `policy_documents.metadata` | Fast JSONB queries |
| `idx_policy_chunks_search_vector` | GIN | `policy_chunks.search_vector` | Full-text search |
| `idx_policy_documents_doc_type` | B-tree | `policy_documents.doc_type` | Filter by document type |
| `idx_policy_documents_regulatory_body` | B-tree | `policy_documents.regulatory_body` | Filter by regulatory body |

---

## File Structure

```
labs/
├── shared/
│   ├── compose.yml              # Docker services (PostgreSQL + Ollama)
│   ├── requirements.txt         # Python dependencies
│   ├── postgres/
│   │   └── schema.sql           # Database schema (auto-run on first start)
│   └── generate_corpus.py       # Script to generate policy documents
├── data/
│   └── policies/                # 30 Markdown policy documents (for Lab 04+)
│       ├── POL-001-anti-money-laundering-policy.md
│       ├── POL-002-kyc-customer-onboarding-procedures.md
│       └── ... (30 files)
├── lab-01-embeddings/
│   ├── readme.md
│   ├── start/                   # Your working files (TODOs to complete)
│   │   ├── step1.py ... step4.py
│   └── solution/                # Reference solutions
│       ├── step1.py ... step4.py
├── lab-02-pgvector/             # Same start/ + solution/ structure
├── lab-03-chunking/
│   ├── data/sample_policy.md    # Sample document for chunking
│   ├── start/                   # Includes stepx.py (stretch)
│   └── solution/
├── lab-04-ingestion/
├── lab-05-retrieval/            # Includes stepx.py (stretch)
├── lab-06-generation/
├── lab-07-hybrid/               # Stretch lab
├── lab-08-api/
│   ├── start/
│   │   ├── utils.py             # Provided complete
│   │   ├── search.py            # You implement
│   │   ├── generate.py          # You implement
│   │   └── app.py               # You implement
│   └── solution/
├── lab-09-evaluation/           # Stretch lab
│   └── data/golden_test_set.json
├── lab-10-hardening/            # Stretch lab
└── lab-11-capstone/             # Stretch lab
    └── data/regulatory_updates/ # 10 update documents (UPDATE-001 to UPDATE-010)
```
