"""
Lab 09 - Step 4: Comparing Metrics Across Configurations (Solution)

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
    """Retrieve doc_ids using vector search only."""
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


def retrieve_hybrid(query, top_k=5):
    """Retrieve doc_ids using hybrid search (vector + full-text).

    Uses Reciprocal Rank Fusion (RRF) to combine vector similarity
    and full-text search rankings.
    """
    embedding = get_embedding(query)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Vector search results with rank
    cur.execute("""
        WITH vector_results AS (
            SELECT pc.document_id, pd.doc_id,
                   ROW_NUMBER() OVER (ORDER BY pc.embedding <=> %s::vector) AS vec_rank
            FROM policy_chunks pc
            JOIN policy_documents pd ON pc.document_id = pd.id
            LIMIT %s
        ),
        text_results AS (
            SELECT pc.document_id, pd.doc_id,
                   ROW_NUMBER() OVER (ORDER BY ts_rank(pc.search_vector,
                       plainto_tsquery('english', %s)) DESC) AS text_rank
            FROM policy_chunks pc
            JOIN policy_documents pd ON pc.document_id = pd.id
            WHERE pc.search_vector @@ plainto_tsquery('english', %s)
            LIMIT %s
        ),
        combined AS (
            SELECT doc_id,
                   COALESCE(1.0 / (60 + vec_rank), 0) AS vec_rrf
            FROM vector_results
            UNION ALL
            SELECT doc_id,
                   COALESCE(1.0 / (60 + text_rank), 0) AS text_rrf
            FROM text_results
        )
        SELECT doc_id, SUM(vec_rrf) AS rrf_score
        FROM combined
        GROUP BY doc_id
        ORDER BY rrf_score DESC
        LIMIT %s
    """, (str(embedding), top_k * 2, query, query, top_k * 2, top_k))

    doc_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return doc_ids


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
    """Run evaluation across all combinations of K and search mode."""
    results = []

    for mode_name, retrieval_fn in search_modes.items():
        for k in k_values:
            precisions = []
            recalls = []

            for test_case in test_set:
                query = test_case["query"]
                relevant = test_case["expected_doc_ids"]

                try:
                    retrieved = retrieval_fn(query, top_k=k)
                except Exception as e:
                    print(f"Error with {mode_name} K={k}: {e}")
                    retrieved = []

                p = precision_at_k(retrieved, relevant, k)
                r = recall_at_k(retrieved, relevant, k)
                precisions.append(p)
                recalls.append(r)

            avg_p = sum(precisions) / len(precisions) if precisions else 0.0
            avg_r = sum(recalls) / len(recalls) if recalls else 0.0

            results.append({
                "mode": mode_name,
                "k": k,
                "avg_precision": avg_p,
                "avg_recall": avg_r
            })

            print(f"  Completed: {mode_name} K={k} "
                  f"(P={avg_p:.3f}, R={avg_r:.3f})")

    return results


if __name__ == "__main__":
    test_set = load_golden_test_set("../data/golden_test_set.json")

    k_values = [3, 5, 10]
    search_modes = {
        "vector_only": retrieve_vector_only,
        "hybrid": retrieve_hybrid
    }

    print("Running comparison across configurations...\n")
    results = run_comparison(test_set, k_values, search_modes)

    print(f"\n{'Mode':<15} {'K':<5} {'Avg Precision':<18} {'Avg Recall':<18}")
    print("-" * 56)
    for r in results:
        print(f"{r['mode']:<15} {r['k']:<5} {r['avg_precision']:<18.3f} "
              f"{r['avg_recall']:<18.3f}")

    print("\nObservations:")
    print("- Higher K generally increases recall but may decrease precision")
    print("- Hybrid search can improve recall by catching keyword matches")
    print("  that vector search alone might miss")
