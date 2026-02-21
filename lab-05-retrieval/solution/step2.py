"""
Lab 05, Step 2 Solution: Metadata-Filtered Vector Search
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
    query_embedding = get_embedding(query)

    # Build dynamic WHERE clause
    conditions = []
    params = []

    if doc_type:
        conditions.append("pd.doc_type = %s")
        params.append(doc_type)

    if regulatory_body:
        conditions.append("pd.regulatory_body = %s")
        params.append(regulatory_body)

    if effective_after:
        conditions.append("pd.effective_date > %s")
        params.append(effective_after)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    embedding_json = json.dumps(query_embedding)

    sql = f"""
        SELECT
            pc.content,
            pc.heading,
            1 - (pc.embedding <=> %s::vector) AS score,
            pd.title AS doc_title,
            pd.doc_type,
            pd.effective_date
        FROM policy_chunks pc
        JOIN policy_documents pd ON pc.document_id = pd.id
        {where_clause}
        ORDER BY pc.embedding <=> %s::vector
        LIMIT %s
    """

    all_params = [embedding_json] + params + [embedding_json, top_k]

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, all_params)
            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "content": row[0],
                    "heading": row[1],
                    "score": float(row[2]),
                    "doc_title": row[3],
                    "doc_type": row[4],
                    "effective_date": str(row[5]) if row[5] else None
                })
            return results
    finally:
        conn.close()


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
