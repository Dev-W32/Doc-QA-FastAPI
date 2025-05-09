# app/core/init_db.py

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_db():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    cur = conn.cursor()

    # Enable uuid extension if not exists
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Create the table if it doesn't exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        filename TEXT,
        checksum TEXT UNIQUE,
        uploaded_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized.")

if __name__ == "__main__":
    init_db()
