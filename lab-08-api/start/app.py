"""
Lab 08, Flask App: PolicyChat REST API

Endpoints:
    POST /search   -- Search policy chunks by query (with optional filters)
    POST /ask      -- Ask a question and get a RAG-generated answer
    GET  /documents -- List all policy documents
"""

from flask import Flask, request, jsonify
from search import search_policies
from generate import generate_answer
from utils import get_db_connection

app = Flask(__name__)


@app.route("/search", methods=["POST"])
def search():
    """
    Search policy chunks.

    Expects JSON body:
        {
            "query": "search text",
            "filters": {"doc_type": "AML", ...},  (optional)
            "top_k": 5  (optional, default 5)
        }

    Returns JSON:
        {
            "query": "...",
            "results": [{"content": ..., "heading": ..., "score": ..., ...}],
            "count": N
        }
    """
    # TODO: implement
    # 1. Parse JSON body. Return 400 if "query" is missing.
    # 2. Extract query, filters (default None), top_k (default 5).
    # 3. Call search_policies().
    # 4. Return JSON with query, results list, and count.
    # 5. Wrap in try/except, return JSON error with 500 on failure.
    pass


@app.route("/ask", methods=["POST"])
def ask():
    """
    Ask a question and get a RAG-generated answer.

    Expects JSON body:
        {
            "query": "your question",
            "filters": {"doc_type": "AML", ...}  (optional)
        }

    Returns JSON:
        {
            "query": "...",
            "answer": "...",
            "sources": ["doc title 1", ...],
            "chunks_used": N
        }
    """
    # TODO: implement
    # 1. Parse JSON body. Return 400 if "query" is missing.
    # 2. Call search_policies() to get relevant chunks.
    # 3. Call generate_answer() with the query and search results.
    # 4. Return JSON with query, answer, sources, and chunks_used count.
    # 5. Wrap in try/except, return JSON error with 500 on failure.
    pass


@app.route("/documents", methods=["GET"])
def list_documents():
    """
    List all policy documents.

    Returns JSON:
        {
            "documents": [{"id": ..., "doc_id": ..., "title": ..., "doc_type": ...}],
            "count": N
        }
    """
    # TODO: implement
    # 1. Connect to DB, query policy_documents for id, doc_id, title, doc_type.
    # 2. Return JSON with documents list and count.
    # 3. Wrap in try/except, return JSON error with 500 on failure.
    pass


if __name__ == "__main__":
    print("Starting PolicyChat API on http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
