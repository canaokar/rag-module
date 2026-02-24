import psycopg2
conn = psycopg2.connect(dbname="pgvector", user="postgres",
password="postgres", host="localhost", port="5050")
conn.autocommit = True
cur = conn.cursor()
cur.execute("UPDATE policy_chunks SET search_vector = to_tsvector('english', content) WHERE search_vector IS NULL")
print("Done - search_vector populated")
conn.close()