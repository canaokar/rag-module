"""
Step 4 Solution: Use EXPLAIN ANALYZE to compare query performance with and
without indexes.
"""

import psycopg2
import requests

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

OLLAMA_URL = "http://localhost:11434/api/embed"


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def run_explain_analyze(cursor, query_embedding, top_k=3):
    """Run EXPLAIN ANALYZE on a similarity search query."""
    cursor.execute(
        """
        EXPLAIN ANALYZE
        SELECT content, heading, embedding <=> %s::vector AS distance
        FROM policy_chunks
        ORDER BY distance
        LIMIT %s
        """,
        (str(query_embedding), top_k),
    )
    return [row[0] for row in cursor.fetchall()]


def drop_indexes(cursor):
    """Drop all indexes on the embedding column."""
    cursor.execute("DROP INDEX IF EXISTS idx_policy_chunks_hnsw;")
    cursor.execute("DROP INDEX IF EXISTS idx_policy_chunks_ivfflat;")


def create_hnsw_index(cursor):
    """Recreate the HNSW index on the embedding column."""
    cursor.execute("""
        CREATE INDEX idx_policy_chunks_hnsw
        ON policy_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)


if __name__ == "__main__":
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    query = "What are the AML reporting requirements?"
    print(f"Query: \"{query}\"")
    query_embedding = get_embedding(query)

    # Step A: Query WITH index
    print("\n--- Query WITH index ---")
    plan_with = run_explain_analyze(cur, query_embedding)
    for line in plan_with:
        print(f"  {line}")

    # Step B: Drop indexes and query WITHOUT index
    print("\n--- Dropping indexes ---")
    drop_indexes(cur)
    print("Indexes dropped.")

    print("\n--- Query WITHOUT index ---")
    plan_without = run_explain_analyze(cur, query_embedding)
    for line in plan_without:
        print(f"  {line}")

    # Step C: Recreate index
    print("\n--- Recreating HNSW index ---")
    create_hnsw_index(cur)
    print("Index recreated.")

    # Step D: Query WITH index again
    print("\n--- Query WITH index (after recreate) ---")
    plan_after = run_explain_analyze(cur, query_embedding)
    for line in plan_after:
        print(f"  {line}")

    cur.close()
    conn.close()
    print("\nDone. Compare the execution times above.")
    print("With a small dataset the difference may be minimal,")
    print("but indexes become critical as the table grows to thousands of rows.")
