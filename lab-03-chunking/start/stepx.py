"""
Stretch: Semantic chunking using embedding similarity.
Compute embeddings for each sentence, then group consecutive sentences
with high similarity into chunks.
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
    # TODO: implement
    ...


def split_sentences(text):
    """Split text into sentences.

    Args:
        text: Input text.

    Returns:
        A list of non-empty sentence strings.
    """
    # TODO: implement
    ...


def semantic_chunk(sentences, threshold=SIMILARITY_THRESHOLD):
    """Group consecutive sentences into chunks based on embedding similarity.

    For each pair of consecutive sentences, if their cosine similarity is
    above the threshold, they belong to the same chunk. If similarity drops
    below the threshold, start a new chunk.

    Args:
        sentences: List of sentence strings.
        threshold: Minimum cosine similarity to keep sentences in the same chunk.

    Returns:
        A list of chunk strings (sentences joined back together).
    """
    # TODO: implement
    # 1. Embed all sentences
    # 2. Compare consecutive sentence embeddings
    # 3. When similarity drops below threshold, start a new chunk
    ...


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
