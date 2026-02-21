"""
Step 3 Solution: Generate embeddings for all chunks with progress reporting.
"""

import os
import requests

POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "policies")
OLLAMA_URL = "http://localhost:11434/api/embed"


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


def embed_all_chunks(chunks):
    """Generate embeddings for all chunks with progress reporting."""
    embeddings = []
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        print(f"  Embedding chunk {i+1}/{total}...")
        embedding = get_embedding(chunk["content"])
        embeddings.append(embedding)
    return embeddings


if __name__ == "__main__":
    print(f"Loading policies from: {POLICIES_DIR}")

    if not os.path.isdir(POLICIES_DIR):
        print(f"Directory not found: {POLICIES_DIR}")
    else:
        documents = load_all_policies(POLICIES_DIR)
        print(f"Loaded {len(documents)} documents.")

        all_chunks = chunk_all_documents(documents)
        print(f"Total chunks to embed: {len(all_chunks)}\n")

        embeddings = embed_all_chunks(all_chunks)

        print(f"\nGenerated {len(embeddings)} embeddings.")
        if embeddings:
            print(f"Embedding dimensions: {len(embeddings[0])}")
