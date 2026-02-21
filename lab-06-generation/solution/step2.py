"""
Lab 06, Step 2 Solution: Context Formatting and Prompt Construction
"""

SAMPLE_CHUNKS = [
    {
        "content": "All customers must undergo identity verification before account opening. "
                   "Acceptable documents include government-issued photo ID, proof of address "
                   "dated within three months, and a valid tax identification number.",
        "heading": "Customer Identity Verification",
        "doc_title": "KYC Policy Framework v2.1",
        "score": 0.87
    },
    {
        "content": "Enhanced due diligence is required for politically exposed persons (PEPs) "
                   "and customers from high-risk jurisdictions. Additional documentation and "
                   "senior management approval are mandatory.",
        "heading": "Enhanced Due Diligence Requirements",
        "doc_title": "KYC Policy Framework v2.1",
        "score": 0.82
    },
    {
        "content": "Customer risk assessments must be reviewed annually for standard-risk "
                   "customers and semi-annually for high-risk customers. Any changes in "
                   "customer activity patterns must trigger an immediate review.",
        "heading": "Ongoing Monitoring",
        "doc_title": "AML Compliance Procedures 2024",
        "score": 0.74
    }
]

SYSTEM_PROMPT = """You are PolicyChat, a banking regulatory policy assistant.
Answer questions using ONLY the provided context from policy documents.
Always cite the source document title for each claim you make.
If the context does not contain enough information to answer, say so clearly.
Use professional, precise language appropriate for banking compliance."""


def format_context(chunks):
    """
    Format a list of retrieved chunks into a numbered context string.
    """
    parts = []
    for i, chunk in enumerate(chunks, 1):
        part = (
            f"[{i}] (Source: {chunk['doc_title']})\n"
            f"{chunk['heading']}\n"
            f"{chunk['content']}"
        )
        parts.append(part)
    return "\n\n".join(parts)


def build_messages(query, chunks):
    """
    Build the full messages list for the LLM call.
    """
    context_str = format_context(chunks)

    user_content = f"Context:\n{context_str}\n\nQuestion: {query}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
    return messages


if __name__ == "__main__":
    query = "What documents are needed for KYC verification?"

    context_str = format_context(SAMPLE_CHUNKS)
    print("=== Formatted Context ===")
    print(context_str)

    messages = build_messages(query, SAMPLE_CHUNKS)
    print("\n=== Messages Structure ===")
    for msg in messages:
        print(f"\n[{msg['role'].upper()}]")
        print(msg["content"][:300])
        if len(msg["content"]) > 300:
            print("...")
