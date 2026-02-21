# Lab 04: Full Ingestion Pipeline

Build a complete document ingestion pipeline that loads policy files, chunks them, generates embeddings, and stores everything in PostgreSQL with pgvector.

## Objectives

By the end of this lab, you will:
- Load and parse multiple policy Markdown files with YAML frontmatter
- Chunk documents using structure-aware Markdown splitting
- Generate embeddings for all chunks with progress tracking
- Bulk-load documents and chunks into PostgreSQL
- Verify the pipeline with counts and a test similarity query

---

## Prerequisites

- Docker containers running (shared/compose.yml)
- Labs 01-03 completed
- Policy documents present in `../../data/policies/` (relative to this lab)
- Python packages: `psycopg2-binary`, `requests`

---

## Step 1: Load Policy Documents

Load all Markdown policy files from the data directory and extract their YAML frontmatter metadata.

Open `start/step1.py` and implement `parse_frontmatter` and `load_all_policies`.

### What you are building

A document loader that reads `.md` files, splits the YAML frontmatter from the body content, and parses the frontmatter key-value pairs into a Python dictionary. This gives you structured metadata (doc_id, title, doc_type, etc.) alongside the raw text content.

### Key concepts

- YAML frontmatter is delimited by `---` markers at the start of the file
- Manual parsing splits on `---` and reads `key: value` lines
- Quoted values in the frontmatter should have their quotes stripped
- The loader returns both metadata and content for each document

### Checkpoint

Run `python start/step1.py` and verify:
- All policy documents are loaded
- Each document shows its doc_id, title, and doc_type
- A content preview is shown for each

---

## Step 2: Chunk All Documents

Apply structure-aware Markdown chunking to all loaded documents, preserving document metadata on each chunk.

Open `start/step2.py` and implement `heading_chunk` and `chunk_all_documents`.

### What you are building

A chunking pipeline that splits each document at `##` heading boundaries and creates a chunk record for each section. Each chunk carries the document_id, chunk_index, heading, content, and the full document metadata.

### Key concepts

- Structure-aware chunking preserves section boundaries
- Each chunk inherits metadata from its parent document
- The chunk_index tracks the order of chunks within a document
- Metadata travels with the chunk through the entire pipeline

### Checkpoint

Run `python start/step2.py` and verify:
- All documents are chunked
- The total chunk count is printed
- The first 5 chunks show their document_id, heading, and word count

---

## Step 3: Embed All Chunks

Generate embeddings for every chunk using the Ollama bge-m3 model with progress reporting.

Open `start/step3.py` and implement `embed_all_chunks`.

### What you are building

A batch embedding function that iterates through all chunks, calls the Ollama embedding API for each, and prints progress updates. This step can take some time depending on the number of chunks.

### Key concepts

- Embedding is the most time-consuming step in the pipeline
- Progress reporting helps track long-running batch operations
- Each chunk's content is embedded independently
- The output is a list of embedding vectors aligned with the input chunk list

### Checkpoint

Run `python start/step3.py` and verify:
- Progress is printed for each chunk (e.g., "Embedding chunk 15/234...")
- The total number of embeddings matches the chunk count
- Embedding dimensions are 1024

---

## Step 4: Bulk Load into PostgreSQL

Create the database tables, insert document records, embed and insert all chunks, and create indexes.

Open `start/step4.py` and implement `create_tables`, `insert_document`, `insert_chunk`, and `create_indexes`.

### What you are building

The database layer of the ingestion pipeline. This creates a `policy_documents` table for document-level metadata and a `policy_chunks` table for chunks with embeddings. After all data is inserted, HNSW and GIN indexes are created for fast similarity and metadata queries.

### Key concepts

- Document-level and chunk-level tables allow flexible querying
- Inserting indexes after bulk loading is faster than maintaining them during inserts
- The HNSW index accelerates vector similarity search
- The GIN index on JSONB metadata enables filtering by document attributes
- Use `ON CONFLICT DO NOTHING` to make document insertion idempotent

### Checkpoint

Run `python start/step4.py` and verify:
- Tables are created
- All documents are inserted
- All chunks are embedded and inserted with progress output
- Indexes are created successfully

---

## Step 5: Verify the Pipeline

Count documents and chunks in the database, then run a test similarity query.

Open `start/step5.py` and implement `count_documents`, `count_chunks`, and `similarity_search`.

### What you are building

A verification script that confirms the pipeline worked correctly. It counts records in both tables and runs a semantic search to ensure embeddings produce meaningful results.

### Key concepts

- Verification is a critical step in any data pipeline
- Counting records confirms nothing was lost during ingestion
- A test query confirms the embeddings and indexes work together
- The cosine distance (<=>) operator returns results sorted by relevance

### Checkpoint

Run `python start/step5.py` and verify:
- Document and chunk counts match expectations
- The test query "What are the KYC requirements?" returns relevant results
- Similarity scores are reasonable (the top result should be highly relevant)

---

## Recap

| Step | What You Did |
|------|-------------|
| Step 1 | Loaded policy Markdown files and parsed YAML frontmatter into metadata dicts |
| Step 2 | Chunked all documents by ## headings, preserving metadata on each chunk |
| Step 3 | Generated bge-m3 embeddings for all chunks with progress reporting |
| Step 4 | Created tables, inserted documents and chunks, and built HNSW and GIN indexes |
| Step 5 | Verified the pipeline with record counts and a test similarity query |

---

## Stretch Goals

- Add error handling and retry logic for failed embedding API calls
- Implement a "delta ingestion" mode that only processes new or changed documents
- Add a command-line interface with argparse to control the pipeline (e.g., --rebuild to drop and recreate tables)
- Track ingestion statistics (total time, average embedding time per chunk, chunks per document)
- Add a deduplication check to avoid inserting the same chunk twice
