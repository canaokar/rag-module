"""
Lab 05, Step 2: Metadata-Filtered Vector Search

Add optional filters (doc_type, regulatory_body, effective_date) to the
vector similarity search by joining policy_chunks with policy_documents.
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


def filtered_vector_search(query, top_k=5, doc_type=None, regulatory_body=None, effective_after=None):
    """
    Vector search with optional metadata filters.

    Args:
        query: The search query string.
        top_k: Number of top results to return.
        doc_type: Filter by document type (e.g., "AML").
        regulatory_body: Filter by regulatory body.
        effective_after: Filter for documents effective after this date (YYYY-MM-DD string).

    Returns:
        List of dicts with keys: content, heading, score, doc_title, doc_type, effective_date.
    """
    # TODO: implement
    # 1. Get the embedding for the query.
    # 2. Build a SQL query that JOINs policy_chunks with policy_documents
    #    on policy_chunks.document_id = policy_documents.id.
    # 3. Dynamically build a WHERE clause:
    #    - If doc_type is provided, add: pd.doc_type = %s
    #    - If regulatory_body is provided, add: pd.regulatory_body = %s
    #    - If effective_after is provided, add: pd.effective_date > %s
    #    Use parameterized queries (never string-format user input).
    # 4. ORDER BY embedding <=> query_vector, LIMIT top_k.
    # 5. Return results as a list of dicts.
    pass


if __name__ == "__main__":
    query = "anti-money laundering reporting"

    print("=== Unfiltered search ===")
    results = filtered_vector_search(query, top_k=3)
    if results:
        for r in results:
            print(f"  [{r['score']:.4f}] {r['doc_title']} -- {r['heading']}")
    else:
        print("  No results.")

    print("\n=== Filtered: doc_type=AML ===")
    results = filtered_vector_search(query, top_k=3, doc_type="AML")
    if results:
        for r in results:
            print(f"  [{r['score']:.4f}] {r['doc_title']} -- {r['heading']}")
    else:
        print("  No results.")

    print("\n=== Filtered: effective_after=2024-01-01 ===")
    results = filtered_vector_search(query, top_k=3, effective_after="2024-01-01")
    if results:
        for r in results:
            print(f"  [{r['score']:.4f}] {r['doc_title']} ({r['effective_date']}) -- {r['heading']}")
    else:
        print("  No results.")
