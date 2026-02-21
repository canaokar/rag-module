"""
Step 3: Recursive chunking.
Try paragraph-level first; if a chunk is too large, split by sentences;
if still too large, split by words. Target chunk size is approximately 200 words.
"""

import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_policy.md")
TARGET_WORDS = 200


def load_document(filepath):
    """Load a Markdown document and separate YAML frontmatter from content."""
    with open(filepath, "r") as f:
        text = f.read()
    parts = text.split("---", 2)
    if len(parts) >= 3:
        return parts[1].strip(), parts[2].strip()
    return "", text.strip()


def split_paragraphs(text):
    """Split text into paragraphs (separated by blank lines).

    Args:
        text: Input text.

    Returns:
        A list of paragraph strings.
    """
    # TODO: implement
    ...


def split_sentences(text):
    """Split text into sentences (on '. ' boundaries).

    Args:
        text: Input text.

    Returns:
        A list of sentence strings.
    """
    # TODO: implement
    ...


def recursive_chunk(text, target_words=TARGET_WORDS):
    """Recursively chunk text to meet the target word count.

    Strategy:
        1. Split into paragraphs
        2. If a paragraph exceeds target_words, split it into sentences
        3. If a sentence exceeds target_words, split it by words
        4. Merge small consecutive chunks until they approach target_words

    Args:
        text: Input text.
        target_words: Target maximum words per chunk.

    Returns:
        A list of chunk strings.
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    print(f"Loading document from: {DATA_PATH}")
    frontmatter, body = load_document(DATA_PATH)

    chunks = recursive_chunk(body, target_words=TARGET_WORDS)

    print(f"Number of recursive chunks: {len(chunks)}\n")
    total_words = 0
    for i, chunk in enumerate(chunks):
        word_count = len(chunk.split())
        total_words += word_count
        print(f"  Chunk {i+1}: {word_count} words")
        print(f"    Preview: {chunk[:100]}...")
        print()

    avg_words = total_words / len(chunks) if chunks else 0
    print(f"Average chunk size: {avg_words:.0f} words")
    print(f"Total words across chunks: {total_words}")
