from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv(dotenv_path=os.path.join("..", "crisislens-api", ".env"))
print(os.getenv("DB_HOST"))

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    allow_local_infile=True  
)

cursor = conn.cursor()

query = """
LOAD DATA LOCAL INFILE "C:/Program Files/MySQL/MySQL Server 8.0/data/bulk_raw_calls.csv"
INTO TABLE raw_calls
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(timestamp, description, latitude, longitude, township, gender, age);
"""

cursor.execute(query)
conn.commit()
cursor.close()
conn.close()

print("✅ Data loaded successfully.")
