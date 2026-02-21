"""
Lab 08, Generation Module: Format context and call LLM for RAG answers.
"""

from utils import chat_with_llm, SYSTEM_PROMPT


def generate_answer(query, search_results):
    """
    Generate an answer using LLM with retrieved context.

    Args:
        query: The user's question.
        search_results: List of dicts from search_policies(), each with
                        keys: content, heading, doc_title, score.

    Returns:
        Dict with keys:
            - "answer": The LLM's response string.
            - "sources": List of unique source document titles.
    """
    # TODO: implement
    # 1. If search_results is empty, return a dict with a "no results" answer
    #    and an empty sources list.
    # 2. Format the search results as numbered context with source attribution:
    #    [1] (Source: doc_title)
    #    heading
    #    content
    # 3. Build the messages list:
    #    - system message with SYSTEM_PROMPT
    #    - user message with "Context:\n<context>\n\nQuestion: <query>"
    # 4. Call chat_with_llm() with the messages.
    # 5. Extract unique source titles from search_results.
    # 6. Return {"answer": ..., "sources": [...]}.
    pass


if __name__ == "__main__":
    # Test with sample data
    sample_results = [
        {
            "content": "All customers must undergo identity verification before account opening.",
            "heading": "Customer Identity Verification",
            "doc_title": "KYC Policy Framework v2.1",
            "score": 0.87,
            "metadata": {}
        }
    ]
    result = generate_answer("What are KYC requirements?", sample_results)
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
