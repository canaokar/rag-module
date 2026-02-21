"""
Lab 07, Step 4: GIN Indexes for JSONB Performance

Create GIN indexes on JSONB paths, then use EXPLAIN ANALYZE to compare
query plans and execution times with and without indexes.
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

    Args:
        cur: A psycopg2 cursor.
        sql: The SQL query to analyze.
        params: Optional query parameters.

    Returns:
        List of plan line strings.
    """
    # TODO: implement
    # Prepend "EXPLAIN ANALYZE " to the sql, execute, and fetchall.
    # Return the plan lines.
    pass


def drop_jsonb_indexes():
    """
    Drop the GIN indexes if they exist, so we can measure the 'without index' baseline.
    """
    # TODO: implement
    # DROP INDEX IF EXISTS idx_chunks_metadata_tags;
    # DROP INDEX IF EXISTS idx_chunks_metadata_status;
    pass


def create_jsonb_indexes():
    """
    Create GIN indexes on specific JSONB paths for faster filtering.

    Create two indexes:
    1. GIN index on metadata->'tags' for tag containment queries.
    2. B-tree index on (metadata->>'review_status') for equality checks.
    """
    # TODO: implement
    pass


def benchmark_query(label, cur, sql, params=None):
    """
    Run a query, print its EXPLAIN ANALYZE plan, and return the execution time.
    """
    # TODO: implement
    # 1. Call explain_query() to get the plan.
    # 2. Print the label and plan.
    # 3. Extract execution time from the last line of the plan.
    # 4. Return the time.
    pass


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
    benchmark_query("Tag query (no index)", cur, test_sql_tags)
    benchmark_query("Status query (no index)", cur, test_sql_status)

    # Phase 2: With indexes
    print("\n=== Phase 2: With GIN indexes ===\n")
    create_jsonb_indexes()
    benchmark_query("Tag query (with GIN index)", cur, test_sql_tags)
    benchmark_query("Status query (with B-tree index)", cur, test_sql_status)

    cur.close()
    conn.close()
    print("\nDone. Compare the query plans above to see the difference.")
