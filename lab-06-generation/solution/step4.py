"""
Lab 06, Step 4 Solution: Edge Case Handling
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

SYSTEM_PROMPT = """You are PolicyChat, a banking regulatory policy assistant.
Answer questions using ONLY the provided context from policy documents.
Always cite the source document title for each claim you make.
If the context does not contain enough information to answer, say so clearly.
Use professional, precise language appropriate for banking compliance."""

SIMILARITY_THRESHOLD = 0.3

OUT_OF_SCOPE_KEYWORDS = [
    "weather", "sports", "recipe", "movie", "music", "game",
    "celebrity", "joke", "story", "poem"
]


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


def is_out_of_scope(query):
    """
    Check if the query is clearly outside banking policy scope.
    """
    query_lower = query.lower()
    for keyword in OUT_OF_SCOPE_KEYWORDS:
        if keyword in query_lower:
            return True
    return False


def retrieve_with_threshold(query, top_k=5, threshold=None):
    """
    Retrieve chunks and check against the similarity threshold.
    """
    if threshold is None:
        threshold = SIMILARITY_THRESHOLD

    query_embedding = get_embedding(query)
    embedding_json = json.dumps(query_embedding)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    pc.content,
                    pc.heading,
                    pd.title AS doc_title,
                    1 - (pc.embedding <=> %s::vector) AS score
                FROM policy_chunks pc
                JOIN policy_documents pd ON pc.document_id = pd.doc_id
                ORDER BY pc.embedding <=> %s::vector
                LIMIT %s
            """, (embedding_json, embedding_json, top_k))

            rows = cur.fetchall()

            if not rows:
                return [], "no_match"

            results = []
            for row in rows:
                results.append({
                    "content": row[0],
                    "heading": row[1],
                    "doc_title": row[2],
                    "score": float(row[3])
                })

            # Check best result against threshold
            if results[0]["score"] < threshold:
                return [], "low_confidence"

            # Filter individual results below threshold
            filtered = [r for r in results if r["score"] >= threshold]
            return filtered, "ok"
    finally:
        conn.close()


def handle_query(query):
    """
    Process a query with full edge-case handling.
    """
    # 1. Check out-of-scope
    if is_out_of_scope(query):
        return {
            "answer": (
                "I am PolicyChat, a banking regulatory policy assistant. "
                "Your question appears to be outside the scope of banking "
                "policy and compliance. Please ask a question related to "
                "regulatory policies, compliance procedures, or banking "
                "guidelines."
            ),
            "status": "out_of_scope",
            "sources": []
        }

    # 2. Retrieve with threshold
    results, status = retrieve_with_threshold(query)

    if status == "no_match":
        return {
            "answer": (
                "I could not find any relevant policy documents matching "
                "your query. Please try rephrasing your question or check "
                "that the relevant policies have been ingested into the system."
            ),
            "status": "no_match",
            "sources": []
        }

    if status == "low_confidence":
        return {
            "answer": (
                "I found some documents, but none are sufficiently relevant "
                "to provide a reliable answer. The closest matches had low "
                "similarity scores. Please try a more specific question "
                "related to banking regulatory policies."
            ),
            "status": "low_confidence",
            "sources": []
        }

    # 3. Format context and call LLM
    parts = []
    for i, chunk in enumerate(results, 1):
        part = (
            f"[{i}] (Source: {chunk['doc_title']})\n"
            f"{chunk['heading']}\n"
            f"{chunk['content']}"
        )
        parts.append(part)
    context_str = "\n\n".join(parts)

    user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    answer = chat_with_llm(messages)
    sources = list(set(r["doc_title"] for r in results))

    return {
        "answer": answer,
        "status": "ok",
        "sources": sources
    }


if __name__ == "__main__":
    test_queries = [
        "What are the KYC requirements for new customers?",
        "What is the weather going to be tomorrow?",
        "Tell me about quantum computing advances",
    ]

    for query in test_queries:
        print(f"Query: {query}")
        result = handle_query(query)
        print(f"  Status: {result['status']}")
        print(f"  Answer: {result['answer'][:200]}")
        if result.get("sources"):
            print(f"  Sources: {result['sources']}")
        print()
