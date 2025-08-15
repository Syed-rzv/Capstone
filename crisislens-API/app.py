from flask import Flask, jsonify, request
from flask_cors import CORS
from db_config import get_connection
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

# Load .env if needed (optional)
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# load_dotenv(dotenv_path)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}
app = Flask(__name__)
CORS(app)  # Enables frontend connections (e.g., Power BI or JS frontend)

@app.route('/')
def home():
    return jsonify({"message": "CrisisLens API is running"})


# 🟢 Get all calls (with optional filters + pagination + input validation)
@app.route('/calls', methods=['GET'])
def get_calls():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 🔹 Validate pagination params
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        if page < 1 or limit < 1 or limit > 1000:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid 'page' or 'limit'. Must be positive integers (limit max 1000)."}), 400

    offset = (page - 1) * limit

    # 🔹 Optional filters
    date = request.args.get('date')  # format: YYYY-MM-DD
    emergency_type = request.args.get('type')
    township = request.args.get('township')

    # 🔹 Base query
    query = """
        SELECT id, timestamp, emergency_type, emergency_subtype, township, latitude, longitude,
               description, emergency_title, zipcode, address, priority_flag,
               caller_gender, caller_age, response_time
        FROM emergency_data
        WHERE 1=1
    """
    params = []

    if date:
        query += " AND DATE(timestamp) = %s"
        params.append(date)
    if emergency_type:
        query += " AND emergency_type = %s"
        params.append(emergency_type)
    if township:
        query += " AND township = %s"
        params.append(township)

    # 🔹 Add pagination
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    # 🔹 Run and return
    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "page": page,
        "limit": limit,
        "results": results,
        "count": len(results)
    })


# 📊 Count of calls per emergency type
@app.route('/stats/counts', methods=['GET'])
def get_type_counts():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT emergency_type, COUNT(*) as count
    FROM emergency_data
    GROUP BY emergency_type
    ORDER BY count DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


# 📆 Daily call volume (date vs count)
@app.route('/stats/daily', methods=['GET'])
def get_daily_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT DATE(timestamp) as date, COUNT(*) as count
    FROM emergency_data
    GROUP BY DATE(timestamp)
    ORDER BY date
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


# 🏘️ Calls by township
@app.route('/stats/township', methods=['GET'])
def get_township_counts():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT township, COUNT(*) as count
    FROM emergency_data
    GROUP BY township
    ORDER BY count DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


# 🟠 Ingest a raw emergency call (future-proof pipeline)
@app.route('/calls', methods=['POST'])
def ingest_call():
    data = request.json
    required_fields = ['timestamp', 'description', 'latitude', 'longitude', 'township', 'gender', 'age']

    # 🔍 Input validation
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO raw_calls (timestamp, description, latitude, longitude, township, gender, age)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            data['timestamp'],
            data['description'],
            data['latitude'],
            data['longitude'],
            data['township'],
            data['gender'],
            data['age']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Call successfully ingested"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🟢 NEW: Get latest N enriched calls (for live feed / dashboard)
@app.route('/calls/latest', methods=['GET'])
def get_latest_calls():
    limit = request.args.get('limit', 10)
    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, timestamp, emergency_type, emergency_subtype, township, latitude, longitude,
               description, caller_gender, caller_age, response_time
        FROM emergency_data
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(results)

# 🔮 Get stored forecasted call volumes
@app.route('/forecast', methods=['GET'])
def get_forecast():
    start_date = request.args.get('start_date')  # format YYYY-MM-DD
    end_date = request.args.get('end_date')      # format YYYY-MM-DD
    limit = request.args.get('limit', type=int)  # integer limit

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    query = "SELECT forecast_date, predicted_calls, lower_bound, upper_bound, model_used, generated_at FROM forecast_calls WHERE 1=1"
    params = []

    if start_date:
        query += " AND forecast_date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND forecast_date <= %s"
        params.append(end_date)
    query += " ORDER BY forecast_date ASC"
    if limit:
        query += " LIMIT %s"
        params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert date fields to string for JSON serialization
    for row in results:
        if isinstance(row['forecast_date'], (datetime, )):
            row['forecast_date'] = row['forecast_date'].strftime('%Y-%m-%d')
        if isinstance(row['generated_at'], (datetime, )):
            row['generated_at'] = row['generated_at'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
