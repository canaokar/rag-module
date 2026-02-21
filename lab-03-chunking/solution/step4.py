"""
Step 4 Solution: Compare all three chunking strategies on the same document.
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
    """Split text into fixed-size word-count windows."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), window_size):
        chunk = " ".join(words[i : i + window_size])
        chunks.append(chunk)
    return chunks


def heading_chunk(text):
    """Split text by ## headings, returning content strings."""
    lines = text.split("\n")
    chunks = []
    current_heading = None
    current_lines = []

    for line in lines:
        if line.startswith("## "):
            if current_heading is not None:
                content = "\n".join(current_lines).strip()
                if content:
                    chunks.append(content)
            current_heading = line.strip("# ").strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        content = "\n".join(current_lines).strip()
        if content:
            chunks.append(content)

    return chunks


def split_paragraphs(text):
    """Split text into paragraphs."""
    raw = text.split("\n\n")
    return [p.strip() for p in raw if p.strip()]


def split_sentences(text):
    """Split text into sentences."""
    raw_parts = text.replace("\n", " ").split(". ")
    sentences = []
    for part in raw_parts:
        cleaned = part.strip()
        if cleaned:
            if not cleaned.endswith("."):
                cleaned += "."
            sentences.append(cleaned)
    return sentences


def recursive_chunk(text, target_words=200):
    """Recursively chunk text by paragraphs, sentences, then words."""
    paragraphs = split_paragraphs(text)
    small_pieces = []

    for para in paragraphs:
        if len(para.split()) <= target_words:
            small_pieces.append(para)
        else:
            sentences = split_sentences(para)
            for sentence in sentences:
                if len(sentence.split()) <= target_words:
                    small_pieces.append(sentence)
                else:
                    words = sentence.split()
                    for i in range(0, len(words), target_words):
                        small_pieces.append(" ".join(words[i : i + target_words]))

    chunks = []
    current_chunk = []
    current_word_count = 0

    for piece in small_pieces:
        piece_words = len(piece.split())
        if current_word_count + piece_words > target_words and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [piece]
            current_word_count = piece_words
        else:
            current_chunk.append(piece)
            current_word_count += piece_words

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def analyze_chunks(chunks, strategy_name):
    """Print analysis of a list of chunks."""
    word_counts = [len(c.split()) for c in chunks]
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
    min_words = min(word_counts) if word_counts else 0
    max_words = max(word_counts) if word_counts else 0

    print(f"\nStrategy: {strategy_name}")
    print(f"  Chunk count:     {len(chunks)}")
    print(f"  Average words:   {avg_words:.0f}")
    print(f"  Min words:       {min_words}")
    print(f"  Max words:       {max_words}")
    print(f"  First chunk boundary (first 80 chars):")
    if chunks:
        print(f"    \"{chunks[0][:80]}...\"")
    print()


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
    print("\nKey observations:")
    print("  - Fixed window produces uniform sizes but may split mid-sentence")
    print("  - Heading-based preserves document structure but chunks vary in size")
    print("  - Recursive balances size control with natural text boundaries")
