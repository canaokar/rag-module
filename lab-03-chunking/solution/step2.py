"""
Step 2 Solution: Structure-aware Markdown chunking by ## headings.
"""

import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_policy.md")


def load_document(filepath):
    """Load a Markdown document and separate YAML frontmatter from content."""
    with open(filepath, "r") as f:
        text = f.read()
    parts = text.split("---", 2)
    if len(parts) >= 3:
        return parts[1].strip(), parts[2].strip()
    return "", text.strip()


def heading_chunk(text):
    """Split Markdown text into chunks by ## headings."""
    lines = text.split("\n")
    chunks = []
    current_heading = None
    current_lines = []

    for line in lines:
        if line.startswith("## "):
            # Save previous chunk if it exists
            if current_heading is not None:
                content = "\n".join(current_lines).strip()
                if content:
                    chunks.append({
                        "heading": current_heading,
                        "content": content,
                    })
            current_heading = line.strip("# ").strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
        else:
            # Content before the first ## heading (e.g., the # title)
            # We can either skip it or store it as a preamble chunk
            if line.strip() and not line.startswith("# "):
                if not chunks and current_heading is None:
                    current_heading = "Preamble"
                    current_lines.append(line)

    # Save the last chunk
    if current_heading is not None:
        content = "\n".join(current_lines).strip()
        if content:
            chunks.append({
                "heading": current_heading,
                "content": content,
            })

    return chunks


if __name__ == "__main__":
    print(f"Loading document from: {DATA_PATH}")
    frontmatter, body = load_document(DATA_PATH)

    chunks = heading_chunk(body)

    print(f"Number of heading-based chunks: {len(chunks)}\n")
    for i, chunk in enumerate(chunks):
        word_count = len(chunk["content"].split())
        print(f"  Chunk {i+1}: \"{chunk['heading']}\" ({word_count} words)")
        print(f"    Preview: {chunk['content'][:100]}...")
        print()
