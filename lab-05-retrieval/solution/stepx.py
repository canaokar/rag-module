"""
Lab 05, Stretch Solution: Simple Re-Ranking
"""

import psycopg2
import requests
import json
from datetime import date

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


def initial_retrieval(query, top_k=10):
    """
    Retrieve top_k results using basic vector search, including effective_date.

    Returns list of dicts with: content, heading, score, effective_date, doc_title.
    """
    query_embedding = get_embedding(query)
    embedding_json = json.dumps(query_embedding)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    pc.content,
                    pc.heading,
                    1 - (pc.embedding <=> %s::vector) AS score,
                    pd.effective_date,
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
                    "content": row[0],
                    "heading": row[1],
                    "score": float(row[2]),
                    "effective_date": row[3],
                    "doc_title": row[4]
                })
            return results
    finally:
        conn.close()


def rerank(results, query, recency_weight=0.2, keyword_weight=0.1):
    """
    Re-rank results by adding bonus scores for recency and keyword overlap.

    Final score = original_score + recency_weight * recency_score
                                 + keyword_weight * keyword_score
    """
    if not results:
        return results

    # Compute recency scores
    dates = [r["effective_date"] for r in results if r["effective_date"]]
    if dates and len(set(dates)) > 1:
        min_date = min(dates)
        max_date = max(dates)
        date_range = (max_date - min_date).days
    else:
        date_range = 0

    # Compute keyword overlap
    query_keywords = set(query.lower().split())

    for r in results:
        # Recency score: 0 to 1
        if date_range > 0 and r["effective_date"]:
            r["recency_score"] = (r["effective_date"] - min_date).days / date_range
        else:
            r["recency_score"] = 0.5  # neutral if all dates are the same

        # Keyword score: fraction of query keywords found in content
        content_lower = r["content"].lower()
        matches = sum(1 for kw in query_keywords if kw in content_lower)
        r["keyword_score"] = matches / len(query_keywords) if query_keywords else 0.0

        # Final combined score
        r["final_score"] = (
            r["score"]
            + recency_weight * r["recency_score"]
            + keyword_weight * r["keyword_score"]
        )

    # Sort by final_score descending
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results


if __name__ == "__main__":
    query = "KYC customer due diligence"
    print(f"Query: {query}\n")

    results = initial_retrieval(query, top_k=8)

    if not results:
        print("No results found.")
    else:
        print("=== Before re-ranking ===")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['score']:.4f}] {r['heading']} ({r['effective_date']})")

        reranked = rerank(results, query)

        print("\n=== After re-ranking ===")
        for i, r in enumerate(reranked, 1):
            print(f"  {i}. [final={r['final_score']:.4f} | vec={r['score']:.4f} "
                  f"| recency={r['recency_score']:.2f} | kw={r['keyword_score']:.2f}] "
                  f"{r['heading']} ({r['effective_date']})")
