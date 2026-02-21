"""
Lab 10 - Step 1: Query Rewriting

Use the Ollama LLM to reformulate vague or informal queries into precise
banking policy questions before sending them to the retrieval pipeline.
"""

import requests
import json

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"


def chat_with_llm(messages):
    response = requests.post(OLLAMA_CHAT_URL, json={
        "model": "llama3.2",
        "messages": messages,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["message"]["content"]


def rewrite_query(query):
    """Rewrite a vague or informal query into a precise banking policy question.

    If the query is too vague or lacks sufficient context to rewrite meaningfully,
    return None and explain why.

    Args:
        query: The original user query (may be vague or informal).

    Returns:
        A dict with:
        - "rewritten": The rewritten query string, or None if too vague
        - "explanation": Brief explanation of what was changed and why
    """
    # TODO: implement
    # Hint: Create a system prompt that instructs the LLM to act as a query
    # rewriting assistant for a banking policy search system. Ask it to return
    # a JSON object with "rewritten" and "explanation" fields.
    ...


if __name__ == "__main__":
    test_queries = [
        "what about loans?",
        "AML stuff",
        "can I do that?",
        "tell me about customer checks",
    ]

    print("Query Rewriting Test\n")
    print(f"{'Original Query':<40} {'Rewritten Query'}")
    print("-" * 90)

    for query in test_queries:
        result = rewrite_query(query)
        rewritten = result["rewritten"] if result["rewritten"] else "[TOO VAGUE]"
        print(f"{query:<40} {rewritten}")
        print(f"{'':40} Reason: {result['explanation']}\n")
