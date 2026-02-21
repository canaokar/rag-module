"""
Step 4 Solution: Bulk-load documents and chunks into PostgreSQL with embeddings.
"""

import json
import os
import psycopg2
import requests

POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "policies")
OLLAMA_URL = "http://localhost:11434/api/embed"

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}


def parse_frontmatter(text):
    """Parse YAML frontmatter from a Markdown document."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text.strip()
    frontmatter_str = parts[1].strip()
    body = parts[2].strip()
    metadata = {}
    for line in frontmatter_str.split("\n"):
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            value = value.strip().strip('"').strip("'")
            metadata[key.strip()] = value
    return metadata, body


def load_all_policies(directory):
    """Load all .md files from the given directory."""
    documents = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                text = f.read()
            metadata, body = parse_frontmatter(text)
            documents.append({"metadata": metadata, "content": body})
    return documents


def heading_chunk(text):
    """Split Markdown text into chunks by ## headings."""
    lines = text.split("\n")
    chunks = []
    current_heading = None
    current_lines = []
    for line in lines:
        if line.startswith("## "):
            if current_heading is not None:
                content = "\n".join(current_lines).strip()
                if content:
                    chunks.append({"heading": current_heading, "content": content})
            current_heading = line.strip("# ").strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
    if current_heading is not None:
        content = "\n".join(current_lines).strip()
        if content:
            chunks.append({"heading": current_heading, "content": content})
    return chunks


def chunk_all_documents(documents):
    """Chunk all documents and attach metadata."""
    all_chunks = []
    for doc in documents:
        doc_id = doc["metadata"].get("doc_id", "unknown")
        sections = heading_chunk(doc["content"])
        for idx, section in enumerate(sections):
            all_chunks.append({
                "document_id": doc_id,
                "chunk_index": idx,
                "heading": section["heading"],
                "content": section["content"],
                "metadata": doc["metadata"],
            })
    return all_chunks


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def create_tables(cursor):
    """Create the policy_documents and policy_chunks tables."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_documents (
            id SERIAL PRIMARY KEY,
            doc_id TEXT UNIQUE NOT NULL,
            title TEXT,
            doc_type TEXT,
            metadata JSONB
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_chunks (
            id SERIAL PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            heading TEXT,
            embedding vector(1024),
            metadata JSONB
        );
    """)


def insert_document(cursor, metadata):
    """Insert a document record into the policy_documents table."""
    cursor.execute(
        """
        INSERT INTO policy_documents (doc_id, title, doc_type, metadata)
        VALUES (%s, %s, %s, %s::jsonb)
        ON CONFLICT (doc_id) DO NOTHING
        """,
        (
            metadata.get("doc_id", "unknown"),
            metadata.get("title", ""),
            metadata.get("doc_type", ""),
            json.dumps(metadata),
        ),
    )


def insert_chunk(cursor, chunk, embedding):
    """Insert a chunk with its embedding into the policy_chunks table."""
    cursor.execute(
        """
        INSERT INTO policy_chunks (document_id, chunk_index, content, heading, embedding, metadata)
        VALUES (%s, %s, %s, %s, %s::vector, %s::jsonb)
        """,
        (
            chunk["document_id"],
            chunk["chunk_index"],
            chunk["content"],
            chunk["heading"],
            str(embedding),
            json.dumps(chunk["metadata"]),
        ),
    )


def create_indexes(cursor):
    """Create HNSW index on embedding and GIN index on metadata."""
    cursor.execute("DROP INDEX IF EXISTS idx_policy_chunks_hnsw;")
    cursor.execute("""
        CREATE INDEX idx_policy_chunks_hnsw
        ON policy_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)
    cursor.execute("DROP INDEX IF EXISTS idx_policy_chunks_metadata;")
    cursor.execute("""
        CREATE INDEX idx_policy_chunks_metadata
        ON policy_chunks
        USING gin (metadata);
    """)


if __name__ == "__main__":
    print(f"Loading policies from: {POLICIES_DIR}")

    if not os.path.isdir(POLICIES_DIR):
        print(f"Directory not found: {POLICIES_DIR}")
    else:
        documents = load_all_policies(POLICIES_DIR)
        print(f"Loaded {len(documents)} documents.")

        all_chunks = chunk_all_documents(documents)
        print(f"Total chunks: {len(all_chunks)}")

        print("\nConnecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()

        print("Creating tables...")
        create_tables(cur)

        print("Inserting documents...")
        seen_docs = set()
        for doc in documents:
            doc_id = doc["metadata"].get("doc_id", "unknown")
            if doc_id not in seen_docs:
                insert_document(cur, doc["metadata"])
                seen_docs.add(doc_id)
                print(f"  Inserted document: {doc_id}")

        print(f"\nEmbedding and inserting {len(all_chunks)} chunks...")
        for i, chunk in enumerate(all_chunks):
            print(f"  Embedding chunk {i+1}/{len(all_chunks)}...")
            embedding = get_embedding(chunk["content"])
            insert_chunk(cur, chunk, embedding)

        print("\nCreating indexes...")
        create_indexes(cur)
        print("Indexes created.")

        cur.close()
        conn.close()
        print("\nIngestion complete.")
