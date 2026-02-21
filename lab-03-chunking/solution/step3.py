"""
Step 3 Solution: Recursive chunking by paragraphs, sentences, then words.
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
    """Split text into paragraphs (separated by blank lines)."""
    raw_paragraphs = text.split("\n\n")
    return [p.strip() for p in raw_paragraphs if p.strip()]


def split_sentences(text):
    """Split text into sentences (on '. ' boundaries)."""
    raw_parts = text.replace("\n", " ").split(". ")
    sentences = []
    for part in raw_parts:
        cleaned = part.strip()
        if cleaned:
            if not cleaned.endswith("."):
                cleaned += "."
            sentences.append(cleaned)
    return sentences


def recursive_chunk(text, target_words=TARGET_WORDS):
    """Recursively chunk text to meet the target word count."""
    paragraphs = split_paragraphs(text)
    small_pieces = []

    for para in paragraphs:
        word_count = len(para.split())
        if word_count <= target_words:
            small_pieces.append(para)
        else:
            # Paragraph is too large, split into sentences
            sentences = split_sentences(para)
            for sentence in sentences:
                sw_count = len(sentence.split())
                if sw_count <= target_words:
                    small_pieces.append(sentence)
                else:
                    # Sentence is too large, split by words
                    words = sentence.split()
                    for i in range(0, len(words), target_words):
                        piece = " ".join(words[i : i + target_words])
                        small_pieces.append(piece)

    # Merge small consecutive pieces until they approach target_words
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
