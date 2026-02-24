"""
Lab 11 - Capstone: Multi-Source RAG (Solution)

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
    """Parse YAML frontmatter from a markdown document."""
    if not text.startswith("---"):
        return {}, text

    # Find the closing ---
    end_index = text.find("---", 3)
    if end_index == -1:
        return {}, text

    frontmatter_text = text[3:end_index].strip()
    body = text[end_index + 3:].strip()

    metadata = {}
    current_key = None
    current_list = None

    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Check if this is a list item
        if line.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(line[2:].strip().strip('"').strip("'"))
            metadata[current_key] = current_list
            continue

        # Parse key: value pairs
        if ":" in line:
            # Save any pending list
            current_list = None

            colon_idx = line.index(":")
            key = line[:colon_idx].strip()
            value = line[colon_idx + 1:].strip()

            current_key = key

            if value:
                # Remove quotes if present
                value = value.strip('"').strip("'")
                metadata[key] = value
            # If no value, it might be followed by a list

    return metadata, body


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
        if start >= len(words):
            break
    return chunks if chunks else [text]


def ingest_regulatory_updates(directory_path):
    """Load and ingest regulatory update documents into the database."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Create the regulatory_updates table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS regulatory_updates (
            id SERIAL PRIMARY KEY,
            doc_id TEXT NOT NULL,
            title TEXT,
            effective_date DATE,
            regulatory_body TEXT,
            update_type TEXT,
            content TEXT NOT NULL,
            embedding vector(1024),
            metadata JSONB
        )
    """)
    conn.commit()

    # Clear existing data to allow re-running
    cur.execute("DELETE FROM regulatory_updates")
    conn.commit()

    # Process each markdown file
    files_processed = 0
    chunks_inserted = 0

    for filename in sorted(os.listdir(directory_path)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(directory_path, filename)
        with open(filepath, "r") as f:
            text = f.read()

        metadata, body = parse_frontmatter(text)

        if not metadata.get("doc_id"):
            print(f"  Skipping {filename}: no doc_id in frontmatter")
            continue

        # Chunk the body text
        chunks = chunk_text(body)

        for chunk in chunks:
            try:
                embedding = get_embedding(chunk)
            except Exception as e:
                print(f"  Error embedding chunk from {filename}: {e}")
                continue

            # Store the affects field as part of metadata
            chunk_metadata = {
                "affects": metadata.get("affects", []),
                "source_file": filename
            }

            cur.execute("""
                INSERT INTO regulatory_updates
                (doc_id, title, effective_date, regulatory_body, update_type,
                 content, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s::vector, %s)
            """, (
                metadata.get("doc_id"),
                metadata.get("title"),
                metadata.get("effective_date"),
                metadata.get("regulatory_body"),
                metadata.get("update_type"),
                chunk,
                str(embedding),
                json.dumps(chunk_metadata)
            ))
            chunks_inserted += 1

        files_processed += 1
        print(f"  Ingested: {metadata.get('doc_id')} - {metadata.get('title')}")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\nIngestion complete: {files_processed} files, "
          f"{chunks_inserted} chunks inserted")


def multi_source_search(query, sources=None, top_k=5):
    """Search across multiple data sources (policies and regulatory updates)."""
    if sources is None:
        sources = ["policies", "updates"]

    embedding = get_embedding(query)
    results = {}

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    if "policies" in sources:
        cur.execute("""
            SELECT pc.content,
                   1 - (pc.embedding <=> %s::vector) AS score,
                   pd.doc_id,
                   pd.title
            FROM policy_chunks pc
            JOIN policy_documents pd ON pc.document_id = pd.doc_id
            ORDER BY pc.embedding <=> %s::vector
            LIMIT %s
        """, (str(embedding), str(embedding), top_k))

        results["policies"] = [
            {"content": row[0], "score": row[1], "doc_id": row[2],
             "title": row[3], "source_type": "policy"}
            for row in cur.fetchall()
        ]

    if "updates" in sources:
        # Check if the table exists before querying
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'regulatory_updates'
            )
        """)
        table_exists = cur.fetchone()[0]

        if table_exists:
            cur.execute("""
                SELECT content,
                       1 - (embedding <=> %s::vector) AS score,
                       doc_id,
                       title
                FROM regulatory_updates
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (str(embedding), str(embedding), top_k))

            results["updates"] = [
                {"content": row[0], "score": row[1], "doc_id": row[2],
                 "title": row[3], "source_type": "update"}
                for row in cur.fetchall()
            ]
        else:
            results["updates"] = []

    cur.close()
    conn.close()
    return results


def generate_multi_source_answer(query, policy_results, update_results):
    """Generate an answer using context from multiple sources."""
    # Build context with source attribution
    context_parts = []

    if policy_results:
        context_parts.append("=== EXISTING POLICY DOCUMENTS ===")
        for r in policy_results:
            context_parts.append(
                f"[Source: Policy {r.get('doc_id', 'N/A')} - "
                f"{r.get('title', 'Untitled')}]\n{r['content']}")

    if update_results:
        context_parts.append("\n=== RECENT REGULATORY UPDATES ===")
        for r in update_results:
            context_parts.append(
                f"[Source: Update {r.get('doc_id', 'N/A')} - "
                f"{r.get('title', 'Untitled')}]\n{r['content']}")

    context = "\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": (
            "You are a banking policy assistant with access to both existing "
            "policy documents and recent regulatory updates. When answering:\n"
            "1. Clearly attribute each piece of information to its source "
            "(Policy Document or Regulatory Update)\n"
            "2. If a regulatory update changes or supersedes an existing "
            "policy, highlight this clearly\n"
            "3. Note the document IDs when citing sources\n"
            "4. If there are conflicts between policies and updates, flag them"
        )},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]

    try:
        return chat_with_llm(messages)
    except Exception as e:
        return f"Error generating answer: {e}"


def detect_conflicts(policy_results, update_results):
    """Identify potential conflicts between existing policies and newer updates."""
    if not policy_results or not update_results:
        return []

    policy_summary = "\n".join(
        f"[{r.get('doc_id', 'N/A')}] {r['content'][:200]}"
        for r in policy_results
    )

    update_summary = "\n".join(
        f"[{r.get('doc_id', 'N/A')}] {r['content'][:200]}"
        for r in update_results
    )

    messages = [
        {"role": "system", "content": (
            "You are a compliance analyst. Compare existing policies with "
            "recent regulatory updates and identify potential conflicts or "
            "areas where existing policies may need revision.\n\n"
            "For each conflict found, provide a one-line description in this "
            "format:\n"
            "CONFLICT: [policy doc_id] vs [update doc_id] - description\n\n"
            "If no conflicts are found, respond with exactly: NO CONFLICTS"
        )},
        {"role": "user", "content": (
            f"Existing Policies:\n{policy_summary}\n\n"
            f"Regulatory Updates:\n{update_summary}\n\n"
            "List any conflicts:"
        )}
    ]

    try:
        response = chat_with_llm(messages)
    except Exception as e:
        return [f"Error during conflict detection: {e}"]

    if "NO CONFLICTS" in response.upper():
        return []

    # Parse conflict lines from response
    conflicts = []
    for line in response.split("\n"):
        line = line.strip()
        if line and ("CONFLICT" in line.upper() or line.startswith("-")):
            # Clean up the line
            cleaned = line.lstrip("-").strip()
            if cleaned:
                conflicts.append(cleaned)

    # If we could not parse structured conflicts, return the raw response
    if not conflicts and response.strip():
        conflicts = [response.strip()]

    return conflicts


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
