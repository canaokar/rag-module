"""
Step 3: Compare similarity scores for semantically related vs unrelated term pairs.
Identify which pairs are similar and which are not based on their cosine similarity.
"""

import requests
import math

OLLAMA_URL = "http://localhost:11434/api/embed"

# Pairs of terms to compare: (term_a, term_b, expected_relationship)
TEST_PAIRS = [
    ("AML compliance", "anti-money laundering procedures", "related"),
    ("KYC requirements", "know your customer checks", "related"),
    ("mortgage interest rate", "anti-money laundering", "unrelated"),
    ("suspicious transaction reporting", "SAR filing obligations", "related"),
    ("credit risk assessment", "customer identity verification", "unrelated"),
]

SIMILARITY_THRESHOLD = 0.75  # above this we consider terms "similar"


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two vectors.

    Args:
        vec_a: First embedding vector.
        vec_b: Second embedding vector.

    Returns:
        Cosine similarity as a float.
    """
    # TODO: implement
    ...


def classify_pair(similarity, threshold=SIMILARITY_THRESHOLD):
    """Classify a pair as 'similar' or 'dissimilar' based on the threshold.

    Args:
        similarity: The cosine similarity score.
        threshold: The cutoff for considering terms similar.

    Returns:
        A string: 'similar' or 'dissimilar'.
    """
    # TODO: implement
    ...


if __name__ == "__main__":
    print("Comparing term pairs for semantic similarity")
    print("=" * 70)
    print(f"Similarity threshold: {SIMILARITY_THRESHOLD}\n")

    correct = 0
    total = len(TEST_PAIRS)

    for term_a, term_b, expected in TEST_PAIRS:
        emb_a = get_embedding(term_a)
        emb_b = get_embedding(term_b)
        sim = cosine_similarity(emb_a, emb_b)
        prediction = classify_pair(sim)

        match = "CORRECT" if (
            (prediction == "similar" and expected == "related")
            or (prediction == "dissimilar" and expected == "unrelated")
        ) else "MISMATCH"

        if match == "CORRECT":
            correct += 1

        print(f"  '{term_a}' vs '{term_b}'")
        print(f"    Similarity: {sim:.4f} | Predicted: {prediction} | Expected: {expected} | {match}")
        print()

    print(f"Accuracy: {correct}/{total} pairs classified correctly")
