"""
Step 2: Structure-aware Markdown chunking.
Split by ## headings, keeping the heading with its content.
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


def heading_chunk(text):
    """Split Markdown text into chunks by ## headings.

    Each chunk should contain the heading line and all content below it,
    up to the next ## heading.

    Args:
        text: The Markdown body text.

    Returns:
        A list of dicts with keys: 'heading' (str) and 'content' (str).
    """
    # TODO: implement
    # Hint: Split text by lines, iterate and detect lines starting with "## ".
    # Accumulate content lines under each heading.
    ...


if __name__ == "__main__":
    print(f"Loading document from: {DATA_PATH}")
    frontmatter, body = load_document(DATA_PATH)

    chunks = heading_chunk(body)

    print(f"Number of heading-based chunks: {len(chunks)}\n")
    for i, chunk in enumerate(chunks):
        word_count = len(chunk["content"].split())
        print(f"  Chunk {i+1}: \"{chunk['heading']}\" ({word_count} words)")
        print(f"    Preview: {chunk['content'][:100]}...")
        print()
