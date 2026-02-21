"""
Lab 10 - Step 1: Query Rewriting (Solution)

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
    """Rewrite a vague or informal query into a precise banking policy question."""
    system_prompt = """You are a query rewriting assistant for a banking regulatory policy search system.

Your job is to take vague, informal, or incomplete queries and rewrite them as precise, specific banking policy questions.

Rules:
- If the query is about a recognizable banking topic, rewrite it as a specific policy question
- If the query is too vague to determine the intent (e.g., "can I do that?"), set rewritten to null
- Always respond with valid JSON in this exact format:

{"rewritten": "the rewritten query or null", "explanation": "brief explanation"}

Do not include any text outside the JSON object."""

    user_prompt = f"Rewrite this query: {query}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response_text = chat_with_llm(messages)

        # Try to parse JSON from the response
        # The LLM may include extra text, so try to find JSON in the response
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                result = json.loads(response_text[start:end])
            else:
                result = {
                    "rewritten": response_text.strip(),
                    "explanation": "Could not parse structured response"
                }

        # Normalize null/None
        if result.get("rewritten") in ("null", "None", ""):
            result["rewritten"] = None

        return result

    except Exception as e:
        return {
            "rewritten": None,
            "explanation": f"Error during rewriting: {e}"
        }


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
