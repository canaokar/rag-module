"""
Lab 07, Step 1: Enrich Policy Chunks with JSONB Metadata

Update existing chunks in policy_chunks to add structured metadata
including tags, regulatory_body, review_status, and last_reviewed date.
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

# Keyword-to-tag mapping: if any keyword appears in the chunk content,
# assign the corresponding tags.
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

# Possible review statuses
REVIEW_STATUSES = ["current", "under_review", "archived"]


def derive_tags(content):
    """
    Derive a list of tags for a chunk based on keyword matching.

    Args:
        content: The chunk content text.

    Returns:
        A deduplicated sorted list of tag strings.
    """
    # TODO: implement
    # Loop through TAG_RULES. For each keyword, if it appears (case-insensitive)
    # in the content, add the associated tags. Return a sorted deduplicated list.
    pass


def derive_review_status(chunk_index):
    """
    Assign a review status based on the chunk index to simulate variety.

    Args:
        chunk_index: The chunk's position index.

    Returns:
        One of: "current", "under_review", "archived".
    """
    # TODO: implement
    # Use modular arithmetic to spread statuses across chunks.
    # For example: chunk_index % 5 == 0 -> "archived",
    #              chunk_index % 3 == 0 -> "under_review",
    #              else -> "current".
    pass


def enrich_metadata():
    """
    Update all policy_chunks rows with enriched JSONB metadata.

    For each chunk, set metadata to include:
        - tags: derived from content keywords
        - review_status: "current", "under_review", or "archived"
        - last_reviewed: a date string (e.g., "2024-06-15")
        - enriched: true (flag to indicate metadata has been added)
    """
    # TODO: implement
    # 1. Connect to the database.
    # 2. SELECT id, content, chunk_index, metadata FROM policy_chunks.
    # 3. For each row, derive tags and review_status.
    # 4. Merge new fields into existing metadata (preserve any existing keys).
    # 5. UPDATE the row with the enriched metadata JSONB.
    # 6. Commit and print a summary.
    pass


if __name__ == "__main__":
    enrich_metadata()
