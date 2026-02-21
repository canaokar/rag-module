"""
Lab 07, Step 1 Solution: Enrich Policy Chunks with JSONB Metadata
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

TAG_RULES = {
    "kyc": ["kyc", "compliance", "identity"],
    "know your customer": ["kyc", "compliance", "identity"],
    "anti-money laundering": ["aml", "compliance", "financial-crime"],
    "aml": ["aml", "compliance", "financial-crime"],
    "suspicious": ["aml", "reporting", "financial-crime"],
    "due diligence": ["kyc", "due-diligence", "compliance"],
    "loan": ["lending", "credit-risk"],
    "credit": ["lending", "credit-risk"],
    "mortgage": ["lending", "mortgage"],
    "data protection": ["data-privacy", "compliance"],
    "gdpr": ["data-privacy", "compliance"],
    "risk assessment": ["risk-management", "compliance"],
    "capital": ["capital-requirements", "regulatory"],
    "fraud": ["fraud", "financial-crime"],
    "transaction monitoring": ["aml", "monitoring"],
}

REVIEW_STATUSES = ["current", "under_review", "archived"]


def derive_tags(content):
    """
    Derive a list of tags for a chunk based on keyword matching.
    """
    content_lower = content.lower()
    tags = set()
    for keyword, associated_tags in TAG_RULES.items():
        if keyword in content_lower:
            tags.update(associated_tags)
    if not tags:
        tags.add("general")
    return sorted(tags)


def derive_review_status(chunk_index):
    """
    Assign a review status based on the chunk index to simulate variety.
    """
    if chunk_index % 5 == 0:
        return "archived"
    elif chunk_index % 3 == 0:
        return "under_review"
    else:
        return "current"


def enrich_metadata():
    """
    Update all policy_chunks rows with enriched JSONB metadata.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, content, chunk_index, metadata FROM policy_chunks")
            rows = cur.fetchall()
            print(f"Found {len(rows)} chunks to enrich.")

            updated = 0
            for row in rows:
                chunk_id, content, chunk_index, existing_metadata = row

                # Start with existing metadata or empty dict
                if existing_metadata and isinstance(existing_metadata, dict):
                    metadata = existing_metadata.copy()
                else:
                    metadata = {}

                # Derive and add new fields
                metadata["tags"] = derive_tags(content)
                metadata["review_status"] = derive_review_status(chunk_index)
                metadata["last_reviewed"] = "2024-06-15"
                metadata["enriched"] = True

                cur.execute(
                    "UPDATE policy_chunks SET metadata = %s WHERE id = %s",
                    (json.dumps(metadata), chunk_id)
                )
                updated += 1

            conn.commit()
            print(f"Successfully enriched {updated} chunks with JSONB metadata.")

            # Print a summary of tag distribution
            cur.execute("""
                SELECT
                    jsonb_array_elements_text(metadata->'tags') AS tag,
                    COUNT(*) AS cnt
                FROM policy_chunks
                WHERE metadata->'tags' IS NOT NULL
                GROUP BY tag
                ORDER BY cnt DESC
                LIMIT 10
            """)
            print("\nTag distribution (top 10):")
            for tag_row in cur.fetchall():
                print(f"  {tag_row[0]}: {tag_row[1]} chunks")

    finally:
        conn.close()


if __name__ == "__main__":
    enrich_metadata()
