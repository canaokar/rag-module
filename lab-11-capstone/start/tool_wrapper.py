"""
Lab 11 - Tool Wrapper: Wrapping RAG as a Callable Tool

Package the RAG pipeline as a tool with a standard schema that an AI agent
can discover and invoke. This bridges the RAG module to the Agents module.
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

TOOL_SCHEMA = {
    "name": "policy_search",
    "description": "Search banking regulatory policies and return relevant information with citations.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The policy question to search for"
            },
            "filters": {
                "type": "object",
                "description": "Optional filters to narrow search",
                "properties": {
                    "doc_type": {"type": "string", "description": "Filter by document type"},
                    "regulatory_body": {"type": "string", "description": "Filter by regulatory body"},
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sources to search: policies, updates"
                    }
                }
            }
        },
        "required": ["query"]
    }
}


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


def policy_search_tool(query, filters=None):
    """Execute a policy search and return structured results.

    This function wraps the RAG pipeline as a tool that an AI agent can call.
    It should:
    1. Determine which sources to search based on filters
    2. Embed the query and search the relevant tables
    3. Generate an answer from the retrieved context
    4. Return a structured result with answer, sources, and confidence

    Args:
        query: The policy question to search for.
        filters: Optional dict with doc_type, regulatory_body, and/or sources.

    Returns:
        dict with keys:
        - answer: The generated answer string
        - sources: List of source dicts with doc_id, title, score
        - confidence: "high", "medium", or "low"
    """
    # TODO: implement
    ...


def execute_tool(tool_name, arguments):
    """Dispatcher that routes tool calls to the appropriate function.

    This is the entry point that an agent framework would call. It maps
    tool names to their implementations and passes through arguments.

    Args:
        tool_name: Name of the tool to execute (e.g. "policy_search")
        arguments: Dict of arguments to pass to the tool

    Returns:
        Tool execution result as a dict
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    # Demonstrate the tool schema
    print("Tool Schema:")
    print(json.dumps(TOOL_SCHEMA, indent=2))

    # Test tool execution
    print("\nExecuting tool...")
    result = execute_tool("policy_search", {
        "query": "What are the KYC requirements for new customers?"
    })
    print(f"\nResult: {json.dumps(result, indent=2)}")

    # Test with filters
    result_filtered = execute_tool("policy_search", {
        "query": "AML reporting thresholds",
        "filters": {"doc_type": "AML Policy", "sources": ["policies", "updates"]}
    })
    print(f"\nFiltered result: {json.dumps(result_filtered, indent=2)}")
