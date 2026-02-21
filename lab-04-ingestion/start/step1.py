"""
Step 1: Load all policy documents from the policies directory,
extract YAML frontmatter (manual parsing), and return a list of dicts
with metadata and content.
"""

import os

POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "policies")


def parse_frontmatter(text):
    """Parse YAML frontmatter from a Markdown document.

    Splits on "---" markers and parses key: value lines manually.

    Args:
        text: The full text of a Markdown file.

    Returns:
        A tuple of (metadata_dict, body_string).
        metadata_dict has string keys and string values.
    """
    # TODO: implement
    # Hint:
    # 1. Split text on "---" (expect at least 3 parts: before, frontmatter, body)
    # 2. Parse each line of frontmatter as "key: value"
    # 3. Strip quotes from values if present
    ...


def load_all_policies(directory):
    """Load all .md files from the given directory.

    Args:
        directory: Path to the directory containing policy Markdown files.

    Returns:
        A list of dicts, each with keys: 'metadata' (dict) and 'content' (str).
    """
    # TODO: implement
    # Hint:
    # 1. List all .md files in the directory
    # 2. For each file, read it and call parse_frontmatter
    # 3. Append {"metadata": metadata, "content": body} to the result list
    ...


if __name__ == "__main__":
    print(f"Loading policies from: {POLICIES_DIR}")

    if not os.path.isdir(POLICIES_DIR):
        print(f"Directory not found: {POLICIES_DIR}")
        print("Make sure the data/policies directory exists with .md files.")
    else:
        documents = load_all_policies(POLICIES_DIR)
        print(f"Loaded {len(documents)} documents.\n")

        for doc in documents:
            meta = doc["metadata"]
            content_preview = doc["content"][:100]
            print(f"  Document: {meta.get('doc_id', 'unknown')}")
            print(f"    Title: {meta.get('title', 'untitled')}")
            print(f"    Type: {meta.get('doc_type', 'unknown')}")
            print(f"    Content preview: {content_preview}...")
            print()
