"""
Step 2: Chunk all documents using structure-aware Markdown chunking.
Preserve metadata from each document on its chunks.
"""

import os

POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "policies")


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
    """Split Markdown text into chunks by ## headings.

    Args:
        text: The Markdown body text.

    Returns:
        A list of dicts with 'heading' and 'content' keys.
    """
    # TODO: implement
    # Hint: Iterate through lines, detect "## " prefixes,
    # accumulate content under each heading.
    ...


def chunk_all_documents(documents):
    """Chunk all documents and attach metadata to each chunk.

    Args:
        documents: A list of dicts with 'metadata' and 'content' keys.

    Returns:
        A list of dicts, each with keys:
            'document_id', 'chunk_index', 'heading', 'content', 'metadata'
    """
    # TODO: implement
    # For each document:
    #   1. Extract the doc_id from metadata
    #   2. Chunk the content using heading_chunk
    #   3. Create a chunk dict for each piece, preserving the document metadata
    ...


if __name__ == "__main__":
    print(f"Loading policies from: {POLICIES_DIR}")

    if not os.path.isdir(POLICIES_DIR):
        print(f"Directory not found: {POLICIES_DIR}")
    else:
        documents = load_all_policies(POLICIES_DIR)
        print(f"Loaded {len(documents)} documents.")

        all_chunks = chunk_all_documents(documents)
        print(f"Total chunks: {len(all_chunks)}\n")

        for chunk in all_chunks[:5]:
            print(f"  [{chunk['document_id']}] Chunk {chunk['chunk_index']}: {chunk['heading']}")
            print(f"    Words: {len(chunk['content'].split())}")
            print()

        if len(all_chunks) > 5:
            print(f"  ... and {len(all_chunks) - 5} more chunks.")
