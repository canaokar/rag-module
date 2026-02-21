"""
Step 1: Fixed-window chunking by word count.
Load sample_policy.md and split it into chunks of approximately 200 words each.
"""

import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_policy.md")


def load_document(filepath):
    """Load a Markdown document and separate YAML frontmatter from content.

    Args:
        filepath: Path to the Markdown file.

    Returns:
        A tuple of (frontmatter_string, body_string).
    """
    # TODO: implement
    # Hint: Read the file, split on "---" markers to separate frontmatter.
    ...


def fixed_window_chunk(text, window_size=200):
    """Split text into chunks of approximately window_size words.

    Args:
        text: The input text string.
        window_size: Target number of words per chunk.

    Returns:
        A list of chunk strings.
    """
    # TODO: implement
    # Hint: Split text into words, then group them into chunks of window_size.
    ...


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
