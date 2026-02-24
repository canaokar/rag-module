"""
Lab 05, Step 4: Hybrid Search (Vector + Full-Text)

Combine cosine-similarity vector search with PostgreSQL full-text search
using the search_vector tsvector column and a weighted scoring formula.
"""

import psycopg2
import requests
import json

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


def hybrid_search(query, top_k=5, vector_weight=0.7, text_weight=0.3):
    """
    Combine vector similarity with full-text search.

    The combined score is:
        vector_weight * vector_score + text_weight * text_score

    where:
        vector_score = 1 - (embedding <=> query_vector)
        text_score   = ts_rank(search_vector, plainto_tsquery('english', query))

    Args:
        query: The search query string.
        top_k: Number of top results to return.
        vector_weight: Weight for vector similarity (default 0.7).
        text_weight: Weight for full-text score (default 0.3).

    Returns:
        List of dicts with keys: content, heading, vector_score, text_score, combined_score.
    """
    # TODO: implement
    # 0. After connecting to the DB, backfill search_vector for any rows where it is NULL:
    #    UPDATE policy_chunks SET search_vector = to_tsvector('english', content)
    #    WHERE search_vector IS NULL
    # 1. Get the embedding for the query.
    # 2. Write a SQL query that computes both scores:
    #    - vector_score: 1 - (embedding <=> cast_query_vector)
    #    - text_score: ts_rank(search_vector, plainto_tsquery('english', %s))
    #    - combined_score: %s * vector_score + %s * text_score
    # 3. ORDER BY combined_score DESC, LIMIT top_k.
    # 4. Return results as a list of dicts.
    pass


if __name__ == "__main__":
    query = "suspicious transaction reporting requirements"
    print(f"Query: {query}\n")

    print("=== Hybrid search results ===")
    results = hybrid_search(query, top_k=5)
    if results:
        for i, r in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Heading:       {r['heading']}")
            print(f"  Vector score:  {r['vector_score']:.4f}")
            print(f"  Text score:    {r['text_score']:.4f}")
            print(f"  Combined:      {r['combined_score']:.4f}")
            print(f"  Content:       {r['content'][:150]}...")
            print()
    else:
        print("No results found.")
