"""
Lab 09 - Step 1: Retrieval Testing with a Golden Test Set (Solution)

Load the golden test set and run each query through the retrieval pipeline.
Compare retrieved doc_ids against expected doc_ids to measure retrieval quality.
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
    """Embed the query, run vector search on policy_chunks, join with
    policy_documents to get doc_ids."""
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


def evaluate_retrieval(test_set, top_k=5):
    """Run each query in the test set through retrieval and compare results
    against expected doc_ids."""
    results = []

    for test_case in test_set:
        query = test_case["query"]
        expected = set(test_case["expected_doc_ids"])

        try:
            retrieved = set(retrieve_doc_ids(query, top_k=top_k))
        except Exception as e:
            print(f"Error retrieving for query '{query}': {e}")
            retrieved = set()

        matches = expected & retrieved
        misses = expected - retrieved

        results.append({
            "query": query,
            "expected": list(expected),
            "retrieved": list(retrieved),
            "matches": list(matches),
            "misses": list(misses)
        })

    return results


if __name__ == "__main__":
    test_set = load_golden_test_set("../data/golden_test_set.json")
    print(f"Loaded {len(test_set)} test cases\n")

    results = evaluate_retrieval(test_set, top_k=5)

    print(f"{'Query':<55} {'Matches':<20} {'Misses':<20}")
    print("-" * 95)
    for r in results:
        query_short = r["query"][:52] + "..." if len(r["query"]) > 55 else r["query"]
        matches = ", ".join(r["matches"]) if r["matches"] else "None"
        misses = ", ".join(r["misses"]) if r["misses"] else "None"
        print(f"{query_short:<55} {matches:<20} {misses:<20}")

    total_expected = sum(len(r["expected"]) for r in results)
    total_matches = sum(len(r["matches"]) for r in results)
    print(f"\nOverall hit rate: {total_matches}/{total_expected} "
          f"({total_matches/total_expected*100:.1f}%)")
