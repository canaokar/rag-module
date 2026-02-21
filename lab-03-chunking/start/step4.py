"""
Step 4: Compare all three chunking strategies on the same document.
Show chunk count, average chunk size, and first chunk boundary for each.
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
    """Split text into fixed-size word-count windows.

    Args:
        text: Input text.
        window_size: Words per chunk.

    Returns:
        A list of chunk strings.
    """
    # TODO: implement (copy from step1 or re-implement)
    ...


def heading_chunk(text):
    """Split text by ## headings.

    Args:
        text: Markdown body text.

    Returns:
        A list of chunk content strings.
    """
    # TODO: implement (copy from step2 or re-implement)
    ...


def recursive_chunk(text, target_words=200):
    """Recursively chunk text by paragraphs, sentences, then words.

    Args:
        text: Input text.
        target_words: Target maximum words per chunk.

    Returns:
        A list of chunk strings.
    """
    # TODO: implement (copy from step3 or re-implement)
    ...


def analyze_chunks(chunks, strategy_name):
    """Print analysis of a list of chunks.

    Args:
        chunks: List of chunk strings.
        strategy_name: Name of the chunking strategy.
    """
    # TODO: implement
    # Print: chunk count, average words, min words, max words, first chunk boundary
    ...


if __name__ == "__main__":
    print(f"Loading document from: {DATA_PATH}")
    _, body = load_document(DATA_PATH)
    print(f"Document word count: {len(body.split())}\n")
    print("=" * 60)

    # Fixed window
    fw_chunks = fixed_window_chunk(body, window_size=200)
    analyze_chunks(fw_chunks, "Fixed Window (200 words)")

    print("=" * 60)

    # Heading-based
    h_chunks = heading_chunk(body)
    analyze_chunks(h_chunks, "Heading-Based (## sections)")

    print("=" * 60)

    # Recursive
    r_chunks = recursive_chunk(body, target_words=200)
    analyze_chunks(r_chunks, "Recursive (target 200 words)")

    print("=" * 60)
    print("\nComparison complete.")
