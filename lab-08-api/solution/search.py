"""
Lab 08 Solution: Search Module
"""

import json
from utils import get_db_connection, get_embedding


def search_policies(query, filters=None, top_k=5):
    """
    Search policy chunks using vector similarity with optional metadata filters.
    """
    query_embedding = get_embedding(query)
    embedding_json = json.dumps(query_embedding)

    conditions = []
    params = [embedding_json]

    if filters:
        if filters.get("doc_type"):
            conditions.append("pd.doc_type = %s")
            params.append(filters["doc_type"])

        if filters.get("regulatory_body"):
            conditions.append("pd.regulatory_body = %s")
            params.append(filters["regulatory_body"])

        if filters.get("tag"):
            conditions.append("pc.metadata->'tags' @> %s::jsonb")
            params.append(json.dumps([filters["tag"]]))

        if filters.get("review_status"):
            conditions.append("pc.metadata->>'review_status' = %s")
            params.append(filters["review_status"])

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    params.extend([embedding_json, top_k])

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                    pc.content,
                    pc.heading,
                    1 - (pc.embedding <=> %s::vector) AS score,
                    pd.title AS doc_title,
                    pc.metadata
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
                    "content": row[0],
                    "heading": row[1],
                    "score": float(row[2]),
                    "doc_title": row[3],
                    "metadata": row[4] if row[4] else {}
                })
            return results
    finally:
        conn.close()


if __name__ == "__main__":
    results = search_policies("What are the KYC requirements?", top_k=3)
    if results:
        for r in results:
            print(f"[{r['score']:.4f}] {r['doc_title']} -- {r['heading']}")
    else:
        print("No results found.")
