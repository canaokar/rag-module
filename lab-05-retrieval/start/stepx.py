"""
Lab 05, Stretch: Simple Re-Ranking

After initial retrieval, boost results by recency (newer effective_date
scores higher) and by exact keyword matches. Compare the original ranking
with the re-ranked order.
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
    # TODO: implement
    # Similar to step 1 vector search, but JOIN with policy_documents
    # to also return effective_date and title.
    pass


def rerank(results, query, recency_weight=0.2, keyword_weight=0.1):
    """
    Re-rank results by adding bonus scores for recency and keyword overlap.

    For recency: compute a 0-1 score where the most recent document gets 1.0
    and the oldest gets 0.0.  Use (doc_date - min_date) / (max_date - min_date).

    For keyword match: count how many query keywords appear (case-insensitive)
    in the result content, divided by total query keywords.

    Final score = original_score + recency_weight * recency_score
                                 + keyword_weight * keyword_score

    Args:
        results: List of result dicts from initial_retrieval.
        query: Original query string.
        recency_weight: Weight for recency bonus.
        keyword_weight: Weight for keyword bonus.

    Returns:
        Re-ranked list of dicts, each with added keys:
        recency_score, keyword_score, final_score.
    """
    # TODO: implement
    pass


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
