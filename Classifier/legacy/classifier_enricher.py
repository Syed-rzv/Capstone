# classifier_enricher.py
import mysql.connector
import random
import logging
import os
from dotenv import load_dotenv

# -------------------- CLASSIFICATION FUNCTION --------------------
def classify_incident(description: str) -> str:
    description = (description or "").lower()
    fire_keywords = ['fire', 'smoke', 'explosion', 'burning', 'flames', 'blaze']
    traffic_keywords = ['gunshot', 'gunshots', 'robbery', 'shooting', 'theft', 'burglary',
                       'assault', 'car accident', 'accident', 'crash', 'traffic', 'hit and run']
    EMS_keywords = ['heart attack', 'cardiac', 'chest pain', 'fever', 'vomiting', 'injury',
                        'collapsed', 'ambulance', 'stroke', 'unconscious', 'unresponsive', 'dizziness',
                        'fall', 'head injury', 'allergic reaction', 'respiratory', 'breathing', 'asthma',
                        'seizure', 'overdose']

    if any(keyword in description for keyword in fire_keywords):
        return 'Fire'
    if any(keyword in description for keyword in EMS_keywords):
        return 'EMS'
    if any(keyword in description for keyword in traffic_keywords):
        return 'Traffic'
    return 'Unknown'

# -------------------- ENVIRONMENT SETUP --------------------
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'crisislens-api', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# -------------------- HELPERS --------------------
def random_age():
    return random.randint(18, 90)

def age_group(age):
    if age is None:
        return 'Unknown'
    try:
        age = int(age)
    except Exception:
        return 'Unknown'
    if age < 18:
        return 'Under 18'
    elif 18 <= age <= 29:
        return '18-29'
    elif 30 <= age <= 49:
        return '30-49'
    else:
        return '50+'

def random_gender():
    return random.choice(['Male', 'Female', 'Other'])

def random_response_time():
    return random.randint(2, 20)  # minutes

# -------------------- PROCESS SINGLE ROW --------------------
def process_single_call(raw_id):
    """Process a single raw_calls row by id and insert into enriched_data."""
    logging.basicConfig(level=logging.INFO)
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM raw_calls WHERE id = %s", (raw_id,))
    row = cursor.fetchone()
    if not row:
        logging.error(f"raw_calls id={raw_id} not found")
        cursor.close()
        conn.close()
        return False

    try:
        description = (row.get('description') or '').strip()
        # read district if present, fallback to township (defensive)
        district = row.get('district') or row.get('township') or ''
        latitude = row.get('latitude')
        longitude = row.get('longitude')
        timestamp = row.get('timestamp')
        caller_gender = row.get('gender') if row.get('gender') in ['Male', 'Female', 'Other'] else random_gender()
        caller_age = row.get('age') or random_age()

        # Classification
        emergency_type = classify_incident(description)
        emergency_subtype = 'General'  # default; can be refined

        enriched = {
            'timestamp': timestamp,
            'latitude': latitude,
            'longitude': longitude,
            'description': description,
            'emergency_title': description,
            'emergency_type': emergency_type,
            'emergency_subtype': emergency_subtype,
            'zipcode': row.get('zipcode') or '',
            'address': row.get('address') or '',
            'district': district,
            'priority_flag': row.get('priority_flag') or 0,
            'caller_gender': caller_gender,
            'caller_age': caller_age,
            'response_time': random_response_time(),
            'age_group': age_group(caller_age),
            'source': 'real_time'
        }

        cursor.execute("""
            INSERT INTO enriched_data (
                timestamp, latitude, longitude, description, emergency_title,
                emergency_type, emergency_subtype, zipcode, address, district,
                priority_flag, caller_gender, caller_age, response_time, age_group, source
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            enriched['timestamp'], enriched['latitude'], enriched['longitude'], enriched['description'],
            enriched['emergency_title'], enriched['emergency_type'], enriched['emergency_subtype'],
            enriched['zipcode'], enriched['address'], enriched['district'], enriched['priority_flag'],
            enriched['caller_gender'], enriched['caller_age'], enriched['response_time'],
            enriched['age_group'], enriched['source']
        ))

        # mark raw_calls processed
        cursor.execute("UPDATE raw_calls SET processed = 1 WHERE id = %s", (raw_id,))
        conn.commit()
        logging.info(f"Processed raw_calls id={raw_id} -> enriched_data inserted")
        return True

    except Exception as e:
        conn.rollback()
        logging.exception(f"Error processing raw_calls id={raw_id}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# -------------------- BATCH PROCESS (existing behavior) --------------------
def process_new_calls(limit=100):
    """Process up to `limit` unprocessed raw calls (existing batch job)."""
    logging.basicConfig(level=logging.INFO)
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM raw_calls WHERE processed = 0 LIMIT %s", (limit,))
    rows = cursor.fetchall()
    processed = 0
    for row in rows:
        success = process_single_call(row['id'])
        if success:
            processed += 1

    logging.info(f"✅ Processed and enriched {processed} call(s).")
    return processed

# -------------------- CLI ENTRYPOINT --------------------
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Classifier/enricher")
    parser.add_argument('--id', type=int, help='Process single raw_call id')
    parser.add_argument('--batch', type=int, nargs='?', const=100, help='Process batch of unprocessed calls (limit)')
    args = parser.parse_args()

    if args.id:
        process_single_call(args.id)
    else:
        # default: batch run (use --batch to control size)
        lim = args.batch if args.batch else 100
        process_new_calls(limit=lim)
