import mysql.connector
import logging
import os
from dotenv import load_dotenv

# -------------------- ENVIRONMENT SETUP --------------------
# Adjust path if .env is not in the same place
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'crisislens-api', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# -------------------- PIPELINE LOGIC --------------------
def run_pipeline():
    """
    Placeholder pipeline logic: right now just tests DB connectivity.
    Later this will orchestrate classifier + enricher + other steps.
    """
    logging.basicConfig(level=logging.INFO)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Simple test query (adjust if your schema changes)
        cursor.execute("SELECT COUNT(*) FROM raw_calls")
        count = cursor.fetchone()[0]
        logging.info(f"📊 raw_calls table contains {count} rows")

        cursor.close()
        conn.close()
    except Exception as e:
        logging.exception(f"Pipeline error: {e}")

# -------------------- CLI ENTRYPOINT --------------------
if __name__ == '__main__':
    run_pipeline()
