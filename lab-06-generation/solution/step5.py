"""
Lab 06, Step 5 Solution: Full RAG Loop -- ask_policychat()
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


def ask_policychat(query):
    """
    Full RAG pipeline for PolicyChat.

    Returns:
        Dict with keys:
            - "answer": The LLM's response string, or a fallback message.
            - "sources": List of unique source document titles used.
    """
    # 1. Check out-of-scope
    query_lower = query.lower()
    for keyword in OUT_OF_SCOPE_KEYWORDS:
        if keyword in query_lower:
            return {
                "answer": (
                    "I am PolicyChat, a banking regulatory policy assistant. "
                    "Your question appears to be outside the scope of banking "
                    "policy and compliance. Please ask a question related to "
                    "regulatory policies or banking guidelines."
                ),
                "sources": []
            }

    # 2. Embed and retrieve
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
                JOIN policy_documents pd ON pc.document_id = pd.id
                ORDER BY pc.embedding <=> %s::vector
                LIMIT 5
            """, (embedding_json, embedding_json))

            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        return {
            "answer": "No relevant policy documents were found for your query.",
            "sources": []
        }

    # Build results and apply threshold
    results = []
    for row in rows:
        results.append({
            "content": row[0],
            "heading": row[1],
            "doc_title": row[2],
            "score": float(row[3])
        })

    # 3. Threshold check
    if results[0]["score"] < SIMILARITY_THRESHOLD:
        return {
            "answer": (
                "I could not find sufficiently relevant policy documents to "
                "answer your question. Please try rephrasing or ask about a "
                "specific banking regulatory topic."
            ),
            "sources": []
        }

    # Filter below threshold
    results = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]

    # 4. Format context
    parts = []
    for i, chunk in enumerate(results, 1):
        part = (
            f"[{i}] (Source: {chunk['doc_title']})\n"
            f"{chunk['heading']}\n"
            f"{chunk['content']}"
        )
        parts.append(part)
    context_str = "\n\n".join(parts)

    # 5. Build messages and call LLM
    user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    answer = chat_with_llm(messages)
    sources = list(set(r["doc_title"] for r in results))

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":
    test_queries = [
        "What are the KYC requirements for new customers?",
        "What are the AML reporting thresholds?",
        "How often must customer risk assessments be reviewed?",
    ]

    for query in test_queries:
        print(f"{'=' * 60}")
        print(f"Question: {query}\n")
        result = ask_policychat(query)
        print(f"Answer:\n{result['answer']}\n")
        print(f"Sources: {result['sources']}")
        print()
