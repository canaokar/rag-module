"""
Lab 09 - Step 3: LLM-as-Judge Evaluation

Run the full RAG pipeline for each query, then ask the LLM to score
the generated answer on faithfulness and relevance.
"""

import psycopg2
import requests
import json
import re

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050"
}

OLLAMA_URL = "http://localhost:11434/api/embed"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"


def get_embedding(text):
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def chat_with_llm(messages):
    response = requests.post(OLLAMA_CHAT_URL, json={
        "model": "llama3.2",
        "messages": messages,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["message"]["content"]


def load_golden_test_set(filepath):
    """Load the golden test set from a JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def retrieve_chunks(query, top_k=5):
    """Embed the query and retrieve the top-K chunks with their content."""
    embedding = get_embedding(query)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT pc.content, 1 - (pc.embedding <=> %s::vector) AS score
        FROM policy_chunks pc
        ORDER BY pc.embedding <=> %s::vector
        LIMIT %s
    """, (str(embedding), str(embedding), top_k))
    results = [{"content": row[0], "score": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results


def generate_answer(query, chunks):
    """Generate an answer using retrieved chunks as context."""
    context = "\n\n".join(c["content"] for c in chunks)
    messages = [
        {"role": "system", "content": "You are a banking policy assistant. "
         "Answer questions using only the provided context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]
    return chat_with_llm(messages)


def judge_answer(query, answer, context_chunks):
    """Use the LLM to score an answer on faithfulness and relevance.

    The judge should evaluate:
    - Faithfulness (0-5): Is the answer supported by the provided context?
    - Relevance (0-5): Does the answer address the question asked?

    Args:
        query: The original question.
        answer: The generated answer to evaluate.
        context_chunks: The retrieved context chunks used to generate the answer.

    Returns:
        A dict with "faithfulness" and "relevance" scores (integers 0-5).
    """
    # TODO: implement
    # Hint: Build a judge prompt that asks the LLM to return scores in a
    # parseable format like "Faithfulness: X/5, Relevance: Y/5"
    # Then parse the numeric values from the response.
    ...


def parse_scores(judge_response):
    """Parse faithfulness and relevance scores from the judge LLM response.

    Expected format in response: "Faithfulness: X/5, Relevance: Y/5"

    Args:
        judge_response: The raw text response from the judge LLM.

    Returns:
        A dict with "faithfulness" and "relevance" as integers.
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    test_set = load_golden_test_set("../data/golden_test_set.json")
    print(f"Running LLM-as-Judge on {len(test_set)} queries\n")

    results = []
    for i, test_case in enumerate(test_set):
        query = test_case["query"]
        print(f"[{i+1}/{len(test_set)}] Evaluating: {query[:60]}...")

        chunks = retrieve_chunks(query)
        answer = generate_answer(query, chunks)
        scores = judge_answer(query, answer, chunks)

        results.append({
            "query": query,
            "faithfulness": scores["faithfulness"],
            "relevance": scores["relevance"]
        })

    print(f"\n{'Query':<55} {'Faithfulness':<15} {'Relevance':<15}")
    print("-" * 85)
    for r in results:
        query_short = r["query"][:52] + "..." if len(r["query"]) > 55 else r["query"]
        print(f"{query_short:<55} {r['faithfulness']}/5{'':<10} {r['relevance']}/5")

    avg_faith = sum(r["faithfulness"] for r in results) / len(results)
    avg_rel = sum(r["relevance"] for r in results) / len(results)
    print("-" * 85)
    print(f"{'AVERAGE':<55} {avg_faith:.1f}/5{'':<9} {avg_rel:.1f}/5")
