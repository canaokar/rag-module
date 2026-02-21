"""
Step 2 Solution: Generate embeddings for multiple sentences and compute cosine
similarity between all pairs.
"""

import math
import requests

OLLAMA_URL = "http://localhost:11434/api/embed"

SENTENCES = [
    "All customers must complete identity verification before account opening.",
    "KYC procedures require valid government-issued photo identification.",
    "The maximum loan-to-value ratio for residential mortgages is 85 percent.",
    "Anti-money laundering checks must be performed on all new accounts.",
]


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def cosine_similarity(vec_a, vec_b):
    """Compute the cosine similarity between two vectors.

    Args:
        vec_a: First embedding vector (list of floats).
        vec_b: Second embedding vector (list of floats).

    Returns:
        A float between -1 and 1 representing cosine similarity.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


if __name__ == "__main__":
    print("Generating embeddings for all sentences...")
    embeddings = []
    for i, sentence in enumerate(SENTENCES):
        emb = get_embedding(sentence)
        embeddings.append(emb)
        print(f"  [{i+1}/{len(SENTENCES)}] Embedded: {sentence[:60]}...")

    print(f"\nEmbedding dimensions: {len(embeddings[0])}")

    print("\nPairwise cosine similarities:")
    print("-" * 60)
    for i in range(len(SENTENCES)):
        for j in range(i + 1, len(SENTENCES)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            label_i = SENTENCES[i][:50]
            label_j = SENTENCES[j][:50]
            print(f"  ({i+1},{j+1}) {sim:.4f}  {label_i}...")
            print(f"         vs  {label_j}...")
            print()
