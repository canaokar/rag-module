"""
Lab 05, Step 1: Basic Vector Similarity Search

Embed a query and find the most similar policy chunks using cosine distance.
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
    """Get embedding vector for a text string using Ollama."""
    # TODO: implement
    # Send a POST request to OLLAMA_URL with model "bge-m3" and input text.
    # Return the first embedding from the response.
    pass


def vector_search(query, top_k=5):
    """
    Perform basic vector similarity search on policy_chunks.

    Args:
        query: The search query string.
        top_k: Number of top results to return.

    Returns:
        List of dicts with keys: content, heading, score.
        Score is computed as 1 - (embedding <=> query_vector).
    """
    # TODO: implement
    # 1. Get the embedding for the query.
    # 2. Connect to the database.
    # 3. Execute a SQL query on policy_chunks:
    #    - SELECT content, heading, and similarity score
    #    - Use ORDER BY embedding <=> %s (cast query vector as vector)
    #    - Use 1 - (embedding <=> ...) to compute the similarity score
    #    - LIMIT to top_k results
    # 4. Return results as a list of dicts.
    pass


if __name__ == "__main__":
    query = "What are the KYC requirements?"
    print(f"Searching for: {query}\n")

    results = vector_search(query, top_k=5)

    if results:
        for i, r in enumerate(results, 1):
            print(f"--- Result {i} (score: {r['score']:.4f}) ---")
            print(f"Heading: {r['heading']}")
            print(f"Content: {r['content'][:200]}...")
            print()
    else:
        print("No results found.")
