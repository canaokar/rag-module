"""
Step 1 Solution: Generate an embedding for a single policy sentence using Ollama bge-m3.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/embed"


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3 model.

    Args:
        text: The input string to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    response = requests.post(
        OLLAMA_URL,
        json={"model": "bge-m3", "input": text},
    )
    response.raise_for_status()
    return response.json()["embeddings"][0]


if __name__ == "__main__":
    sentence = "All customers must complete identity verification before account opening."

    print(f"Generating embedding for: \"{sentence}\"")
    embedding = get_embedding(sentence)

    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"Data type of first value: {type(embedding[0])}")
