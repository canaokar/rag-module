# Lab 09: RAG Evaluation

How do you know if your RAG system is working well? In this lab, you will build an evaluation framework that measures retrieval quality and answer quality using a golden test set and automated scoring.

## Objectives
- Build a golden test set for systematic evaluation
- Implement precision@K and recall@K metrics for retrieval
- Use LLM-as-judge to score answer faithfulness and relevance
- Compare metrics across different retrieval configurations

---

## Prerequisites
- Docker containers running (PostgreSQL with pgvector, Ollama)
- Labs 01-08 completed (policy documents ingested with embeddings)

---

## Step 1: Retrieval Testing with a Golden Test Set

A golden test set is a curated collection of queries paired with known-good expected results. This gives you a repeatable benchmark for measuring retrieval quality.

Open `start/step1.py` and implement the TODO sections.

### What you are building
- `load_golden_test_set()`: Load the pre-built test set from `data/golden_test_set.json`
- `retrieve_doc_ids()`: Run the retrieval pipeline (embed query, vector search in policy_chunks, join with policy_documents to get doc_ids)
- `evaluate_retrieval()`: For each query, compare retrieved doc_ids against expected doc_ids and track matches and misses

### Checkpoint
Run the script and verify you see a table showing which expected documents were found and which were missed for each query. You should also see an overall hit rate percentage.

---

## Step 2: Precision and Recall Metrics

Raw hit/miss counts are useful, but standard IR metrics give you a more precise picture of retrieval quality.

Open `start/step2.py` and implement the TODO sections.

### What you are building
- `precision_at_k()`: Calculates what fraction of your top-K results are actually relevant. Formula: (relevant docs in top-K) / K
- `recall_at_k()`: Calculates what fraction of all relevant documents you managed to retrieve. Formula: (relevant docs in top-K) / (total relevant docs)
- `evaluate_metrics()`: Runs both metrics for each query in the test set

### Checkpoint
Run the script and verify you see a formatted table with precision@5 and recall@5 for each query, plus averages at the bottom.

---

## Step 3: LLM-as-Judge

Retrieval metrics tell you if you found the right documents, but they do not tell you if the generated answer is actually good. Here you will use the LLM itself as an automated judge.

Open `start/step3.py` and implement the TODO sections.

### What you are building
- `judge_answer()`: Constructs a judge prompt asking the LLM to evaluate the answer on faithfulness (is it supported by context?) and relevance (does it answer the question?)
- `parse_scores()`: Extracts numeric scores from the judge response using the format "Faithfulness: X/5, Relevance: Y/5"

### Checkpoint
Run the script (this will take longer since it runs the full RAG pipeline plus judge for each query). Verify you see faithfulness and relevance scores for each query, plus averages.

---

## Step 4: Comparing Configurations

Now use your evaluation framework to make data-driven decisions about your retrieval setup.

Open `start/step4.py` and implement the TODO sections.

### What you are building
- `retrieve_vector_only()`: Standard vector search retrieval
- `retrieve_hybrid()`: Hybrid search combining vector similarity with full-text search using Reciprocal Rank Fusion (RRF)
- `run_comparison()`: Runs evaluation across all combinations of K values (3, 5, 10) and search modes (vector only, hybrid)

### Checkpoint
Run the script and verify you see a comparison table showing how precision and recall change across configurations. Look for the tradeoff between precision and recall as K increases.

---

## Recap

| Step | What You Did |
|------|-------------|
| 1    | Built retrieval testing using a golden test set with expected doc_ids |
| 2    | Implemented precision@K and recall@K to quantify retrieval quality |
| 3    | Used LLM-as-judge to automatically score answer faithfulness and relevance |
| 4    | Compared metrics across K values and search modes to find the best configuration |

---

## Stretch Goals
- Add Mean Reciprocal Rank (MRR) as an additional retrieval metric
- Implement nDCG (normalized Discounted Cumulative Gain) for graded relevance
- Create a script that generates evaluation reports as HTML or CSV files
- Add answer coverage checking using the expected_answer_contains field from the test set
- Build a regression test that alerts you when metrics drop below a threshold
