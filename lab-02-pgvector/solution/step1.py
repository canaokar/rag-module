"""
Step 1 Solution: Connect to pgvector, verify the vector extension,
and create the policy_chunks table.
"""

import psycopg2

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}


def check_vector_extension(cursor):
    """Verify that the pgvector extension is installed."""
    cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
    result = cursor.fetchone()
    return result is not None


def create_policy_chunks_table(cursor):
    """Create the policy_chunks table if it does not exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_chunks (
            id SERIAL PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            heading TEXT,
            embedding vector(1024),
            metadata JSONB
        );
    """)


if __name__ == "__main__":
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    # Check vector extension
    if check_vector_extension(cur):
        print("pgvector extension is installed.")
    else:
        print("pgvector extension is NOT installed. Creating it...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("Extension created.")

    # Create table
    create_policy_chunks_table(cur)
    print("policy_chunks table is ready.")

    # Verify table exists
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'policy_chunks'
        ORDER BY ordinal_position;
    """)
    columns = cur.fetchall()
    print("\nTable columns:")
    for col_name, col_type in columns:
        print(f"  {col_name}: {col_type}")

    cur.close()
    conn.close()
    print("\nDone.")
