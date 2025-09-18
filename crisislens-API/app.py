from flask import Flask, jsonify, request
from flask_cors import CORS
from db_config import get_connection
from datetime import datetime
import os
from dotenv import load_dotenv

# For background processing
from redis import Redis
from rq import Queue
import sys

# Add project root to Python path (so we can import Classifier scripts)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Classifier import classifier_enricher

# ------------------------- Configuration -------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)  # Allow frontend / Power BI access

# Redis connection + queue for enrichment jobs
redis_conn = Redis(host="localhost", port=6379, db=0)
q = Queue("crisislens", connection=redis_conn)

# ------------------------- Home -------------------------
@app.route('/')
def home():
    return jsonify({"message": "CrisisLens API is running"})

# ------------------------- Emergency Calls Endpoints -------------------------
@app.route('/calls', methods=['GET'])
def get_calls():
    try:
        page = max(int(request.args.get('page', 1)), 1)
        limit = min(max(int(request.args.get('limit', 100)), 1), 1000)
    except ValueError:
        return jsonify({"error": "Invalid 'page' or 'limit'"}), 400

    offset = (page - 1) * limit
    date = request.args.get('date')  # YYYY-MM-DD
    emergency_type = request.args.get('type')
    emergency_subtype = request.args.get('subtype')
    district = request.args.get('district')

    query = """
        SELECT id, timestamp, emergency_type, emergency_subtype, district, latitude, longitude,
               description, emergency_title, zipcode, address, priority_flag, caller_gender,
               caller_age, response_time, source
        FROM enriched_data WHERE 1=1
    """
    params = []

    if date:
        query += " AND DATE(timestamp) = %s"
        params.append(date)
    if emergency_type:
        query += " AND emergency_type = %s"
        params.append(emergency_type)
    if emergency_subtype:
        query += " AND emergency_subtype = %s"
        params.append(emergency_subtype)
    if district:
        query += " AND district = %s"
        params.append(district)

    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

    return jsonify({"page": page, "limit": limit, "count": len(results), "results": results})


@app.route('/calls/latest', methods=['GET'])
def get_latest_calls():
    limit = request.args.get('limit', 10)
    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    query = """
        SELECT id, timestamp, emergency_type, emergency_subtype, district, latitude, longitude,
               description, caller_gender, caller_age, response_time, source
        FROM enriched_data
        ORDER BY timestamp DESC LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (limit,))
            results = cursor.fetchall()

    return jsonify(results)


@app.route('/calls', methods=['POST'])
def ingest_call():
    data = request.json
    required_fields = ['timestamp', 'description', 'latitude', 'longitude', 'district', 'gender', 'age']

    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    insert_query = """
        INSERT INTO raw_calls (timestamp, description, latitude, longitude, district, gender, age, caller_name, caller_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data['timestamp'], data['description'], data['latitude'], data['longitude'],
        data['district'], data['gender'], data['age'],
        data.get('caller_name'), data.get('caller_number')
    )

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(insert_query, values)
                raw_id = cursor.lastrowid
                conn.commit()

        # Enqueue classification job in background
        q.enqueue(classifier_enricher.process_single_call, raw_id)

        return jsonify({"message": "Call successfully ingested", "raw_id": raw_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------- Stats Endpoints -------------------------
@app.route('/stats/counts', methods=['GET'])
def get_type_counts():
    query = """
        SELECT emergency_type, emergency_subtype, COUNT(*) as count
        FROM enriched_data
        GROUP BY emergency_type, emergency_subtype
        ORDER BY count DESC
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    return jsonify(results)


@app.route('/stats/daily', methods=['GET'])
def get_daily_stats():
    query = """
        SELECT DATE(timestamp) AS date, COUNT(*) AS count
        FROM enriched_data
        GROUP BY DATE(timestamp)
        ORDER BY date
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    return jsonify(results)


@app.route('/stats/district', methods=['GET'])
def get_district_counts():
    query = """
        SELECT district, COUNT(*) AS count
        FROM enriched_data
        GROUP BY district
        ORDER BY count DESC
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    return jsonify(results)

# ------------------------- Forecast Endpoints -------------------------
@app.route('/forecast', methods=['GET'])
def get_forecast():
    start_date = request.args.get('start_date')  # YYYY-MM-DD
    end_date = request.args.get('end_date')      # YYYY-MM-DD
    limit = request.args.get('limit', type=int)
    latest = request.args.get('latest', '').lower() == 'true'

    query = """
        SELECT forecast_date, district, emergency_type, emergency_subtype,
               predicted_calls, lower_bound, upper_bound, model_used, source, generated_at
        FROM forecasted_calls WHERE 1=1
    """
    params = []

    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            if latest:
                cursor.execute("SELECT MAX(generated_at) AS last_run FROM forecasted_calls")
                last = cursor.fetchone()['last_run']
                if last:
                    query += " AND generated_at = %s"
                    params.append(last)
                else:
                    return jsonify([])

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

            # Convert datetime to string
            for row in results:
                if isinstance(row['forecast_date'], datetime):
                    row['forecast_date'] = row['forecast_date'].strftime('%Y-%m-%d')
                if isinstance(row['generated_at'], datetime):
                    row['generated_at'] = row['generated_at'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify(results)

# ------------------------- Entry Point -------------------------
if __name__ == '__main__':
    app.run(debug=True)
