"""
Lab 06, Step 3: Full Retrieval-to-Generation Flow

Connect the retrieval pipeline (from Lab 05) to the LLM to produce
grounded answers with citations.
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
# Requires AWS credentials (env vars or ~/.aws/credentials)
BEDROCK_MODEL_ID = "meta.llama3-8b-instruct-v1:0"
AWS_REGION = "us-east-1"  # Change to your region
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

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

    Returns:
        List of dicts with keys: content, heading, doc_title, score.
    """
    # TODO: implement
    # 1. Get the query embedding.
    # 2. Query policy_chunks joined with policy_documents.
    # 3. Order by cosine similarity, limit to top_k.
    # 4. Return list of dicts.
    pass


def format_context(chunks):
    """
    Format retrieved chunks into a numbered context string with source attribution.
    """
    # TODO: implement
    pass


def chat_with_llm(messages):
    """
    Call Bedrock LLM (Meta Llama 3) with the given messages list.

    The messages list uses the OpenAI-style format:
        [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]

    You need to convert this to Bedrock Converse API format:
        - System messages go in the `system` parameter as [{"text": "..."}]
        - Other messages go in `messages` as [{"role": "user", "content": [{"text": "..."}]}]

    Returns:
        The assistant's response content as a string.
    """
    # TODO: implement
    # 1. Separate system messages from conversation messages.
    # 2. Convert conversation messages to Bedrock format:
    #    {"role": "user", "content": [{"text": "..."}]}
    # 3. Call bedrock_client.converse(modelId=BEDROCK_MODEL_ID, system=..., messages=...)
    # 4. Return response["output"]["message"]["content"][0]["text"]
    pass


def ask(query, top_k=5):
    """
    Full RAG flow: retrieve context, format prompt, call LLM.

    Args:
        query: The user's question.
        top_k: Number of chunks to retrieve.

    Returns:
        The LLM's answer as a string.
    """
    # TODO: implement
    # 1. Retrieve chunks using retrieve_chunks().
    # 2. Format the context.
    # 3. Build messages: [system prompt, user message with context + query].
    # 4. Call chat_with_llm().
    # 5. Return the answer.
    pass


if __name__ == "__main__":
    query = "What are the KYC requirements for new customers?"
    print(f"Question: {query}\n")

    answer = ask(query)
    print("=== PolicyChat Answer ===")
    print(answer)
