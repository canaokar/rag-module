"""
Step 1: Connect to pgvector, verify the vector extension is installed,
and create the policy_chunks table if it does not exist.
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
    """Verify that the pgvector extension is installed.

    Args:
        cursor: A psycopg2 cursor object.

    Returns:
        True if the vector extension is installed, False otherwise.
    """
    # TODO: implement
    # Hint: Query pg_extension for the 'vector' extension.
    ...


def create_policy_chunks_table(cursor):
    """Create the policy_chunks table if it does not exist.

    The table should have these columns:
        - id: SERIAL PRIMARY KEY
        - document_id: TEXT NOT NULL
        - chunk_index: INTEGER NOT NULL
        - content: TEXT NOT NULL
        - heading: TEXT
        - embedding: vector(1024)
        - metadata: JSONB

    Args:
        cursor: A psycopg2 cursor object.
    """
    # TODO: implement
    ...


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
