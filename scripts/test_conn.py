# test_conn.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
print("Using:", url)

try:
    conn = psycopg2.connect(url, connect_timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("OK:", cur.fetchone())
    cur.close()
    conn.close()
except Exception as e:
    print("CONN ERROR:", type(e).__name__, e)
