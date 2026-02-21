"""
Lab 09 - Step 2: Retrieval Evaluation Metrics

Implement precision@K and recall@K for each query in the golden test set.
Print a formatted table showing per-query and average metrics.
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


def retrieve_doc_ids(query, top_k=5):
    """Embed the query, run vector search, return unique doc_ids."""
    embedding = get_embedding(query)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT pd.doc_id
        FROM policy_chunks pc
        JOIN policy_documents pd ON pc.document_id = pd.id
        ORDER BY pc.embedding <=> %s::vector
        LIMIT %s
    """, (str(embedding), top_k))
    doc_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return doc_ids


def precision_at_k(retrieved, relevant, k):
    """Calculate precision@K.

    Args:
        retrieved: List of retrieved doc_ids (ordered by rank).
        relevant: Set of relevant (expected) doc_ids.
        k: The cutoff rank.

    Returns:
        Precision score as a float between 0 and 1.
    """
    # TODO: implement
    ...


def recall_at_k(retrieved, relevant, k):
    """Calculate recall@K.

    Args:
        retrieved: List of retrieved doc_ids (ordered by rank).
        relevant: Set of relevant (expected) doc_ids.
        k: The cutoff rank.

    Returns:
        Recall score as a float between 0 and 1.
    """
    # TODO: implement
    ...


def evaluate_metrics(test_set, k=5):
    """Run retrieval for each query and compute precision@K and recall@K.

    Args:
        test_set: List of test case dicts.
        k: The cutoff rank for metrics.

    Returns:
        A list of result dicts with query, precision, recall.
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    test_set = load_golden_test_set("../data/golden_test_set.json")
    print(f"Evaluating {len(test_set)} queries at K=5\n")

    results = evaluate_metrics(test_set, k=5)

    print(f"{'Query':<55} {'Precision@5':<15} {'Recall@5':<15}")
    print("-" * 85)
    for r in results:
        query_short = r["query"][:52] + "..." if len(r["query"]) > 55 else r["query"]
        print(f"{query_short:<55} {r['precision']:<15.3f} {r['recall']:<15.3f}")

    avg_precision = sum(r["precision"] for r in results) / len(results)
    avg_recall = sum(r["recall"] for r in results) / len(results)
    print("-" * 85)
    print(f"{'AVERAGE':<55} {avg_precision:<15.3f} {avg_recall:<15.3f}")
