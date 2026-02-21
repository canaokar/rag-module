"""
Lab 05, Step 1 Solution: Basic Vector Similarity Search
"""

import psycopg2
import requests
import json

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050"
}

OLLAMA_URL = "http://localhost:11434/api/embed"


def get_embedding(text):
    """Get embedding vector for a text string using Ollama."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def vector_search(query, top_k=5):
    """
    Perform basic vector similarity search on policy_chunks.

    Args:
        query: The search query string.
        top_k: Number of top results to return.

    Returns:
        List of dicts with keys: content, heading, score.
    """
    query_embedding = get_embedding(query)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    content,
                    heading,
                    1 - (embedding <=> %s::vector) AS score
                FROM policy_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (json.dumps(query_embedding), json.dumps(query_embedding), top_k))

            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "content": row[0],
                    "heading": row[1],
                    "score": float(row[2])
                })
            return results
    finally:
        conn.close()


if __name__ == "__main__":
    query = "What are the KYC requirements?"
    print(f"Searching for: {query}\n")

    results = vector_search(query, top_k=5)

    if results:
        for i, r in enumerate(results, 1):
            print(f"--- Result {i} (score: {r['score']:.4f}) ---")
            print(f"Heading: {r['heading']}")
            print(f"Content: {r['content'][:200]}...")
            print()
    else:
        print("No results found.")
