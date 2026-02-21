"""
Step 4 Solution: Experiment with chunk length impact on embedding similarity.
Embed a full paragraph, then split into sentences and embed each individually.
Compare full-paragraph embedding to each sentence embedding.
"""

import math
import requests

OLLAMA_URL = "http://localhost:11434/api/embed"

AML_PARAGRAPH = (
    "Financial institutions must implement robust anti-money laundering controls "
    "to detect and prevent illicit financial activity. All customer accounts are "
    "subject to ongoing transaction monitoring using automated screening systems. "
    "Transactions exceeding the reporting threshold of 10,000 GBP must be flagged "
    "for further review. Suspicious activity reports must be filed with the National "
    "Crime Agency within the prescribed timeframe. Failure to comply with AML "
    "regulations may result in significant regulatory penalties and reputational damage."
)


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


def split_into_sentences(text):
    """Split text into sentences on period boundaries.

    Args:
        text: Input text string.

    Returns:
        A list of sentence strings (stripped of whitespace).
    """
    raw_parts = text.split(". ")
    sentences = []
    for part in raw_parts:
        cleaned = part.strip().rstrip(".")
        if cleaned:
            sentences.append(cleaned + ".")
    return sentences


if __name__ == "__main__":
    print("Full paragraph:")
    print(f"  {AML_PARAGRAPH[:80]}...\n")
    print(f"Paragraph word count: {len(AML_PARAGRAPH.split())}\n")

    # Embed the full paragraph
    full_embedding = get_embedding(AML_PARAGRAPH)
    print(f"Full paragraph embedding dimensions: {len(full_embedding)}\n")

    # Split and embed each sentence
    sentences = split_into_sentences(AML_PARAGRAPH)
    print(f"Number of sentences: {len(sentences)}\n")

    print("Similarity of each sentence to the full paragraph:")
    print("-" * 70)
    sent_embeddings = []
    for i, sentence in enumerate(sentences):
        sent_embedding = get_embedding(sentence)
        sent_embeddings.append(sent_embedding)
        sim = cosine_similarity(full_embedding, sent_embedding)
        word_count = len(sentence.split())
        print(f"  Sentence {i+1} ({word_count} words): {sim:.4f}  \"{sentence[:55]}...\"")

    # Compare sentence-to-sentence similarity
    print("\nSentence-to-sentence similarities:")
    print("-" * 70)
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            sim = cosine_similarity(sent_embeddings[i], sent_embeddings[j])
            print(f"  S{i+1} vs S{j+1}: {sim:.4f}")

    # Summary insight
    sims_to_full = []
    for se in sent_embeddings:
        sims_to_full.append(cosine_similarity(full_embedding, se))
    avg_sim = sum(sims_to_full) / len(sims_to_full)
    print(f"\nAverage sentence-to-paragraph similarity: {avg_sim:.4f}")
    print(f"Max: {max(sims_to_full):.4f} | Min: {min(sims_to_full):.4f}")
    print("\nKey takeaway: Individual sentences capture only part of the paragraph's")
    print("meaning. Longer chunks preserve more context but may dilute specifics.")
