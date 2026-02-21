"""
Step 5 Solution: Verify the ingestion pipeline.
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
    """Count total documents in the policy_documents table."""
    cursor.execute("SELECT COUNT(*) FROM policy_documents;")
    return cursor.fetchone()[0]


def count_chunks(cursor):
    """Count total chunks in the policy_chunks table."""
    cursor.execute("SELECT COUNT(*) FROM policy_chunks;")
    return cursor.fetchone()[0]


def similarity_search(cursor, query_embedding, top_k=3):
    """Find the top_k most similar chunks to the query embedding."""
    cursor.execute(
        """
        SELECT document_id, heading, content, embedding <=> %s::vector AS distance
        FROM policy_chunks
        ORDER BY distance
        LIMIT %s
        """,
        (str(query_embedding), top_k),
    )
    return cursor.fetchall()


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

    # Show chunks per document
    cur.execute("""
        SELECT document_id, COUNT(*) as chunk_count
        FROM policy_chunks
        GROUP BY document_id
        ORDER BY document_id;
    """)
    print("\nChunks per document:")
    for doc_id, count in cur.fetchall():
        print(f"  {doc_id}: {count} chunks")

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
