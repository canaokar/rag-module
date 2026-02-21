"""
Step 5: Verify the ingestion pipeline.
Count total documents, total chunks, and run a test similarity query.
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


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def count_documents(cursor):
    """Count total documents in the policy_documents table.

    Args:
        cursor: A psycopg2 cursor object.

    Returns:
        An integer count.
    """
    # TODO: implement
    ...


def count_chunks(cursor):
    """Count total chunks in the policy_chunks table.

    Args:
        cursor: A psycopg2 cursor object.

    Returns:
        An integer count.
    """
    # TODO: implement
    ...


def similarity_search(cursor, query_embedding, top_k=3):
    """Find the top_k most similar chunks to the query embedding.

    Args:
        cursor: A psycopg2 cursor object.
        query_embedding: A list of floats.
        top_k: Number of results to return.

    Returns:
        A list of tuples: (document_id, heading, content, distance).
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    # Count documents and chunks
    doc_count = count_documents(cur)
    chunk_count = count_chunks(cur)
    print(f"Total documents: {doc_count}")
    print(f"Total chunks: {chunk_count}")

    # Test similarity query
    query = "What are the KYC requirements?"
    print(f"\nTest query: \"{query}\"")
    query_embedding = get_embedding(query)

    results = similarity_search(cur, query_embedding, top_k=3)
    print(f"\nTop {len(results)} results:")
    for i, (doc_id, heading, content, distance) in enumerate(results):
        similarity = 1 - distance
        print(f"\n  {i+1}. [{doc_id}] {heading} (similarity: {similarity:.4f})")
        print(f"     {content[:150]}...")

    cur.close()
    conn.close()
    print("\nVerification complete.")
