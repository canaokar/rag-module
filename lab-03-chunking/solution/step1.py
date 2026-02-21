"""
Step 1 Solution: Fixed-window chunking by word count.
"""

import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_policy.md")


def load_document(filepath):
    """Load a Markdown document and separate YAML frontmatter from content."""
    with open(filepath, "r") as f:
        text = f.read()
    parts = text.split("---", 2)
    if len(parts) >= 3:
        return parts[1].strip(), parts[2].strip()
    return "", text.strip()


def fixed_window_chunk(text, window_size=200):
    """Split text into chunks of approximately window_size words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), window_size):
        chunk = " ".join(words[i : i + window_size])
        chunks.append(chunk)
    return chunks


if __name__ == "__main__":
    print(f"Loading document from: {DATA_PATH}")
    frontmatter, body = load_document(DATA_PATH)

    print(f"Frontmatter length: {len(frontmatter)} chars")
    print(f"Body length: {len(body)} chars")
    print(f"Body word count: {len(body.split())}")

    chunks = fixed_window_chunk(body, window_size=200)

    print(f"\nNumber of chunks: {len(chunks)}")
    print(f"\nChunk sizes (words):")
    for i, chunk in enumerate(chunks):
        word_count = len(chunk.split())
        print(f"  Chunk {i+1}: {word_count} words")

    print(f"\nFirst chunk preview:")
    print(f"  {chunks[0][:200]}...")
