"""
Reset the pgvector database — drops and recreates all PolicyChat tables and indexes.
Run this from the labs/ directory if you need a clean slate.

Usage:
    python reset_db.py
"""

import psycopg2

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE policy_documents (
    id SERIAL PRIMARY KEY,
    doc_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    effective_date DATE,
    regulatory_body TEXT,
    jurisdiction TEXT,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE policy_chunks (
    id SERIAL PRIMARY KEY,
    document_id TEXT REFERENCES policy_documents(doc_id),
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    heading TEXT,
    embedding vector(1024),
    metadata JSONB,
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policy_chunks_embedding
    ON policy_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_policy_chunks_metadata
    ON policy_chunks USING gin (metadata);

CREATE INDEX idx_policy_documents_metadata
    ON policy_documents USING gin (metadata);

CREATE INDEX idx_policy_chunks_search_vector
    ON policy_chunks USING gin (search_vector);

CREATE INDEX idx_policy_documents_doc_type
    ON policy_documents (doc_type);

CREATE INDEX idx_policy_documents_regulatory_body
    ON policy_documents (regulatory_body);
"""

conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True
cur = conn.cursor()

print("Dropping existing tables...")
cur.execute("DROP TABLE IF EXISTS policy_chunks CASCADE;")
cur.execute("DROP TABLE IF EXISTS policy_documents CASCADE;")

print("Recreating schema (tables + indexes)...")
cur.execute(SCHEMA_SQL)

print("Done! Database is clean with empty tables ready to go.")
conn.close()
