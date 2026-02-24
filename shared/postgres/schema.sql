-- PolicyChat schema for pgvector database
-- Sets up tables and indexes for banking policy document storage and retrieval

CREATE EXTENSION IF NOT EXISTS vector;

-- Stores full policy documents with metadata
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

-- Stores chunked segments of policy documents with embeddings
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

-- HNSW index for fast approximate nearest-neighbour search on embeddings
CREATE INDEX idx_policy_chunks_embedding
    ON policy_chunks
    USING hnsw (embedding vector_cosine_ops);

-- GIN index on chunk metadata for JSONB queries
CREATE INDEX idx_policy_chunks_metadata
    ON policy_chunks
    USING gin (metadata);

-- GIN index on document metadata for JSONB queries
CREATE INDEX idx_policy_documents_metadata
    ON policy_documents
    USING gin (metadata);

-- GIN index on search_vector for full-text search
CREATE INDEX idx_policy_chunks_search_vector
    ON policy_chunks
    USING gin (search_vector);

-- B-tree index for filtering documents by type
CREATE INDEX idx_policy_documents_doc_type
    ON policy_documents (doc_type);

-- B-tree index for filtering documents by regulatory body
CREATE INDEX idx_policy_documents_regulatory_body
    ON policy_documents (regulatory_body);
