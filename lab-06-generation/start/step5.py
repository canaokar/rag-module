"""
Lab 06, Step 5: Full RAG Loop -- ask_policychat()

Combine everything into a single clean function that returns a structured
response with answer and sources.
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


def ask_policychat(query):
    """
    Full RAG pipeline for PolicyChat.

    Steps:
    1. Check if the query is out of scope.
    2. Embed the query and retrieve top chunks with threshold check.
    3. Format retrieved chunks as context with source attribution.
    4. Build messages with SYSTEM_PROMPT and call the LLM.
    5. Extract source document titles from the retrieved chunks.

    Args:
        query: The user's question about banking policy.

    Returns:
        Dict with keys:
            - "answer": The LLM's response string, or a fallback message.
            - "sources": List of unique source document titles used.
    """
    # TODO: implement
    pass


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
