"""
Lab 07, Step 3 Solution: Hybrid Queries -- Vector + Relational + JSONB
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
    """
    query_embedding = get_embedding(query)
    embedding_json = json.dumps(query_embedding)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    pc.id,
                    pc.heading,
                    1 - (pc.embedding <=> %s::vector) AS score,
                    pc.metadata->'tags' AS tags,
                    pc.metadata->>'review_status' AS review_status,
                    pd.title AS doc_title
                FROM policy_chunks pc
                JOIN policy_documents pd ON pc.document_id = pd.id
                ORDER BY pc.embedding <=> %s::vector
                LIMIT %s
            """, (embedding_json, embedding_json, top_k))

            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "heading": row[1],
                    "score": float(row[2]),
                    "tags": row[3],
                    "review_status": row[4],
                    "doc_title": row[5]
                })
            return results
    finally:
        conn.close()


def hybrid_filtered_search(query, top_k=10, tag=None, review_status=None, doc_type=None):
    """
    Vector search combined with JSONB metadata filters and relational filters.
    """
    query_embedding = get_embedding(query)
    embedding_json = json.dumps(query_embedding)

    conditions = []
    params = [embedding_json]

    if tag:
        conditions.append("pc.metadata->'tags' @> %s::jsonb")
        params.append(json.dumps([tag]))

    if review_status:
        conditions.append("pc.metadata->>'review_status' = %s")
        params.append(review_status)

    if doc_type:
        conditions.append("pd.doc_type = %s")
        params.append(doc_type)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    params.extend([embedding_json, top_k])

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                    pc.id,
                    pc.heading,
                    1 - (pc.embedding <=> %s::vector) AS score,
                    pc.metadata->'tags' AS tags,
                    pc.metadata->>'review_status' AS review_status,
                    pd.title AS doc_title
                FROM policy_chunks pc
                JOIN policy_documents pd ON pc.document_id = pd.id
                {where_clause}
                ORDER BY pc.embedding <=> %s::vector
                LIMIT %s
            """, params)

            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "heading": row[1],
                    "score": float(row[2]),
                    "tags": row[3],
                    "review_status": row[4],
                    "doc_title": row[5]
                })
            return results
    finally:
        conn.close()


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
