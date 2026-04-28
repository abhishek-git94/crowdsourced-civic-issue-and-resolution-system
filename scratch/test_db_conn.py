import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Common passwords to test
passwords = ["admin123d", "admin123", "postgres", "admin", "password"]
db_names = ["postgres", "civic_db"]

url_template = "postgresql://postgres:{}@localhost:5432/{}"

current_url = os.getenv("DATABASE_URL")
if current_url:
    print(f"Testing current URL from .env: {current_url}")
    try:
        engine = create_engine(current_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Successfully connected with current URL!")
            exit(0)
    except Exception as e:
        print(f"Failed with current URL: {e}")

print("\nTesting common combinations...")
for pw in passwords:
    for db in db_names:
        url = url_template.format(pw, db)
        print(f"Testing: {url}")
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print(f"FOUND WORKING COMBINATION: {url}")
                exit(0)
        except Exception as e:
            # print(f"Failed: {e}")
            pass

print("\nNo working combination found.")
