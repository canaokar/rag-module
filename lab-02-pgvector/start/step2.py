"""
Step 2: Generate embeddings for sample policy sentences and insert them
into the policy_chunks table.
"""

import psycopg2
import requests

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

OLLAMA_URL = "http://localhost:11434/api/embed"

SAMPLE_CHUNKS = [
    {
        "document_id": "POL-001",
        "chunk_index": 0,
        "content": "All customers must complete identity verification before account opening.",
        "heading": "Customer Due Diligence",
    },
    {
        "document_id": "POL-001",
        "chunk_index": 1,
        "content": "KYC procedures require valid government-issued photo identification.",
        "heading": "Customer Due Diligence",
    },
    {
        "document_id": "POL-002",
        "chunk_index": 0,
        "content": "The maximum loan-to-value ratio for residential mortgages is 85 percent.",
        "heading": "Mortgage Lending",
    },
    {
        "document_id": "POL-002",
        "chunk_index": 1,
        "content": "Anti-money laundering checks must be performed on all new accounts.",
        "heading": "AML Compliance",
    },
    {
        "document_id": "POL-003",
        "chunk_index": 0,
        "content": "Suspicious activity reports must be filed with the NCA within 14 days.",
        "heading": "Suspicious Activity Reporting",
    },
]


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def insert_chunk(cursor, chunk, embedding):
    """Insert a single chunk with its embedding into the policy_chunks table.

    Args:
        cursor: A psycopg2 cursor object.
        chunk: A dict with keys: document_id, chunk_index, content, heading.
        embedding: A list of floats (the embedding vector).
    """
    # TODO: implement
    # Hint: Use INSERT INTO policy_chunks (document_id, chunk_index, content,
    #       heading, embedding, metadata) VALUES (...)
    # Pass the embedding as a string like '[0.1, 0.2, ...]' or use %s with
    # the list converted to a string.
    ...


if __name__ == "__main__":
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    print(f"Inserting {len(SAMPLE_CHUNKS)} chunks with embeddings...\n")
    for i, chunk in enumerate(SAMPLE_CHUNKS):
        print(f"  [{i+1}/{len(SAMPLE_CHUNKS)}] Embedding: {chunk['content'][:50]}...")
        embedding = get_embedding(chunk["content"])
        insert_chunk(cur, chunk, embedding)
        print(f"    Inserted into policy_chunks.")

    # Verify
    cur.execute("SELECT COUNT(*) FROM policy_chunks;")
    count = cur.fetchone()[0]
    print(f"\nTotal rows in policy_chunks: {count}")

    cur.close()
    conn.close()
    print("Done.")
