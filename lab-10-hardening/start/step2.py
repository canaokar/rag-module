"""
Lab 10 - Step 2: Confidence Thresholds and Tiered Responses

Implement a system that checks similarity scores from retrieval and
returns tiered responses based on confidence level.
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


def retrieve_with_scores(query, top_k=5):
    """Retrieve chunks with their similarity scores.

    Args:
        query: The search query.
        top_k: Number of results to return.

    Returns:
        List of dicts with content, score, and chunk_id.
    """
    embedding = get_embedding(query)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT pc.id, pc.content, 1 - (pc.embedding <=> %s::vector) AS score
        FROM policy_chunks pc
        ORDER BY pc.embedding <=> %s::vector
        LIMIT %s
    """, (str(embedding), str(embedding), top_k))
    results = [{"chunk_id": row[0], "content": row[1], "score": row[2]}
               for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results


def determine_confidence(scores):
    """Determine confidence level based on similarity scores.

    Uses the average of the top scores to determine confidence:
    - High: average score > 0.5
    - Medium: average score between 0.3 and 0.5
    - Low: average score < 0.3

    Args:
        scores: List of similarity scores (floats).

    Returns:
        A string: "high", "medium", or "low"
    """
    # TODO: implement
    ...


def generate_tiered_response(query, chunks, confidence):
    """Generate a response appropriate for the confidence level.

    - High confidence: Generate a full answer from the retrieved chunks.
    - Medium confidence: Generate an answer but append a caveat noting the
      answer is based on partially matching documents.
    - Low confidence: Return a message stating insufficient confidence and
      suggesting the user rephrase or contact the compliance team.

    Args:
        query: The original query.
        chunks: Retrieved chunks with content and scores.
        confidence: The confidence level string.

    Returns:
        The response string.
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    test_queries = [
        "What are the KYC verification requirements for new customers?",
        "How does quantum computing affect banking policy?",
        "What is the process for reporting suspicious transactions?",
    ]

    print("Tiered Response Test\n")
    for query in test_queries:
        print(f"Query: {query}")

        chunks = retrieve_with_scores(query)
        scores = [c["score"] for c in chunks]
        confidence = determine_confidence(scores)

        print(f"Top scores: {[f'{s:.3f}' for s in scores[:3]]}")
        print(f"Confidence: {confidence}")

        response = generate_tiered_response(query, chunks, confidence)
        print(f"Response: {response[:200]}...")
        print("-" * 80 + "\n")
