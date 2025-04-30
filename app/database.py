# app/database.py

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
