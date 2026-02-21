# Lab 01: Embedding Explorer

Get hands-on with text embeddings by generating vectors from banking policy sentences and measuring how similar they are to each other.

## Objectives

By the end of this lab, you will:
- Generate text embeddings using the Ollama bge-m3 model
- Understand embedding dimensions and vector representation
- Compute cosine similarity between embedding vectors
- Observe how semantic meaning is captured in vector space
- Explore the effect of chunk length on embedding quality

---

## Prerequisites

- Docker containers running (shared/compose.yml)
- Ollama running with the bge-m3 model pulled
- Python packages: `requests`

---

## Step 1: Generate Your First Embedding

In this step you will call the Ollama embedding API to convert a single policy sentence into a numeric vector.

Open `start/step1.py` and implement the `get_embedding` function.

### What you are building

A function that sends text to the Ollama bge-m3 model and receives back a 1024-dimensional embedding vector. This vector is a numeric representation of the sentence's meaning.

### Key concepts

- An embedding is a list of floating-point numbers (a vector) that represents the meaning of text
- The bge-m3 model produces 1024-dimensional vectors
- The Ollama `/api/embed` endpoint accepts a model name and input text

### Checkpoint

Run `python start/step1.py` and verify:
- The output shows "Embedding dimensions: 1024"
- Five floating-point values are printed

---

## Step 2: Pairwise Cosine Similarity

Generate embeddings for four policy sentences and compute the cosine similarity between every pair.

Open `start/step2.py` and implement the `cosine_similarity` function.

### What you are building

A cosine similarity function that measures the angle between two vectors. Values close to 1.0 mean the texts are semantically similar, while values closer to 0 mean they are unrelated.

### Key concepts

- Cosine similarity = dot(a, b) / (norm(a) * norm(b))
- Sentences about the same topic (e.g., KYC and identity verification) should score higher
- Sentences about different topics (e.g., KYC vs mortgages) should score lower

### Checkpoint

Run `python start/step2.py` and verify:
- All four sentences are embedded successfully
- Six pairwise similarity scores are printed
- KYC/identity sentences have higher similarity than KYC/mortgage pairs

---

## Step 3: Related vs Unrelated Term Pairs

Test the embedding model's ability to recognise synonyms and abbreviations common in banking regulation.

Open `start/step3.py` and implement the `cosine_similarity` and `classify_pair` functions.

### What you are building

A classifier that uses a similarity threshold to determine whether two terms are semantically related. This tests whether the embedding model understands domain-specific abbreviations like AML, KYC, and SAR.

### Key concepts

- Embedding models can capture synonyms and abbreviations
- A threshold separates "similar" from "dissimilar" pairs
- Domain-specific terms (AML, KYC) are well represented in modern embedding models

### Checkpoint

Run `python start/step3.py` and verify:
- Related pairs (e.g., "AML compliance" vs "anti-money laundering procedures") score above the threshold
- Unrelated pairs score below the threshold
- Most or all pairs are classified correctly

---

## Step 4: Chunk Length Impact

Explore how the length of text affects its embedding by comparing a full paragraph embedding to individual sentence embeddings.

Open `start/step4.py` and implement the `cosine_similarity` and `split_into_sentences` functions.

### What you are building

An experiment that embeds one AML paragraph as a whole and also embeds each sentence individually, then compares the results. This demonstrates the trade-off between chunk size and embedding specificity.

### Key concepts

- Longer text chunks capture broader context but may dilute specific details
- Shorter chunks are more specific but lose surrounding context
- The choice of chunk size is a key design decision in RAG systems
- Each sentence's similarity to the full paragraph varies based on how central it is to the overall topic

### Checkpoint

Run `python start/step4.py` and verify:
- The paragraph is split into 5 sentences
- Each sentence's similarity to the full paragraph is printed
- Sentence-to-sentence similarities are shown
- Sentences closely related to the main AML topic have higher similarity to the paragraph

---

## Recap

| Step | What You Did |
|------|-------------|
| Step 1 | Generated a 1024-dimensional embedding from a single sentence using Ollama bge-m3 |
| Step 2 | Computed cosine similarity between four policy sentence embeddings |
| Step 3 | Classified term pairs as related or unrelated using a similarity threshold |
| Step 4 | Compared full-paragraph vs individual-sentence embeddings to understand chunk length effects |

---

## Stretch Goals

- Try different embedding models (e.g., nomic-embed-text) and compare the similarity scores
- Experiment with different similarity thresholds in Step 3 to find the optimal cutoff
- Add more domain-specific term pairs and test edge cases (e.g., partial abbreviations)
- Plot the similarity matrix as a heatmap using matplotlib
