"""
Stretch Solution: Semantic chunking using embedding similarity.
"""

import os
import math
import requests

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_policy.md")
OLLAMA_URL = "http://localhost:11434/api/embed"
SIMILARITY_THRESHOLD = 0.75


def load_document(filepath):
    """Load a Markdown document and separate YAML frontmatter from content."""
    with open(filepath, "r") as f:
        text = f.read()
    parts = text.split("---", 2)
    if len(parts) >= 3:
        return parts[1].strip(), parts[2].strip()
    return "", text.strip()


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


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


def semantic_chunk(sentences, threshold=SIMILARITY_THRESHOLD):
    """Group consecutive sentences into chunks based on embedding similarity."""
    if not sentences:
        return []

    print(f"  Embedding {len(sentences)} sentences...")
    embeddings = []
    for i, sentence in enumerate(sentences):
        emb = get_embedding(sentence)
        embeddings.append(emb)
        if (i + 1) % 10 == 0 or i == len(sentences) - 1:
            print(f"    Embedded {i+1}/{len(sentences)} sentences")

    # Compare consecutive sentences and find chunk boundaries
    chunks = []
    current_chunk_sentences = [sentences[0]]

    for i in range(1, len(sentences)):
        sim = cosine_similarity(embeddings[i - 1], embeddings[i])
        if sim >= threshold:
            # High similarity: keep in the same chunk
            current_chunk_sentences.append(sentences[i])
        else:
            # Low similarity: start a new chunk
            chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [sentences[i]]
            print(f"    Chunk boundary at sentence {i+1} (similarity: {sim:.4f})")

    # Add the final chunk
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks


if __name__ == "__main__":
    print(f"Loading document from: {DATA_PATH}")
    _, body = load_document(DATA_PATH)

    sentences = split_sentences(body)
    print(f"Total sentences: {len(sentences)}")
    print(f"Similarity threshold: {SIMILARITY_THRESHOLD}\n")

    print("Computing semantic chunks (this may take a moment)...")
    chunks = semantic_chunk(sentences, threshold=SIMILARITY_THRESHOLD)

    print(f"\nNumber of semantic chunks: {len(chunks)}\n")
    for i, chunk in enumerate(chunks):
        word_count = len(chunk.split())
        print(f"  Chunk {i+1}: {word_count} words")
        print(f"    Preview: {chunk[:100]}...")
        print()

    total_words = sum(len(c.split()) for c in chunks)
    avg_words = total_words / len(chunks) if chunks else 0
    print(f"Average chunk size: {avg_words:.0f} words")
    print(f"Total words: {total_words}")
    print("\nNote: Semantic chunking produces variable-sized chunks that follow")
    print("topical boundaries rather than fixed word counts or structural markers.")
