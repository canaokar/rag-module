"""
Lab 08, Search Module: Vector search with optional metadata filters.
"""

import json
from utils import get_db_connection, get_embedding


def search_policies(query, filters=None, top_k=5):
    """
    Search policy chunks using vector similarity with optional metadata filters.

    Args:
        query: The search query string.
        filters: Optional dict with keys:
            - doc_type: Filter by document type (e.g., "AML").
            - regulatory_body: Filter by regulatory body.
            - tag: Filter by metadata tag.
            - review_status: Filter by metadata review_status.
        top_k: Number of top results to return.

    Returns:
        List of dicts with keys: content, heading, score, doc_title, metadata.
    """
    # TODO: implement
    # 1. Get the query embedding using get_embedding().
    # 2. Build a SQL query joining policy_chunks with policy_documents.
    # 3. Dynamically add WHERE conditions based on filters dict:
    #    - doc_type: pd.doc_type = %s
    #    - regulatory_body: pd.regulatory_body = %s
    #    - tag: pc.metadata->'tags' @> %s::jsonb
    #    - review_status: pc.metadata->>'review_status' = %s
    # 4. Order by cosine distance, limit to top_k.
    # 5. Return results as a list of dicts.
    pass


if __name__ == "__main__":
    results = search_policies("What are the KYC requirements?", top_k=3)
    if results:
        for r in results:
            print(f"[{r['score']:.4f}] {r['doc_title']} -- {r['heading']}")
    else:
        print("No results found.")
