"""
Lab 10 - Step 3: Audit Logging (Solution)

Create functions that log every RAG interaction to a JSON Lines file
for compliance and debugging purposes.
"""

import psycopg2
import requests
import json
import os
from datetime import datetime, timezone

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050"
}

OLLAMA_URL = "http://localhost:11434/api/embed"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
AUDIT_LOG_FILE = "audit_log.jsonl"


def get_embedding(text):
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def chat_with_llm(messages):
    response = requests.post(OLLAMA_CHAT_URL, json={
        "model": "llama3.2",
        "messages": messages,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["message"]["content"]


def log_interaction(log_entry, log_file=AUDIT_LOG_FILE):
    """Append a log entry to the audit log file in JSON Lines format."""
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def retrieve_with_scores(query, top_k=5):
    """Retrieve chunks with their similarity scores."""
    embedding = get_embedding(query)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT pc.id, pc.content, 1 - (pc.embedding <=> %s::vector) AS score
        FROM policy_chunks pc
        ORDER BY pc.embedding <=> %s::vector
        LIMIT %s
    """, (str(embedding), str(embedding), top_k))
    results = [{"chunk_id": row[0], "content": row[1], "score": row[2]}
               for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results


def determine_confidence(scores):
    """Determine confidence level based on similarity scores."""
    if not scores:
        return "low"
    avg = sum(scores) / len(scores)
    if avg > 0.5:
        return "high"
    elif avg >= 0.3:
        return "medium"
    else:
        return "low"


def rag_pipeline_with_logging(query, rewritten_query=None):
    """Run the full RAG pipeline with audit logging."""
    search_query = rewritten_query if rewritten_query else query

    # Retrieve
    chunks = retrieve_with_scores(search_query)
    scores = [c["score"] for c in chunks]
    confidence = determine_confidence(scores)

    # Generate response
    if confidence == "low":
        response = ("I'm not confident I have relevant information to answer "
                    "this question. Please try rephrasing or contact the "
                    "compliance team directly.")
    else:
        context = "\n\n".join(c["content"] for c in chunks)
        messages = [
            {"role": "system", "content": "You are a banking policy assistant. "
             "Answer questions using only the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        try:
            response = chat_with_llm(messages)
        except Exception as e:
            response = f"Error generating response: {e}"

        if confidence == "medium":
            response += ("\n\nNote: this answer is based on partially matching "
                         "documents and may not be complete.")

    # Build log entry
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "rewritten_query": rewritten_query,
        "retrieved_chunks": [
            {"chunk_id": c["chunk_id"], "score": round(c["score"], 4)}
            for c in chunks
        ],
        "generated_response": response,
        "confidence_level": confidence,
    }

    # Write to log
    log_interaction(log_entry)

    return response


def display_audit_log(log_file=AUDIT_LOG_FILE, last_n=5):
    """Read and display the last N entries from the audit log."""
    if not os.path.exists(log_file):
        print("No audit log file found.")
        return

    with open(log_file, "r") as f:
        lines = f.readlines()

    entries = lines[-last_n:] if len(lines) > last_n else lines

    for i, line in enumerate(entries):
        entry = json.loads(line.strip())
        print(f"\nEntry {i + 1}:")
        print(f"  Timestamp:  {entry['timestamp']}")
        print(f"  Query:      {entry['query']}")
        if entry.get("rewritten_query"):
            print(f"  Rewritten:  {entry['rewritten_query']}")
        print(f"  Confidence: {entry['confidence_level']}")
        print(f"  Chunks:     {len(entry['retrieved_chunks'])} retrieved")
        for chunk in entry["retrieved_chunks"][:3]:
            print(f"    - chunk_id={chunk['chunk_id']}, "
                  f"score={chunk['score']}")
        response_preview = entry["generated_response"][:120]
        print(f"  Response:   {response_preview}...")


if __name__ == "__main__":
    # Clean up any existing log file for a fresh start
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)

    test_queries = [
        "What are the KYC requirements?",
        "How do I report a suspicious transaction?",
        "What is the capital adequacy ratio?",
    ]

    print("Running RAG pipeline with audit logging\n")
    for query in test_queries:
        print(f"Query: {query}")
        response = rag_pipeline_with_logging(query)
        print(f"Response: {response[:150]}...")
        print("-" * 60)

    print("\n\nAudit Log Contents:")
    print("=" * 60)
    display_audit_log()
