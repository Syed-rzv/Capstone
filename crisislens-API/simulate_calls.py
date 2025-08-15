import mysql.connector
import os
import random
import datetime
from dotenv import load_dotenv

# -------------------------------
# 1. Load Database Config
# -------------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'crisislens-api', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# -------------------------------
# 2. Fetch Township Coordinates
# -------------------------------
def fetch_township_coords():
    """Fetch distinct townships with avg coordinates from emergency_data."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT township, AVG(latitude) AS lat, AVG(longitude) AS lon
        FROM emergency_data
        GROUP BY township
        HAVING lat IS NOT NULL AND lon IS NOT NULL
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    township_coords = {row['township']: (row['lat'], row['lon']) for row in rows}
    print(f"✅ Loaded {len(township_coords)} townships with coordinates.")
    return township_coords

# -------------------------------
# 3. Helper Functions for Random Data
# -------------------------------
def random_description():
    samples = [
        "House on fire reported by neighbor",
        "Gunshot heard near downtown",
        "Person collapsed in shopping mall",
        "Car accident with injuries",
        "Smoke detected in apartment building"
    ]
    return random.choice(samples)

def random_gender():
    return random.choice(['Male', 'Female'])

def random_age():
    return random.randint(18, 85)

# -------------------------------
# 4. Insert Simulated Raw Call
# -------------------------------
def insert_simulated_call(township_coords):
    """Insert one simulated raw call using real township + jittered coordinates."""
    township = random.choice(list(township_coords.keys()))
    base_lat, base_lon = township_coords[township]
    lat = round(base_lat + random.uniform(-0.002, 0.002), 6)
    lon = round(base_lon + random.uniform(-0.002, 0.002), 6)

    timestamp = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(0, 1440))
    description = random_description()
    gender = random_gender()
    age = random_age()

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO raw_calls (timestamp, description, latitude, longitude, township, gender, age, processed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
    """, (timestamp, description, lat, lon, township, gender, age))
    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Inserted simulated call: {description} in {township} @ {lat},{lon}")

# -------------------------------
# 5. Main Function
# -------------------------------
def simulate_calls(n=10):
    township_coords = fetch_township_coords()
    for _ in range(n):
        insert_simulated_call(township_coords)

if __name__ == '__main__':
    simulate_calls(20)  # Change number as needed
