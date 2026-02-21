"""
Lab 06, Step 3 Solution: Full Retrieval-to-Generation Flow
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


def get_embedding(text):
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def retrieve_chunks(query, top_k=5):
    """
    Retrieve the top_k most similar chunks for the given query.
    """
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
                LIMIT %s
            """, (embedding_json, embedding_json, top_k))

            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append({
                    "content": row[0],
                    "heading": row[1],
                    "doc_title": row[2],
                    "score": float(row[3])
                })
            return results
    finally:
        conn.close()


def format_context(chunks):
    """
    Format retrieved chunks into a numbered context string with source attribution.
    """
    parts = []
    for i, chunk in enumerate(chunks, 1):
        part = (
            f"[{i}] (Source: {chunk['doc_title']})\n"
            f"{chunk['heading']}\n"
            f"{chunk['content']}"
        )
        parts.append(part)
    return "\n\n".join(parts)


def chat_with_llm(messages):
    """
    Call Ollama LLM with the given messages list.
    """
    response = requests.post(OLLAMA_CHAT_URL, json={
        "model": "llama3.2",
        "messages": messages,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["message"]["content"]


def ask(query, top_k=5):
    """
    Full RAG flow: retrieve context, format prompt, call LLM.
    """
    # 1. Retrieve relevant chunks
    chunks = retrieve_chunks(query, top_k=top_k)

    if not chunks:
        return "No relevant policy documents were found for your query."

    # 2. Format context
    context_str = format_context(chunks)

    # 3. Build messages
    user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    # 4. Call LLM
    answer = chat_with_llm(messages)
    return answer


if __name__ == "__main__":
    query = "What are the KYC requirements for new customers?"
    print(f"Question: {query}\n")

    answer = ask(query)
    print("=== PolicyChat Answer ===")
    print(answer)
