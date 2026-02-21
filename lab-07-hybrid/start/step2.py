"""
Lab 07, Step 2: Pure JSONB Queries

Query policy_chunks using JSONB operators to filter by tags, regulatory
body, and review status stored in the metadata column.
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

    Use the JSONB containment operator: metadata->'tags' @> '["aml"]'::jsonb

    Args:
        tag: A tag string, e.g., "aml".

    Returns:
        List of dicts with keys: id, heading, content_preview, tags.
    """
    # TODO: implement
    pass


def find_by_review_status(status):
    """
    Find chunks with a specific review_status in their metadata.

    Use: metadata->>'review_status' = %s

    Args:
        status: One of "current", "under_review", "archived".

    Returns:
        List of dicts with keys: id, heading, review_status.
    """
    # TODO: implement
    pass


def find_by_multiple_conditions(tag=None, review_status=None):
    """
    Combine multiple JSONB conditions with AND.

    Args:
        tag: Optional tag to filter by.
        review_status: Optional review status to filter by.

    Returns:
        List of dicts with keys: id, heading, tags, review_status.
    """
    # TODO: implement
    # Build WHERE conditions dynamically, similar to Lab 05 Step 2.
    pass


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
