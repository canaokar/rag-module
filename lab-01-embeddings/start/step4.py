"""
Step 4: Experiment with chunk length impact on embedding similarity.
Embed a full paragraph about AML policy, then split into sentences and embed each.
Compare the full-paragraph embedding to each sentence embedding.
"""

import requests
import math

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
    """Compute cosine similarity between two vectors.

    Args:
        vec_a: First embedding vector.
        vec_b: Second embedding vector.

    Returns:
        Cosine similarity as a float.
    """
    # TODO: implement
    ...


def split_into_sentences(text):
    """Split text into sentences on period boundaries.

    Args:
        text: Input text string.

    Returns:
        A list of sentence strings (stripped of whitespace).
    """
    # TODO: implement
    # Hint: split on ". " and handle the last sentence.
    ...


if __name__ == "__main__":
    print("Full paragraph:")
    print(f"  {AML_PARAGRAPH[:80]}...\n")

    # Embed the full paragraph
    full_embedding = get_embedding(AML_PARAGRAPH)
    print(f"Full paragraph embedding dimensions: {len(full_embedding)}\n")

    # Split and embed each sentence
    sentences = split_into_sentences(AML_PARAGRAPH)
    print(f"Number of sentences: {len(sentences)}\n")

    print("Similarity of each sentence to the full paragraph:")
    print("-" * 60)
    for i, sentence in enumerate(sentences):
        sent_embedding = get_embedding(sentence)
        sim = cosine_similarity(full_embedding, sent_embedding)
        print(f"  Sentence {i+1}: {sim:.4f}  \"{sentence[:60]}...\"")

    # Compare sentence-to-sentence similarity
    print("\nSentence-to-sentence similarities:")
    print("-" * 60)
    sent_embeddings = [get_embedding(s) for s in sentences]
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            sim = cosine_similarity(sent_embeddings[i], sent_embeddings[j])
            print(f"  S{i+1} vs S{j+1}: {sim:.4f}")
