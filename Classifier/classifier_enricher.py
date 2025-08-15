import mysql.connector
import random
import logging
import os
from dotenv import load_dotenv

# --------------------
# CLASSIFICATION FUNCTION
# --------------------
def classify_incident(description: str) -> str:
    description = description.lower()

    fire_keywords = ['fire', 'smoke', 'explosion', 'burning', 'flames', 'blaze']
    police_keywords = ['gunshot', 'gunshots', 'robbery', 'shooting', 'theft', 'burglary', 'assault', 'car accident', 'accident', 'crash', 'traffic', 'hit and run']
    medical_keywords = [
        'heart attack', 'cardiac', 'chest pain', 'fever', 'vomiting', 'injury', 'collapsed',
        'ambulance', 'stroke', 'unconscious', 'unresponsive', 'dizziness', 'fall', 'head injury',
        'allergic reaction', 'respiratory', 'breathing', 'asthma', 'seizure', 'overdose'
    ]

    if any(keyword in description for keyword in fire_keywords):
        return 'Fire'
    if any(keyword in description for keyword in medical_keywords):
        return 'Medical'
    if any(keyword in description for keyword in police_keywords):
        return 'Police'

    return 'EMS'

# --------------------
# ENVIRONMENT SETUP
# --------------------
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'crisislens-api', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# --------------------
# HELPER FUNCTIONS
# --------------------
def random_age():
    return random.randint(18, 90)

def age_group(age):
    if age < 18:
        return 'Under 18'
    elif 18 <= age <= 29:
        return '18-29'
    elif 30 <= age <= 49:
        return '30-49'
    else:
        return '50+'

def random_gender():
    return random.choice(['Male', 'Female'])

def random_response_time():
    return random.randint(2, 20)  # integer minutes (smallint)

# --------------------
# MAIN FUNCTION
# --------------------
def process_new_calls():
    logging.basicConfig(level=logging.INFO)
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM raw_calls
        WHERE processed = 0
        LIMIT 100
    """)
    rows = cursor.fetchall()

    for row in rows:
        description = (row.get('description') or '').strip()
        township = row.get('township') or ''
        latitude = row.get('latitude')
        longitude = row.get('longitude')
        timestamp = row.get('timestamp')

        caller_gender = row.get('gender')
        caller_age = row.get('age')

        if caller_age is None:
            caller_age = random_age()
        if caller_gender not in ['Male', 'Female']:
            caller_gender = random_gender()

        emergency_type = classify_incident(description)
        emergency_subtype = 'General'

        enriched = {
            'timestamp': timestamp,
            'latitude': latitude,
            'longitude': longitude,
            'description': description,
            'emergency_title': description,  # Fixed: assign description as emergency_title
            'emergency_type': emergency_type,
            'emergency_subtype': emergency_subtype,
            'zipcode': '',  # Not available in raw_calls
            'address': '',  # Not available in raw_calls
            'township': township,
            'priority_flag': 0,
            'caller_gender': caller_gender,
            'caller_age': caller_age,
            'response_time': random_response_time(),
            'age_group': age_group(caller_age),
            'source': 'real-time'
        }

        cursor.execute("""
            INSERT INTO enriched_data (
                timestamp, latitude, longitude, description, emergency_title,
                emergency_type, emergency_subtype,
                zipcode, address, township, priority_flag,
                caller_gender, caller_age, response_time, age_group, source
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            enriched['timestamp'], enriched['latitude'], enriched['longitude'], enriched['description'],
            enriched['emergency_title'], enriched['emergency_type'], enriched['emergency_subtype'],
            enriched['zipcode'], enriched['address'], enriched['township'], enriched['priority_flag'],
            enriched['caller_gender'], enriched['caller_age'], enriched['response_time'],
            enriched['age_group'], enriched['source']
        ))

        cursor.execute("UPDATE raw_calls SET processed = 1 WHERE id = %s", (row['id'],))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Processed and enriched {len(rows)} call(s).")

if __name__ == '__main__':
    process_new_calls()
