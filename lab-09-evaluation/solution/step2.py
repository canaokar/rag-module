"""
Lab 09 - Step 2: Retrieval Evaluation Metrics (Solution)

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
        JOIN policy_documents pd ON pc.document_id = pd.doc_id
        ORDER BY pc.embedding <=> %s::vector
        LIMIT %s
    """, (str(embedding), top_k))
    doc_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return doc_ids


def precision_at_k(retrieved, relevant, k):
    """Calculate precision@K.

    Precision@K = (number of relevant docs in top-K results) / K
    """
    top_k = retrieved[:k]
    relevant_set = set(relevant)
    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return hits / k if k > 0 else 0.0


def recall_at_k(retrieved, relevant, k):
    """Calculate recall@K.

    Recall@K = (number of relevant docs in top-K results) / (total relevant docs)
    """
    top_k = retrieved[:k]
    relevant_set = set(relevant)
    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return hits / len(relevant_set) if relevant_set else 0.0


def evaluate_metrics(test_set, k=5):
    """Run retrieval for each query and compute precision@K and recall@K."""
    results = []

    for test_case in test_set:
        query = test_case["query"]
        relevant = test_case["expected_doc_ids"]

        try:
            retrieved = retrieve_doc_ids(query, top_k=k)
        except Exception as e:
            print(f"Error retrieving for query '{query}': {e}")
            retrieved = []

        p = precision_at_k(retrieved, relevant, k)
        r = recall_at_k(retrieved, relevant, k)

        results.append({
            "query": query,
            "precision": p,
            "recall": r,
            "retrieved": retrieved,
            "relevant": relevant
        })

    return results


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
