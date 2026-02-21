"""
Lab 07, Step 2 Solution: Pure JSONB Queries
"""

import psycopg2
import json

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050"
}


def find_by_tag(tag):
    """
    Find all chunks whose metadata 'tags' array contains the given tag.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Use the @> containment operator
            cur.execute("""
                SELECT id, heading, LEFT(content, 100) AS content_preview, metadata->'tags' AS tags
                FROM policy_chunks
                WHERE metadata->'tags' @> %s::jsonb
                ORDER BY id
            """, (json.dumps([tag]),))

            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "heading": row[1],
                    "content_preview": row[2],
                    "tags": row[3]
                })
            return results
    finally:
        conn.close()


def find_by_review_status(status):
    """
    Find chunks with a specific review_status in their metadata.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, heading, metadata->>'review_status' AS review_status
                FROM policy_chunks
                WHERE metadata->>'review_status' = %s
                ORDER BY id
            """, (status,))

            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "heading": row[1],
                    "review_status": row[2]
                })
            return results
    finally:
        conn.close()


def find_by_multiple_conditions(tag=None, review_status=None):
    """
    Combine multiple JSONB conditions with AND.
    """
    conditions = []
    params = []

    if tag:
        conditions.append("metadata->'tags' @> %s::jsonb")
        params.append(json.dumps([tag]))

    if review_status:
        conditions.append("metadata->>'review_status' = %s")
        params.append(review_status)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, heading, metadata->'tags' AS tags,
                       metadata->>'review_status' AS review_status
                FROM policy_chunks
                {where_clause}
                ORDER BY id
            """, params)

            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "heading": row[1],
                    "tags": row[2],
                    "review_status": row[3]
                })
            return results
    finally:
        conn.close()


if __name__ == "__main__":
    print("=== Chunks tagged 'aml' ===")
    results = find_by_tag("aml")
    print(f"Found {len(results)} chunks")
    for r in results[:3]:
        print(f"  [{r['id']}] {r['heading']} -- tags: {r['tags']}")

    print("\n=== Chunks with review_status 'current' ===")
    results = find_by_review_status("current")
    print(f"Found {len(results)} chunks")
    for r in results[:3]:
        print(f"  [{r['id']}] {r['heading']}")

    print("\n=== Chunks tagged 'compliance' AND status 'current' ===")
    results = find_by_multiple_conditions(tag="compliance", review_status="current")
    print(f"Found {len(results)} chunks")
    for r in results[:3]:
        print(f"  [{r['id']}] {r['heading']} -- {r['review_status']}")
