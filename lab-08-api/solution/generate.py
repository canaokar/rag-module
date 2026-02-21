"""
Lab 08 Solution: Generation Module
"""

from utils import chat_with_llm, SYSTEM_PROMPT


def generate_answer(query, search_results):
    """
    Generate an answer using LLM with retrieved context.
    """
    if not search_results:
        return {
            "answer": "No relevant policy documents were found for your query.",
            "sources": []
        }

    # Format context with source attribution
    parts = []
    for i, chunk in enumerate(search_results, 1):
        part = (
            f"[{i}] (Source: {chunk['doc_title']})\n"
            f"{chunk['heading']}\n"
            f"{chunk['content']}"
        )
        parts.append(part)
    context_str = "\n\n".join(parts)

    # Build messages
    user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    # Call LLM
    answer = chat_with_llm(messages)

    # Extract unique sources
    sources = list(set(r["doc_title"] for r in search_results))

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":
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
