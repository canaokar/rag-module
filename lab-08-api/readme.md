# Lab 08: PolicyChat API

Wrap the PolicyChat RAG pipeline in a Flask REST API with endpoints for
search, question answering, and document listing.

## Objectives
- Build a modular Flask application with separated search, generation, and utility layers
- Expose a /search endpoint for vector-based policy retrieval
- Expose an /ask endpoint for end-to-end RAG question answering
- Expose a /documents endpoint for listing ingested policy documents
- Handle errors gracefully with JSON error responses

---

## Prerequisites
- Docker containers running (PostgreSQL with pgvector, Ollama)
- Labs 01-07 completed (data ingested, metadata enriched)
- Flask installed (`pip install flask`)

---

## Step 1: Review the Utilities Module

The `start/utils.py` file is provided complete. It contains the database
configuration, embedding helper, and LLM call helper that the other modules
will import.

Open `start/utils.py` and read through it to understand the shared interface.

### What is provided
- `DB_CONFIG`: connection parameters for PostgreSQL
- `SYSTEM_PROMPT`: the PolicyChat system prompt
- `get_db_connection()`: returns a psycopg2 connection
- `get_embedding(text)`: embeds text using Ollama bge-m3
- `chat_with_llm(messages)`: calls Ollama llama3.2

### Checkpoint
No code changes needed. Confirm you understand the interface.

---

## Step 2: Implement the Search Module

Open `start/search.py` and implement the TODO sections.

### What you are building
- `search_policies(query, filters, top_k)`: combines vector similarity search
  with optional metadata filters (doc_type, regulatory_body, tag, review_status).
- Returns a list of dicts with content, heading, score, doc_title, and metadata.

### Checkpoint
Run the module directly to test:

```
python start/search.py
```

You should see scored search results for the KYC query.

---

## Step 3: Implement the Generation Module

Open `start/generate.py` and implement the TODO sections.

### What you are building
- `generate_answer(query, search_results)`: formats retrieved chunks as
  numbered context, builds the messages list with SYSTEM_PROMPT, calls the
  LLM, and returns a dict with "answer" and "sources".

### Checkpoint
Run the module directly with the sample data:

```
python start/generate.py
```

You should see a generated answer citing the sample document title.

---

## Step 4: Build the Flask API

Open `start/app.py` and implement the TODO sections for each route.

### What you are building

Three endpoints:

**POST /search** -- Accepts a JSON body with "query", optional "filters" dict,
and optional "top_k" integer. Calls search_policies() and returns JSON results.

**POST /ask** -- Accepts a JSON body with "query" and optional "filters".
Calls search_policies() then generate_answer(), returning the answer with
source citations.

**GET /documents** -- Queries policy_documents for all documents and returns
their id, doc_id, title, and doc_type.

All endpoints should return JSON error messages with appropriate HTTP status
codes (400 for bad requests, 500 for server errors).

### Checkpoint
Start the server and test with curl:

```
python start/app.py
```

Test the search endpoint:
```
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "KYC requirements"}'
```

Test the ask endpoint:
```
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the AML reporting thresholds?"}'
```

Test the documents endpoint:
```
curl http://localhost:5001/documents
```

Verify that:
- /search returns a list of scored results
- /ask returns an answer with source citations
- /documents returns a list of policy documents
- Missing "query" field returns a 400 error

---

## Recap

| Step | What You Did |
|------|-------------|
| Step 1 | Reviewed the shared utilities module |
| Step 2 | Implemented vector search with metadata filtering |
| Step 3 | Implemented context formatting and LLM generation |
| Step 4 | Built a Flask API with search, ask, and documents endpoints |

---

## Stretch Goals
- Add a /health endpoint that checks database connectivity and Ollama availability, returning status for each.
- Add request logging middleware that records the query, response time, and result count for each request.
- Add a top_k parameter to the /ask endpoint so users can control how many chunks are used for context.
- Implement a /search endpoint that supports pagination with offset and limit parameters.
