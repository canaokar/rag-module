# Lab 10: Production Hardening

A RAG pipeline that works in a demo is not the same as one that works in production. In this lab, you will add four essential production features: query rewriting, confidence-based responses, audit logging, and prompt injection defense.

## Objectives
- Rewrite vague user queries into precise policy questions using an LLM
- Implement confidence thresholds that control response quality
- Build audit logging for compliance and debugging
- Add basic defenses against prompt injection attacks

---

## Prerequisites
- Docker containers running (PostgreSQL with pgvector, Ollama)
- Labs 01-08 completed (policy documents ingested with embeddings)

---

## Step 1: Query Rewriting

Users rarely ask perfectly-formed questions. They type things like "AML stuff" or "what about loans?" and expect useful answers. Query rewriting uses the LLM to transform these vague inputs into precise policy questions before retrieval.

Open `start/step1.py` and implement the TODO sections.

### What you are building
- `rewrite_query()`: Sends the user query to the LLM with a system prompt that instructs it to rewrite the query as a specific banking policy question. Returns a JSON object with the rewritten query and an explanation. If the query is too vague to rewrite, returns null for the rewritten field.

### Checkpoint
Run the script and verify that:
- "what about loans?" becomes a specific lending policy question
- "AML stuff" becomes a question about anti-money laundering procedures
- "can I do that?" is flagged as too vague to rewrite
- "tell me about customer checks" becomes a KYC-related question

---

## Step 2: Confidence Thresholds and Tiered Responses

Not every query will match well against the policy corpus. Rather than always generating an answer (which may hallucinate), you can use similarity scores to determine how confident the system should be in its response.

Open `start/step2.py` and implement the TODO sections.

### What you are building
- `determine_confidence()`: Takes the similarity scores from retrieval and classifies confidence as high (average > 0.5), medium (0.3 to 0.5), or low (< 0.3)
- `generate_tiered_response()`: Generates different types of responses based on confidence level. High confidence gets a full answer. Medium gets an answer with a caveat. Low gets a safe fallback message.

### Checkpoint
Run the script with the test queries. Verify that in-domain queries (KYC requirements, suspicious transactions) produce higher confidence than out-of-domain queries (quantum computing). Check that the response format changes based on confidence level.

---

## Step 3: Audit Logging

In regulated environments, every system interaction needs to be traceable. Audit logs provide a record of what was asked, what was retrieved, and what was generated.

Open `start/step3.py` and implement the TODO sections.

### What you are building
- `log_interaction()`: Appends a JSON object as a single line to a JSON Lines file (audit_log.jsonl)
- `rag_pipeline_with_logging()`: Wraps the full RAG pipeline (retrieve, determine confidence, generate) and logs every interaction with timestamp, query, rewritten query, retrieved chunks with scores, generated response, and confidence level
- `display_audit_log()`: Reads and displays the last N entries from the log file

### Checkpoint
Run the script and verify that audit_log.jsonl is created with one entry per query. Each entry should contain all required fields. The display function should show a readable summary of recent interactions.

---

## Step 4: Basic Prompt Injection Defense

Prompt injection is an attack where a user crafts input designed to override the system prompt and make the LLM behave in unintended ways. While no defense is perfect, basic input sanitization catches the most common patterns.

Open `start/step4.py` and implement the TODO sections.

### What you are building
- `detect_injection()`: Scans the query against a list of known injection patterns (case-insensitive) and returns which patterns matched
- `truncate_input()`: Cuts off inputs longer than 500 characters to prevent very long injection payloads
- `sanitize_query()`: Runs the full sanitization pipeline and returns a result indicating whether the query is safe, along with details about any issues found

### Checkpoint
Run the script and verify that:
- Normal policy queries pass sanitization
- Injection attempts like "Ignore previous instructions..." are blocked
- The specific matched patterns are reported
- Very long inputs are truncated

---

## Recap

| Step | What You Did |
|------|-------------|
| 1    | Used LLM-based query rewriting to turn vague inputs into precise policy questions |
| 2    | Implemented confidence thresholds with tiered response strategies |
| 3    | Built audit logging that records every interaction in JSON Lines format |
| 4    | Added prompt injection detection and input sanitization |

---

## Stretch Goals
- Add query caching to avoid re-embedding identical or very similar queries
- Implement rate limiting per user or session
- Build a multi-turn conversation handler that tracks context across questions
- Add more sophisticated injection detection using the LLM itself as a classifier
- Create an admin dashboard that reads audit logs and shows usage statistics
