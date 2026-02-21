"""
Lab 09 - Step 4: Comparing Metrics Across Configurations

Run evaluation with different values of K (3, 5, 10) and with/without
hybrid search to see how metrics change across configurations.
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


def load_golden_test_set(filepath):
    """Load the golden test set from a JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def retrieve_vector_only(query, top_k=5):
    """Retrieve doc_ids using vector search only.

    Args:
        query: The search query string.
        top_k: Number of results to retrieve.

    Returns:
        List of unique doc_id strings.
    """
    # TODO: implement
    ...


def retrieve_hybrid(query, top_k=5):
    """Retrieve doc_ids using hybrid search (vector + full-text).

    Combine vector similarity with full-text search using ts_rank.
    Use Reciprocal Rank Fusion (RRF) or a simple weighted combination
    to merge the two result sets.

    Args:
        query: The search query string.
        top_k: Number of results to retrieve.

    Returns:
        List of unique doc_id strings.
    """
    # TODO: implement
    ...


def precision_at_k(retrieved, relevant, k):
    """Calculate precision@K."""
    top_k = retrieved[:k]
    relevant_set = set(relevant)
    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return hits / k if k > 0 else 0.0


def recall_at_k(retrieved, relevant, k):
    """Calculate recall@K."""
    top_k = retrieved[:k]
    relevant_set = set(relevant)
    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return hits / len(relevant_set) if relevant_set else 0.0


def run_comparison(test_set, k_values, search_modes):
    """Run evaluation across all combinations of K and search mode.

    Args:
        test_set: List of test case dicts.
        k_values: List of K values to test (e.g., [3, 5, 10]).
        search_modes: Dict mapping mode name to retrieval function.

    Returns:
        A list of result dicts, one per configuration, with avg precision
        and recall.
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    test_set = load_golden_test_set("../data/golden_test_set.json")

    k_values = [3, 5, 10]
    search_modes = {
        "vector_only": retrieve_vector_only,
        "hybrid": retrieve_hybrid
    }

    print("Running comparison across configurations...\n")
    results = run_comparison(test_set, k_values, search_modes)

    print(f"{'Mode':<15} {'K':<5} {'Avg Precision':<18} {'Avg Recall':<18}")
    print("-" * 56)
    for r in results:
        print(f"{r['mode']:<15} {r['k']:<5} {r['avg_precision']:<18.3f} "
              f"{r['avg_recall']:<18.3f}")

    print("\nObservations:")
    print("- Higher K generally increases recall but may decrease precision")
    print("- Hybrid search can improve recall by catching keyword matches")
    print("  that vector search alone might miss")
