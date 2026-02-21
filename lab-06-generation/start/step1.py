"""
Lab 06, Step 1: Design the PolicyChat System Prompt

Craft a system prompt that instructs the LLM to behave as a banking
regulatory policy assistant with strict grounding rules.
"""


# TODO: implement
# Define a SYSTEM_PROMPT constant (multi-line string) that instructs the LLM to:
# 1. Only answer from provided context -- never use external knowledge.
# 2. Cite sources by document title for each claim.
# 3. Say "I don't have enough information to answer that question" when context
#    does not cover the query.
# 4. Use professional banking/compliance language.
# 5. Structure answers clearly with bullet points where appropriate.

SYSTEM_PROMPT = """"""


if __name__ == "__main__":
    print("=== PolicyChat System Prompt ===\n")
    print(SYSTEM_PROMPT)
    print(f"\nPrompt length: {len(SYSTEM_PROMPT)} characters")
