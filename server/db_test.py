import psycopg2

# Connection parameters
host = "localhost"
database = "smart-doctor-patient"
user = "postgres"   # your PostgreSQL username
password = "a"  # your PostgreSQL password
port = "5432"

try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("Connected to PostgreSQL:", db_version)
except Exception as e:
    print("Error connecting to PostgreSQL:", e)
finally:
    if conn:
        cursor.close()
        conn.close()
