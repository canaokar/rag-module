"""
Lab 08 Solution: Flask App -- PolicyChat REST API
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
    """
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing required field: query"}), 400

        query = data["query"]
        filters = data.get("filters", None)
        top_k = data.get("top_k", 5)

        results = search_policies(query, filters=filters, top_k=top_k)

        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ask", methods=["POST"])
def ask():
    """
    Ask a question and get a RAG-generated answer.
    """
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing required field: query"}), 400

        query = data["query"]
        filters = data.get("filters", None)

        # Retrieve relevant chunks
        results = search_policies(query, filters=filters, top_k=5)

        # Generate answer
        response = generate_answer(query, results)

        return jsonify({
            "query": query,
            "answer": response["answer"],
            "sources": response["sources"],
            "chunks_used": len(results)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/documents", methods=["GET"])
def list_documents():
    """
    List all policy documents.
    """
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, doc_id, title, doc_type
                    FROM policy_documents
                    ORDER BY id
                """)
                rows = cur.fetchall()
                documents = []
                for row in rows:
                    documents.append({
                        "id": row[0],
                        "doc_id": row[1],
                        "title": row[2],
                        "doc_type": row[3]
                    })
        finally:
            conn.close()

        return jsonify({
            "documents": documents,
            "count": len(documents)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting PolicyChat API on http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
