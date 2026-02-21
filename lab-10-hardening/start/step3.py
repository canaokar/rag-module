"""
Lab 10 - Step 3: Audit Logging

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
    """Append a log entry to the audit log file in JSON Lines format.

    Each line in the file should be a single JSON object.

    Args:
        log_entry: Dict containing the interaction details.
        log_file: Path to the audit log file.
    """
    # TODO: implement
    ...


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
    """Run the full RAG pipeline with audit logging.

    This function should:
    1. Retrieve relevant chunks
    2. Determine confidence level
    3. Generate a response
    4. Log the entire interaction with all required fields

    The log entry must include:
    - timestamp: ISO format timestamp
    - query: the original query
    - rewritten_query: the rewritten query (if applicable, else null)
    - retrieved_chunks: list of {chunk_id, score} for each retrieved chunk
    - generated_response: the response text
    - confidence_level: high, medium, or low

    Args:
        query: The user query.
        rewritten_query: The rewritten version of the query, if any.

    Returns:
        The generated response string.
    """
    # TODO: implement
    ...


def display_audit_log(log_file=AUDIT_LOG_FILE, last_n=5):
    """Read and display the last N entries from the audit log.

    Args:
        log_file: Path to the audit log file.
        last_n: Number of recent entries to display.
    """
    # TODO: implement
    ...


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
