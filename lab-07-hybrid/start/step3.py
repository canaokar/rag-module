"""
Lab 07, Step 3: Hybrid Queries -- Vector + Relational + JSONB

Combine vector similarity search with relational filters and JSONB
conditions in a single query. Compare the result set size against
vector-only search to show how filters narrow results.
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


def vector_only_search(query, top_k=10):
    """
    Baseline: pure vector search with no filters.

    Returns:
        List of dicts with keys: id, heading, score, tags, review_status, doc_title.
    """
    # TODO: implement
    # Join policy_chunks with policy_documents.
    # Order by cosine distance, limit to top_k.
    # Include metadata tags and review_status in the output.
    pass


def hybrid_filtered_search(query, top_k=10, tag=None, review_status=None, doc_type=None):
    """
    Vector search combined with JSONB metadata filters and relational filters.

    Args:
        query: Search query string.
        top_k: Max results.
        tag: If provided, only return chunks whose metadata tags contain this tag.
        review_status: If provided, filter by metadata review_status.
        doc_type: If provided, filter by policy_documents.doc_type.

    Returns:
        List of dicts with keys: id, heading, score, tags, review_status, doc_title.
    """
    # TODO: implement
    # 1. Get the query embedding.
    # 2. Build a SQL query joining policy_chunks with policy_documents.
    # 3. Dynamically add WHERE conditions for tag, review_status, doc_type.
    #    - tag filter: pc.metadata->'tags' @> %s::jsonb
    #    - review_status filter: pc.metadata->>'review_status' = %s
    #    - doc_type filter: pd.doc_type = %s
    # 4. Order by cosine distance, limit to top_k.
    # 5. Return results.
    pass


if __name__ == "__main__":
    query = "loan approval process"

    print(f"Query: {query}\n")

    print("=== Vector-only search (no filters) ===")
    results_all = vector_only_search(query, top_k=10)
    print(f"Results: {len(results_all)}")
    for r in results_all[:5]:
        print(f"  [{r['score']:.4f}] {r['heading']} | tags={r.get('tags')} | status={r.get('review_status')}")

    print("\n=== Filtered: tag='lending' AND review_status='current' ===")
    results_filtered = hybrid_filtered_search(query, top_k=10, tag="lending", review_status="current")
    print(f"Results: {len(results_filtered)}")
    for r in results_filtered[:5]:
        print(f"  [{r['score']:.4f}] {r['heading']} | tags={r.get('tags')} | status={r.get('review_status')}")

    print(f"\nFiltering narrowed results from {len(results_all)} to {len(results_filtered)}")
