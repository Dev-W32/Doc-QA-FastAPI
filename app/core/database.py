# app/core/database.py

import os
import psycopg2
from dotenv import load_dotenv
from fastapi import Depends

load_dotenv()  # if you use a .env for credentials

def get_db_connection():
    
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    try:
        yield conn
    finally:
        conn.close()


# app/core/database.py

import os
from typing import Generator
from dotenv import load_dotenv
import psycopg2
from psycopg2.pool import SimpleConnectionPool

# Load environment variables from .env
load_dotenv()

# — Why connection pooling? —
# Opening and closing a new database connection on every single request
# is expensive: it takes time and resources. A connection pool keeps
# a small pool of open connections that your app can reuse, dramatically
# improving performance under load.

# Initialize a global pool (adjust minconn/maxconn to your needs)
try:
    pool = SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
except Exception as e:
    # In a real app, replace print() with logging
    print(f"❌ Failed to initialize DB pool: {e}")
    pool = None

def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    if pool is None:
        # If the pool failed to initialize, we can't serve requests.
        # Raising here will result in a 500 error from FastAPI.
        raise RuntimeError("Database connection pool is not available")

    # Grab a connection from the pool
    conn = pool.getconn()
    try:
        yield conn
    finally:
        # Return the connection back to the pool so others can reuse it
        pool.putconn(conn)

