# Lab 11: Capstone -- Multi-Source RAG and Agent Bridge

In this capstone, you will extend PolicyChat to handle multiple data sources and package it as a tool that an AI agent can call. This is where the RAG module connects to the Agents module.

## The Scenario

PolicyChat currently searches a single corpus of existing policy documents. But in a real compliance setting, policies are constantly being updated by regulatory bodies. Your task is to:

1. Ingest a new set of regulatory update documents alongside the existing policies
2. Build a search pipeline that queries both sources and attributes results clearly
3. Detect conflicts between existing policies and newer regulatory updates
4. Wrap the entire pipeline as a callable tool with a standard schema

## Objectives
- Parse and ingest markdown documents with YAML frontmatter
- Build multi-source search across policies and regulatory updates
- Generate answers with clear source attribution
- Detect conflicts between old policies and new regulatory guidance
- Package RAG as a tool with a discoverable schema

---

## Prerequisites
- Docker containers running (PostgreSQL with pgvector, Ollama)
- Labs 01-10 completed (policy documents ingested, evaluation and hardening done)

---

## Part 1: Multi-Source RAG (capstone.py)

Open `start/capstone.py` and implement the TODO sections.

### Step 1: Parse Frontmatter

Implement `parse_frontmatter()` to extract YAML metadata from the markdown files in `data/regulatory_updates/`. Each file has a frontmatter block between `---` markers containing fields like doc_id, title, effective_date, regulatory_body, update_type, and affects.

### Step 2: Ingest Regulatory Updates

Implement `ingest_regulatory_updates()` to:
- Create a `regulatory_updates` table with columns for doc_id, title, effective_date, regulatory_body, update_type, content, embedding (vector 1024), and metadata (JSONB)
- Read each markdown file from the updates directory
- Parse its frontmatter and body content
- Chunk the body text
- Generate embeddings for each chunk
- Insert everything into the database

### Step 3: Multi-Source Search

Implement `multi_source_search()` to:
- Accept an optional `sources` parameter (defaults to searching both "policies" and "updates")
- Embed the query once and search both the policy_chunks and regulatory_updates tables
- Return results grouped by source type

### Step 4: Generate Multi-Source Answer

Implement `generate_multi_source_answer()` to:
- Build a context string that clearly labels each piece of context with its source type and document ID
- Use a system prompt that instructs the LLM to attribute information to its source and flag any conflicts

### Step 5: Detect Conflicts

Implement `detect_conflicts()` to:
- Send policy and update content to the LLM
- Ask it to identify areas where regulatory updates may conflict with or supersede existing policies
- Parse the response into a list of conflict descriptions

### Checkpoint

Run `capstone.py` and verify that:
- Regulatory update files are ingested successfully
- Multi-source search returns results from both policies and updates
- The generated answer attributes information to specific sources
- Conflict detection identifies relevant differences

---

## Part 2: Tool Wrapper (tool_wrapper.py)

Open `start/tool_wrapper.py` and implement the TODO sections.

### What you are building

The `TOOL_SCHEMA` is already defined -- it describes what the tool does, what parameters it accepts, and what it returns. This schema follows the standard format used by AI agent frameworks to discover available tools.

Your job is to implement:
- `policy_search_tool()`: The actual tool function that runs the RAG pipeline. It should embed the query, search the relevant tables (respecting any filters), generate an answer, and return a structured result with `answer`, `sources`, and `confidence` fields.
- `execute_tool()`: A dispatcher that maps tool names to their implementations. This is the single entry point that an agent framework calls.

### Checkpoint

Run `tool_wrapper.py` and verify that:
- The tool schema prints correctly
- The tool executes and returns structured results with answer, sources, and confidence
- Filters are applied correctly when provided
- Unknown tool names return a helpful error

---

## Bridge to Agents

The tool wrapper you built in Part 2 is the connection point between RAG and Agents. Here is how the pieces fit together:

**Discovery**: An agent receives the `TOOL_SCHEMA` as part of its available tools. The schema tells the agent what the tool does and what arguments it needs.

**Invocation**: When the agent decides it needs policy information, it constructs arguments matching the schema and calls `execute_tool("policy_search", arguments)`.

**Response**: The tool returns structured results (answer, sources, confidence) that the agent can use in its reasoning, present to the user, or combine with results from other tools.

This pattern -- defining a schema, implementing the function, and routing through a dispatcher -- is the standard way to give agents access to external capabilities. In the Agents module, you will build the other side: an agent that reads tool schemas and decides when and how to call them.

---

## Recap

| Step | What You Did |
|------|-------------|
| Capstone Step 1 | Parsed YAML frontmatter from regulatory update documents |
| Capstone Step 2 | Ingested regulatory updates into a new database table with embeddings |
| Capstone Step 3 | Built multi-source search across policies and regulatory updates |
| Capstone Step 4 | Generated answers with clear source attribution |
| Capstone Step 5 | Detected conflicts between existing policies and newer updates |
| Tool Wrapper | Packaged the RAG pipeline as a callable tool with a standard schema |

---

## Stretch Goals
- Add a metadata filter to search by regulatory body or effective date range
- Implement versioning so you can track which version of a policy was current when an answer was generated
- Build a "regulatory impact report" that shows which existing policies are affected by each new update
- Add a second tool (e.g., "policy_compare") that takes two document IDs and returns a detailed comparison
- Extend the tool wrapper to support streaming responses for long answers
