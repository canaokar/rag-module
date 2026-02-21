"""
Lab 05, Step 3 Solution: Similarity Score Threshold
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


def search_with_threshold(query, top_k=5, threshold=0.3):
    """
    Vector search that checks whether results meet a minimum similarity score.

    Args:
        query: The search query string.
        top_k: Number of top results to return.
        threshold: Minimum similarity score (0 to 1).

    Returns:
        Tuple of (results_list, message).
        - If results are above threshold: (list_of_dicts, None)
        - If below threshold: ([], "No confident match found for your query.")
    """
    query_embedding = get_embedding(query)
    embedding_json = json.dumps(query_embedding)

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
            """, (embedding_json, embedding_json, top_k))

            rows = cur.fetchall()

            if not rows:
                return [], "No results found in the database."

            results = []
            for row in rows:
                results.append({
                    "content": row[0],
                    "heading": row[1],
                    "score": float(row[2])
                })

            # Check the best (first) result against the threshold
            if results[0]["score"] < threshold:
                return [], "No confident match found for your query."

            # Filter out individual results below threshold
            filtered = [r for r in results if r["score"] >= threshold]
            return filtered, None
    finally:
        conn.close()


if __name__ == "__main__":
    # In-scope query -- should return results
    query_good = "What are the KYC requirements?"
    print(f"Query: {query_good}")
    results, msg = search_with_threshold(query_good)
    if msg:
        print(f"  Message: {msg}")
    else:
        print(f"  Found {len(results)} results (best score: {results[0]['score']:.4f})")
        for r in results:
            print(f"    [{r['score']:.4f}] {r['heading']}")

    print()

    # Out-of-scope query -- should trigger the threshold guard
    query_bad = "What is the weather today?"
    print(f"Query: {query_bad}")
    results, msg = search_with_threshold(query_bad)
    if msg:
        print(f"  Message: {msg}")
    else:
        print(f"  Found {len(results)} results (best score: {results[0]['score']:.4f})")
