"""
Lab 11 - Capstone: Multi-Source RAG

Build a RAG system that ingests regulatory updates alongside existing policies,
searches across both sources, generates answers with source attribution,
and detects potential conflicts between policies and updates.
"""

import psycopg2
import requests
import json
import os

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050"
}

OLLAMA_URL = "http://localhost:11434/api/embed"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"


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


def parse_frontmatter(text):
    """Parse YAML frontmatter from a markdown document.

    Expects the document to start with '---' and have a closing '---'.
    Extracts key-value pairs from the frontmatter and returns them as a dict.
    Also returns the body content (everything after the closing '---').

    Args:
        text: The full text of the markdown document.

    Returns:
        A tuple of (metadata_dict, body_text).
    """
    # TODO: implement
    ...


def ingest_regulatory_updates(directory_path):
    """Load and ingest regulatory update documents into the database.

    Creates a regulatory_updates table if needed, chunks and embeds the documents,
    and stores them with their metadata.

    The table should have columns:
    - id: serial primary key
    - doc_id: text (e.g. UPDATE-001)
    - title: text
    - effective_date: date
    - regulatory_body: text
    - update_type: text
    - content: text (the chunk content)
    - embedding: vector(1024)
    - metadata: jsonb
    """
    # TODO: implement
    ...


def multi_source_search(query, sources=None, top_k=5):
    """Search across multiple data sources (policies and regulatory updates).

    Args:
        query: The search query string
        sources: List of sources to search. Options: ["policies", "updates"].
                 Defaults to both.
        top_k: Number of results per source

    Returns:
        Dict with "policies" and "updates" keys, each containing ranked results.
        Each result should have: content, score, doc_id, title (where available).
    """
    # TODO: implement
    ...


def generate_multi_source_answer(query, policy_results, update_results):
    """Generate an answer using context from multiple sources.

    The answer should clearly attribute information to its source type
    (Policy Document vs Regulatory Update) and flag any potential conflicts.

    Args:
        query: The user query.
        policy_results: List of results from the policies source.
        update_results: List of results from the updates source.

    Returns:
        The generated answer string with source attribution.
    """
    # TODO: implement
    ...


def detect_conflicts(policy_results, update_results):
    """Identify potential conflicts between existing policies and newer updates.

    Uses the LLM to compare policy content with regulatory updates and
    flag areas where policies may need revision.

    Args:
        policy_results: List of policy search results.
        update_results: List of regulatory update search results.

    Returns:
        A list of conflict description strings, or an empty list if none found.
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    # Step 1: Ingest regulatory updates
    updates_dir = "../data/regulatory_updates"
    print("Ingesting regulatory updates...")
    ingest_regulatory_updates(updates_dir)

    # Step 2: Multi-source search
    query = "What are the current KYC requirements and any recent changes?"
    print(f"\nSearching: {query}")
    results = multi_source_search(query)

    print(f"\nPolicy results: {len(results.get('policies', []))}")
    for r in results.get("policies", []):
        print(f"  - [{r.get('doc_id', 'N/A')}] score={r['score']:.3f}: "
              f"{r['content'][:80]}...")

    print(f"\nUpdate results: {len(results.get('updates', []))}")
    for r in results.get("updates", []):
        print(f"  - [{r.get('doc_id', 'N/A')}] score={r['score']:.3f}: "
              f"{r['content'][:80]}...")

    # Step 3: Generate multi-source answer
    answer = generate_multi_source_answer(
        query, results.get("policies", []), results.get("updates", []))
    print(f"\nAnswer:\n{answer}")

    # Step 4: Detect conflicts
    print("\nChecking for conflicts...")
    conflicts = detect_conflicts(
        results.get("policies", []), results.get("updates", []))
    if conflicts:
        print("Potential conflicts found:")
        for c in conflicts:
            print(f"  - {c}")
    else:
        print("No conflicts detected.")
