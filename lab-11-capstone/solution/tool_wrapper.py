"""
Lab 11 - Tool Wrapper: Wrapping RAG as a Callable Tool (Solution)

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


def search_policies(query, embedding, top_k=5, doc_type=None, regulatory_body=None):
    """Search the policy_chunks table with optional filters."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Build the query with optional filters
    where_clauses = []
    params = [str(embedding), str(embedding)]

    if doc_type:
        where_clauses.append("pd.doc_type = %s")
        params.append(doc_type)

    if regulatory_body:
        where_clauses.append("pd.regulatory_body = %s")
        params.append(regulatory_body)

    where_str = ""
    if where_clauses:
        where_str = "WHERE " + " AND ".join(where_clauses)

    params.append(top_k)

    cur.execute(f"""
        SELECT pc.content,
               1 - (pc.embedding <=> %s::vector) AS score,
               pd.doc_id,
               pd.title
        FROM policy_chunks pc
        JOIN policy_documents pd ON pc.document_id = pd.doc_id
        {where_str}
        ORDER BY pc.embedding <=> %s::vector
        LIMIT %s
    """, params)

    results = [
        {"content": row[0], "score": row[1], "doc_id": row[2],
         "title": row[3], "source_type": "policy"}
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()
    return results


def search_updates(query, embedding, top_k=5, regulatory_body=None):
    """Search the regulatory_updates table with optional filters."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'regulatory_updates'
        )
    """)
    if not cur.fetchone()[0]:
        cur.close()
        conn.close()
        return []

    where_clauses = []
    params = [str(embedding), str(embedding)]

    if regulatory_body:
        where_clauses.append("regulatory_body = %s")
        params.append(regulatory_body)

    where_str = ""
    if where_clauses:
        where_str = "WHERE " + " AND ".join(where_clauses)

    params.append(top_k)

    cur.execute(f"""
        SELECT content,
               1 - (embedding <=> %s::vector) AS score,
               doc_id,
               title
        FROM regulatory_updates
        {where_str}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, params)

    results = [
        {"content": row[0], "score": row[1], "doc_id": row[2],
         "title": row[3], "source_type": "update"}
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()
    return results


def determine_confidence(all_results):
    """Determine confidence level from search results."""
    if not all_results:
        return "low"

    scores = [r["score"] for r in all_results]
    avg_score = sum(scores) / len(scores)

    if avg_score > 0.5:
        return "high"
    elif avg_score >= 0.3:
        return "medium"
    else:
        return "low"


def policy_search_tool(query, filters=None):
    """Execute a policy search and return structured results."""
    if filters is None:
        filters = {}

    sources = filters.get("sources", ["policies", "updates"])
    doc_type = filters.get("doc_type")
    regulatory_body = filters.get("regulatory_body")

    try:
        embedding = get_embedding(query)
    except Exception as e:
        return {
            "answer": f"Error generating embedding: {e}",
            "sources": [],
            "confidence": "low"
        }

    all_results = []

    # Search policies
    if "policies" in sources:
        try:
            policy_results = search_policies(
                query, embedding, top_k=5,
                doc_type=doc_type, regulatory_body=regulatory_body)
            all_results.extend(policy_results)
        except Exception as e:
            print(f"Warning: Policy search failed: {e}")

    # Search updates
    if "updates" in sources:
        try:
            update_results = search_updates(
                query, embedding, top_k=5,
                regulatory_body=regulatory_body)
            all_results.extend(update_results)
        except Exception as e:
            print(f"Warning: Update search failed: {e}")

    # Determine confidence
    confidence = determine_confidence(all_results)

    # Generate answer
    if confidence == "low":
        answer = ("I'm not confident I have relevant information to answer "
                  "this question. Please try rephrasing or contact the "
                  "compliance team directly.")
    else:
        context_parts = []
        for r in all_results:
            source_label = ("Policy" if r["source_type"] == "policy"
                            else "Regulatory Update")
            context_parts.append(
                f"[{source_label}: {r.get('doc_id', 'N/A')} - "
                f"{r.get('title', 'Untitled')}]\n{r['content']}")

        context = "\n\n".join(context_parts)

        messages = [
            {"role": "system", "content": (
                "You are a banking policy assistant. Answer the question "
                "using only the provided context. Cite document IDs when "
                "referencing specific policies or updates."
            )},
            {"role": "user", "content": (
                f"Context:\n{context}\n\nQuestion: {query}"
            )}
        ]

        try:
            answer = chat_with_llm(messages)
        except Exception as e:
            answer = f"Error generating answer: {e}"

    # Build sources list for the response
    source_list = [
        {
            "doc_id": r.get("doc_id", "N/A"),
            "title": r.get("title", "Untitled"),
            "score": round(r["score"], 4),
            "source_type": r["source_type"]
        }
        for r in all_results
    ]

    return {
        "answer": answer,
        "sources": source_list,
        "confidence": confidence
    }


def execute_tool(tool_name, arguments):
    """Dispatcher that routes tool calls to the appropriate function."""
    available_tools = {
        "policy_search": policy_search_tool
    }

    if tool_name not in available_tools:
        return {
            "error": f"Unknown tool: {tool_name}",
            "available_tools": list(available_tools.keys())
        }

    tool_fn = available_tools[tool_name]

    try:
        result = tool_fn(**arguments)
        return result
    except TypeError as e:
        return {"error": f"Invalid arguments for tool '{tool_name}': {e}"}
    except Exception as e:
        return {"error": f"Tool execution failed: {e}"}


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

    # Test with unknown tool
    result_unknown = execute_tool("unknown_tool", {"query": "test"})
    print(f"\nUnknown tool result: {json.dumps(result_unknown, indent=2)}")
