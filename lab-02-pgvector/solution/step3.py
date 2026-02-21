"""
Step 3 Solution: Create HNSW and IVFFlat indexes on the embedding column,
then run a basic similarity query.
"""

import psycopg2
import requests

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

OLLAMA_URL = "http://localhost:11434/api/embed"


def get_embedding(text):
    """Generate an embedding using Ollama bge-m3."""
    response = requests.post(OLLAMA_URL, json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]


def create_hnsw_index(cursor):
    """Create an HNSW index on the embedding column of policy_chunks."""
    cursor.execute("DROP INDEX IF EXISTS idx_policy_chunks_hnsw;")
    cursor.execute("""
        CREATE INDEX idx_policy_chunks_hnsw
        ON policy_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)


def create_ivfflat_index(cursor):
    """Create an IVFFlat index on the embedding column of policy_chunks."""
    cursor.execute("DROP INDEX IF EXISTS idx_policy_chunks_ivfflat;")
    cursor.execute("""
        CREATE INDEX idx_policy_chunks_ivfflat
        ON policy_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 4);
    """)


def similarity_search(cursor, query_embedding, top_k=3):
    """Find the top_k most similar chunks to the query embedding."""
    cursor.execute(
        """
        SELECT content, heading, embedding <=> %s::vector AS distance
        FROM policy_chunks
        ORDER BY distance
        LIMIT %s
        """,
        (str(query_embedding), top_k),
    )
    return cursor.fetchall()


if __name__ == "__main__":
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    # Create indexes
    print("Creating HNSW index...")
    create_hnsw_index(cur)
    print("HNSW index created.")

    print("Creating IVFFlat index...")
    create_ivfflat_index(cur)
    print("IVFFlat index created.")

    # Run a similarity search
    query = "What identity documents are needed for new customers?"
    print(f"\nQuery: \"{query}\"")
    query_embedding = get_embedding(query)

    results = similarity_search(cur, query_embedding, top_k=3)
    print(f"\nTop {len(results)} results:")
    for i, (content, heading, distance) in enumerate(results):
        similarity = 1 - distance
        print(f"\n  {i+1}. [{heading}] (similarity: {similarity:.4f})")
        print(f"     {content}")

    cur.close()
    conn.close()
    print("\nDone.")
