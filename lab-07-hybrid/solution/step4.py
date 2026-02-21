"""
Lab 07, Step 4 Solution: GIN Indexes for JSONB Performance
"""

import psycopg2
import json
import time

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050"
}


def explain_query(cur, sql, params=None):
    """
    Run EXPLAIN ANALYZE on a query and return the plan as a list of strings.
    """
    explain_sql = "EXPLAIN ANALYZE " + sql
    cur.execute(explain_sql, params)
    rows = cur.fetchall()
    return [row[0] for row in rows]


def drop_jsonb_indexes():
    """
    Drop the GIN indexes if they exist.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("DROP INDEX IF EXISTS idx_chunks_metadata_tags")
            cur.execute("DROP INDEX IF EXISTS idx_chunks_metadata_status")
            print("Dropped existing JSONB indexes (if any).")
    finally:
        conn.close()


def create_jsonb_indexes():
    """
    Create GIN indexes on specific JSONB paths.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            # GIN index for tag containment queries
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_metadata_tags
                ON policy_chunks USING GIN ((metadata->'tags'))
            """)
            print("Created GIN index on metadata->'tags'.")

            # B-tree index for review_status equality checks
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_metadata_status
                ON policy_chunks ((metadata->>'review_status'))
            """)
            print("Created B-tree index on metadata->>'review_status'.")
    finally:
        conn.close()


def benchmark_query(label, cur, sql, params=None):
    """
    Run a query, print its EXPLAIN ANALYZE plan, and return the execution time.
    """
    plan = explain_query(cur, sql, params)
    print(f"\n--- {label} ---")
    for line in plan:
        print(f"  {line}")

    # Extract execution time from the last line
    last_line = plan[-1]
    exec_time = None
    if "Execution Time" in last_line:
        # Format: "Execution Time: 0.123 ms"
        parts = last_line.split(":")
        if len(parts) >= 2:
            time_str = parts[1].strip().replace(" ms", "")
            try:
                exec_time = float(time_str)
            except ValueError:
                pass
    return exec_time


if __name__ == "__main__":
    test_sql_tags = """
        SELECT id, heading
        FROM policy_chunks
        WHERE metadata->'tags' @> '["aml"]'::jsonb
    """

    test_sql_status = """
        SELECT id, heading
        FROM policy_chunks
        WHERE metadata->>'review_status' = 'current'
    """

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    # Phase 1: Without indexes
    print("=== Phase 1: Without GIN indexes ===\n")
    drop_jsonb_indexes()

    # Run the query once to warm the cache, then benchmark
    cur.execute("SELECT 1")  # warm connection
    t1 = benchmark_query("Tag query (no index)", cur, test_sql_tags)
    t2 = benchmark_query("Status query (no index)", cur, test_sql_status)

    # Phase 2: With indexes
    print("\n\n=== Phase 2: With GIN indexes ===\n")
    create_jsonb_indexes()

    # Force PostgreSQL to recognize the new indexes
    cur.execute("ANALYZE policy_chunks")

    t3 = benchmark_query("Tag query (with GIN index)", cur, test_sql_tags)
    t4 = benchmark_query("Status query (with B-tree index)", cur, test_sql_status)

    # Summary
    print("\n=== Summary ===")
    if t1 is not None and t3 is not None:
        print(f"Tag query:    {t1:.3f} ms (no index) -> {t3:.3f} ms (with index)")
    if t2 is not None and t4 is not None:
        print(f"Status query: {t2:.3f} ms (no index) -> {t4:.3f} ms (with index)")

    cur.close()
    conn.close()
    print("\nDone. Compare the query plans above to see the difference.")
