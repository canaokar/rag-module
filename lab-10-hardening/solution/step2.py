"""
Lab 10 - Step 2: Confidence Thresholds and Tiered Responses (Solution)

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
    """Retrieve chunks with their similarity scores."""
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
    """Determine confidence level based on similarity scores."""
    if not scores:
        return "low"

    avg_score = sum(scores) / len(scores)

    if avg_score > 0.5:
        return "high"
    elif avg_score >= 0.3:
        return "medium"
    else:
        return "low"


def generate_tiered_response(query, chunks, confidence):
    """Generate a response appropriate for the confidence level."""
    if confidence == "low":
        return ("I'm not confident I have relevant information to answer this "
                "question. Please try rephrasing or contact the compliance "
                "team directly.")

    # Build context from retrieved chunks
    context = "\n\n".join(c["content"] for c in chunks)

    messages = [
        {"role": "system", "content": "You are a banking policy assistant. "
         "Answer questions using only the provided context. "
         "Be precise and cite specific policy details."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]

    try:
        answer = chat_with_llm(messages)
    except Exception as e:
        return f"Error generating response: {e}"

    if confidence == "medium":
        caveat = ("\n\nNote: this answer is based on partially matching "
                  "documents and may not be complete.")
        answer += caveat

    return answer


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
