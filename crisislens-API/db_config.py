import os
from dotenv import load_dotenv
import mysql.connector
from contextlib import contextmanager

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'crisislens')
}

@contextmanager
def get_connection():
    """
    Context manager for database connections using mysql.connector.
    Automatically handles connection cleanup.
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()