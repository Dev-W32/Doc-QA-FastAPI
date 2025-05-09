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

    # Create the table if it doesn't exist, with all required columns
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        filename TEXT,
        checksum TEXT UNIQUE,
        uploaded_at TIMESTAMPTZ DEFAULT now(),
        status TEXT DEFAULT 'pending',
        gcs_uri TEXT,
        error TEXT
    );
    """)

    # If the table already existed, make sure each column is present
    cur.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending';")
    cur.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS gcs_uri TEXT;")
    cur.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS error TEXT;")

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized / migrated successfully.")

if __name__ == "__main__":
    init_db()
