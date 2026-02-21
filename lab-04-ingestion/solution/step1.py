"""
Step 1 Solution: Load all policy documents and extract YAML frontmatter.
"""

import os

POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "policies")


def parse_frontmatter(text):
    """Parse YAML frontmatter from a Markdown document.

    Splits on "---" markers and parses key: value lines manually.
    """
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text.strip()

    frontmatter_str = parts[1].strip()
    body = parts[2].strip()

    metadata = {}
    for line in frontmatter_str.split("\n"):
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            value = value.strip().strip('"').strip("'")
            metadata[key.strip()] = value
    return metadata, body


def load_all_policies(directory):
    """Load all .md files from the given directory."""
    documents = []
    if not os.path.isdir(directory):
        print(f"Warning: directory not found: {directory}")
        return documents

    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                text = f.read()
            metadata, body = parse_frontmatter(text)
            documents.append({"metadata": metadata, "content": body})

    return documents


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
