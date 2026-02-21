"""
Lab 05, Step 3: Similarity Score Threshold

Return a "no confident match" message when the best result falls below a
configurable similarity threshold.
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
        threshold: Minimum similarity score (0 to 1). If the best result
                   scores below this, return an empty list and a warning message.

    Returns:
        Tuple of (results_list, message).
        - If results are above threshold: (list_of_dicts, None)
        - If below threshold: ([], "No confident match found for your query.")
    """
    # TODO: implement
    # 1. Get the embedding for the query.
    # 2. Run the vector search (same as step 1).
    # 3. Check the score of the best (first) result.
    # 4. If best score < threshold, return ([], "No confident match found ...").
    # 5. Otherwise filter out any individual results below threshold and return them.
    pass


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
