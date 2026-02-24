"""
Lab 05, Step 4 Solution: Hybrid Search (Vector + Full-Text)
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
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def hybrid_search(query, top_k=5, vector_weight=0.7, text_weight=0.3):
    """
    Combine vector similarity with full-text search.

    The combined score is:
        vector_weight * vector_score + text_weight * text_score

    Args:
        query: The search query string.
        top_k: Number of top results to return.
        vector_weight: Weight for vector similarity (default 0.7).
        text_weight: Weight for full-text score (default 0.3).

    Returns:
        List of dicts with keys: content, heading, vector_score, text_score, combined_score.
    """
    query_embedding = get_embedding(query)
    embedding_json = json.dumps(query_embedding)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Backfill search_vector if not yet populated
            cur.execute("""
                UPDATE policy_chunks
                SET search_vector = to_tsvector('english', content)
                WHERE search_vector IS NULL
            """)
            conn.commit()

            cur.execute("""
                SELECT
                    content,
                    heading,
                    1 - (embedding <=> %s::vector) AS vector_score,
                    ts_rank(search_vector, plainto_tsquery('english', %s)) AS text_score,
                    (
                        %s * (1 - (embedding <=> %s::vector))
                        + %s * ts_rank(search_vector, plainto_tsquery('english', %s))
                    ) AS combined_score
                FROM policy_chunks
                ORDER BY combined_score DESC
                LIMIT %s
            """, (
                embedding_json,
                query,
                vector_weight, embedding_json,
                text_weight, query,
                top_k
            ))

            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "content": row[0],
                    "heading": row[1],
                    "vector_score": float(row[2]),
                    "text_score": float(row[3]),
                    "combined_score": float(row[4])
                })
            return results
    finally:
        conn.close()


if __name__ == "__main__":
    query = "suspicious transaction reporting requirements"
    print(f"Query: {query}\n")

    print("=== Hybrid search results ===")
    results = hybrid_search(query, top_k=5)
    if results:
        for i, r in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Heading:       {r['heading']}")
            print(f"  Vector score:  {r['vector_score']:.4f}")
            print(f"  Text score:    {r['text_score']:.4f}")
            print(f"  Combined:      {r['combined_score']:.4f}")
            print(f"  Content:       {r['content'][:150]}...")
            print()
    else:
        print("No results found.")
