# Lab 03: Chunking the Policy Corpus

Explore different strategies for splitting policy documents into chunks suitable for embedding and retrieval. Compare fixed-window, structure-aware, and recursive chunking approaches.

## Objectives

By the end of this lab, you will:
- Implement fixed-window chunking by word count
- Build a structure-aware chunker that respects Markdown headings
- Create a recursive chunker that splits by paragraphs, sentences, then words
- Compare the trade-offs of each chunking strategy
- (Stretch) Implement semantic chunking using embedding similarity

---

## Prerequisites

- Docker containers running (shared/compose.yml)
- Lab 01 completed (familiarity with embeddings)
- Python packages: `requests` (for stretch goal only)

---

## Step 1: Fixed-Window Chunking

Split a policy document into chunks of approximately 200 words each, regardless of document structure.

Open `start/step1.py` and implement the `load_document` and `fixed_window_chunk` functions.

### What you are building

A simple chunker that splits text purely by word count. This is the baseline approach and the easiest to implement. It guarantees uniform chunk sizes but may cut sentences or paragraphs in half.

### Key concepts

- Fixed-window chunking is the simplest strategy
- It produces uniform chunk sizes, which is good for consistent embedding quality
- It ignores document structure, which may split important context across chunks
- YAML frontmatter must be separated from the body before chunking

### Checkpoint

Run `python start/step1.py` and verify:
- The document loads and frontmatter is separated from the body
- Chunks are approximately 200 words each
- The word counts for all chunks are printed

---

## Step 2: Structure-Aware Markdown Chunking

Split the document at ## heading boundaries so each chunk corresponds to a section.

Open `start/step2.py` and implement the `heading_chunk` function.

### What you are building

A chunker that uses Markdown heading markers (##) as natural split points. Each chunk contains one section heading and all its content. This preserves the logical structure of the document.

### Key concepts

- Markdown headings provide natural document boundaries
- Each section typically covers a coherent topic
- Section-based chunks vary widely in size (some sections are short, others long)
- Keeping the heading with its content provides useful context for the embedding

### Checkpoint

Run `python start/step2.py` and verify:
- The document is split into 6 section-based chunks
- Each chunk shows its heading and word count
- The sections match the original document structure

---

## Step 3: Recursive Chunking

Implement a multi-level chunking strategy that tries paragraph-level splits first, then sentences, then words as fallback.

Open `start/step3.py` and implement `split_paragraphs`, `split_sentences`, and `recursive_chunk`.

### What you are building

A chunker that respects natural text boundaries as much as possible. It first tries to keep paragraphs intact. If a paragraph exceeds the target size, it splits into sentences. If a sentence is still too long, it falls back to word-level splitting. After splitting, small consecutive pieces are merged back up to the target size.

### Key concepts

- Recursive chunking prioritises natural text boundaries
- The hierarchy of split points: paragraphs, sentences, words
- A merging step recombines small pieces to avoid tiny chunks
- This approach balances chunk size uniformity with content coherence

### Checkpoint

Run `python start/step3.py` and verify:
- Chunks are close to the 200-word target
- No chunk drastically exceeds the target
- The average chunk size is printed

---

## Step 4: Compare All Strategies

Run all three chunking strategies on the same document and compare the results side by side.

Open `start/step4.py` and implement all three chunking functions plus the `analyze_chunks` function.

### What you are building

A comparison tool that shows the chunk count, average size, minimum and maximum size, and first chunk boundary for each strategy. This helps you make an informed decision about which strategy to use in your RAG pipeline.

### Key concepts

- There is no single "best" chunking strategy for all use cases
- Fixed-window is simple but loses context
- Heading-based preserves structure but produces uneven sizes
- Recursive is a good middle ground for most applications
- Chunk size affects both retrieval quality and LLM context usage

### Checkpoint

Run `python start/step4.py` and verify:
- All three strategies produce output
- Statistics (count, average, min, max) are shown for each
- You can see the trade-offs between uniformity and structure

---

## Recap

| Step | What You Did |
|------|-------------|
| Step 1 | Implemented fixed-window chunking that splits text into 200-word segments |
| Step 2 | Built a structure-aware chunker that splits on Markdown ## headings |
| Step 3 | Created a recursive chunker with paragraph, sentence, and word fallback levels |
| Step 4 | Compared all three strategies with chunk count, size stats, and boundary analysis |

---

## Stretch Goals

- **Semantic chunking (stepx.py):** Use embedding similarity to group consecutive sentences that share a topic. Open `start/stepx.py` and implement the `cosine_similarity`, `split_sentences`, and `semantic_chunk` functions. This approach detects natural topic shifts in the text by comparing embedding vectors of adjacent sentences.
- Add overlap between chunks (e.g., 20-word overlap) and observe how it affects retrieval
- Implement a chunker that respects both headings and a maximum word count (splitting large sections)
- Experiment with different target chunk sizes (100, 200, 500 words) and note the impact on chunk count
