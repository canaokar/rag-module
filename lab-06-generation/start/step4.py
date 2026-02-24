"""
Lab 06, Step 4: Edge Case Handling

Handle three edge cases gracefully:
1. No relevant results (low similarity scores)
2. Out-of-scope questions (not about banking policy)
3. Ambiguous queries that need clarification
"""

import boto3
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

# --- Bedrock configuration ---
BEDROCK_MODEL_ID = "meta.llama3-8b-instruct-v1:0"
AWS_REGION = "us-east-1"  # Change to your region
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

SYSTEM_PROMPT = """You are PolicyChat, a banking regulatory policy assistant.
Answer questions using ONLY the provided context from policy documents.
Always cite the source document title for each claim you make.
If the context does not contain enough information to answer, say so clearly.
Use professional, precise language appropriate for banking compliance."""

SIMILARITY_THRESHOLD = 0.3

# Topics that are clearly outside the scope of banking policy
OUT_OF_SCOPE_KEYWORDS = [
    "weather", "sports", "recipe", "movie", "music", "game",
    "celebrity", "joke", "story", "poem"
]


def get_embedding(text):
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def chat_with_llm(messages):
    """Call Bedrock LLM. Converts OpenAI-style messages to Bedrock Converse format."""
    system_parts = []
    converse_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_parts.append({"text": msg["content"]})
        else:
            converse_messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })
    response = bedrock_client.converse(
        modelId=BEDROCK_MODEL_ID,
        system=system_parts,
        messages=converse_messages,
    )
    return response["output"]["message"]["content"][0]["text"]


def is_out_of_scope(query):
    """
    Check if the query is clearly outside banking policy scope.

    Args:
        query: The user's question.

    Returns:
        True if the query appears out of scope, False otherwise.
    """
    # TODO: implement
    # Check if any OUT_OF_SCOPE_KEYWORDS appear in the lowercased query.
    pass


def retrieve_with_threshold(query, top_k=5, threshold=None):
    """
    Retrieve chunks and check against the similarity threshold.

    Args:
        query: The search query.
        top_k: Number of results.
        threshold: Minimum similarity score (uses SIMILARITY_THRESHOLD if None).

    Returns:
        Tuple of (results_list, status).
        status is one of: "ok", "no_match", "low_confidence"
    """
    # TODO: implement
    # 1. Get embedding and search policy_chunks.
    # 2. If no results at all, return ([], "no_match").
    # 3. If best score < threshold, return ([], "low_confidence").
    # 4. Filter out results below threshold, return (filtered, "ok").
    pass


def handle_query(query):
    """
    Process a query with full edge-case handling.

    Args:
        query: The user's question.

    Returns:
        Dict with keys: "answer", "status", "sources".
        status is one of: "ok", "out_of_scope", "no_match", "low_confidence".
    """
    # TODO: implement
    # 1. Check if out of scope. If so, return a polite refusal.
    # 2. Retrieve with threshold.
    # 3. If status is "no_match" or "low_confidence", return an appropriate message
    #    without calling the LLM (no need to hallucinate).
    # 4. If status is "ok", format context, call LLM, return the answer with sources.
    pass


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
