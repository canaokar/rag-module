"""
Step 1: Generate an embedding for a single policy sentence using Ollama bge-m3.
Print the embedding length and first 5 values.
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
    # TODO: implement
    # Hint: POST to OLLAMA_URL with json={"model": "bge-m3", "input": text}
    # Then extract the embedding from the response JSON.
    ...


if __name__ == "__main__":
    sentence = "All customers must complete identity verification before account opening."
    embedding = get_embedding(sentence)
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
