# Lab 06: RAG Generation Pipeline

Build the generation side of PolicyChat. You will design a system prompt,
format retrieved context for the LLM, wire up the full retrieval-to-generation
flow, and handle edge cases gracefully.

## Objectives
- Craft a system prompt that grounds the LLM in retrieved context
- Format retrieved chunks into a structured prompt with source attribution
- Connect retrieval to generation for end-to-end RAG
- Handle out-of-scope queries, low-confidence results, and ambiguous input

---

## Prerequisites
- Docker containers running (PostgreSQL with pgvector, Ollama)
- Labs 01-05 completed (data ingested and retrieval working)

---

## Step 1: Design the System Prompt

A well-crafted system prompt is the foundation of reliable RAG generation.
It tells the LLM how to behave, what to cite, and when to decline.

Open `start/step1.py` and implement the TODO sections.

### What you are building
- A `SYSTEM_PROMPT` constant that instructs the LLM to:
  - Only answer from provided context
  - Cite sources by document title
  - Admit when information is insufficient
  - Use professional banking language

### Checkpoint
Run the script and review your prompt. It should be clear, specific, and
cover all the behavioral rules listed above.

```
python start/step1.py
```

---

## Step 2: Context Formatting

The LLM needs the retrieved chunks presented in a clear, structured format
so it can reference and cite them.

Open `start/step2.py` and implement the TODO sections.

### What you are building
- `format_context()`: takes a list of chunk dicts and produces a numbered
  text block with source attribution for each chunk.
- `build_messages()`: assembles the full messages list (system + user) with
  the formatted context and the user's query.

### Checkpoint
Run the script with the provided sample data. Verify that the context is
cleanly numbered and the messages list has the correct structure.

```
python start/step2.py
```

---

## Step 3: Full Retrieval-to-Generation Flow

Connect the retrieval pipeline from Lab 05 to the Ollama LLM to produce
grounded answers.

Open `start/step3.py` and implement the TODO sections.

### What you are building
- `retrieve_chunks()`: queries pgvector for the most similar chunks.
- `format_context()`: formats chunks with source labels.
- `chat_with_llm()`: sends messages to Ollama and returns the response.
- `ask()`: orchestrates the full flow from query to answer.

### Checkpoint
Run the script and verify that you get a coherent answer about KYC
requirements that cites specific policy documents.

```
python start/step3.py
```

---

## Step 4: Edge Case Handling

A production RAG system must handle queries that fall outside its knowledge
without hallucinating.

Open `start/step4.py` and implement the TODO sections.

### What you are building
- `is_out_of_scope()`: detects clearly off-topic queries.
- `retrieve_with_threshold()`: returns a status flag when results are
  missing or below the confidence threshold.
- `handle_query()`: routes each query through scope check, retrieval,
  and generation, returning appropriate fallback messages for each edge case.

### Checkpoint
Run the script with the three test queries. Verify that:
- The banking policy query gets a real answer with sources.
- The weather query is flagged as out of scope.
- The quantum computing query gets a low-confidence or no-match response.

```
python start/step4.py
```

---

## Step 5: Full RAG Loop

Combine everything into a single clean function.

Open `start/step5.py` and implement the TODO sections.

### What you are building
- `ask_policychat(query)`: a single function that handles the entire pipeline
  and returns a structured dict with "answer" and "sources" keys.
- This is the function you will expose through the API in Lab 08.

### Checkpoint
Run the script with three different queries and verify that each returns
a structured response with both an answer and a sources list.

```
python start/step5.py
```

---

## Recap

| Step | What You Did |
|------|-------------|
| Step 1 | Designed a system prompt to ground the LLM in policy context |
| Step 2 | Built context formatting with source attribution |
| Step 3 | Connected retrieval to generation for end-to-end RAG |
| Step 4 | Added edge case handling for out-of-scope and low-confidence queries |
| Step 5 | Combined everything into a single ask_policychat() function |

---

## Stretch Goals
- Experiment with different system prompt phrasings and observe how the LLM's behavior changes.
- Add a "confidence" field to the response that reflects the average similarity score of retrieved chunks.
- Implement a follow-up mechanism that suggests related questions based on the retrieved chunks.
