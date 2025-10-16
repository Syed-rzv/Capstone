from flask import Flask, jsonify, request
from flask_cors import CORS
from db_config import get_connection
from datetime import datetime
import os
from dotenv import load_dotenv

from functools import lru_cache
from time import time 

# For background processing
from redis import Redis
from rq import Queue
import sys

from clustering import analyze_emergency_clusters
import pandas as pd

# Add project root to Python path (so we can import Classifier scripts)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the background processing function
from Classifier.production.tasks import process_emergency_call

# ------------------------- Configuration -------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app, resources={       # Allow frontend access
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
}) 

# Redis connection + queue for enrichment jobs
redis_conn = Redis(host="localhost", port=6379, db=0)
q = Queue("crisislens", connection=redis_conn)
# ------------------------- Home -------------------------
@app.route('/')
def home():
    return jsonify({"message": "CrisisLens API is running"})

# ------------------------- Emergency Calls Endpoints -------------------------
# ------------------------- Emergency Calls Endpoints -------------------------
@app.route('/calls', methods=['GET'])
def get_calls():
    try:
        page = max(int(request.args.get('page', 1)), 1)
        limit = min(max(int(request.args.get('limit', 100)), 1), 50000)
    except ValueError:
        return jsonify({"error": "Invalid 'page' or 'limit'"}), 400

    offset = (page - 1) * limit
    date = request.args.get('date')
    emergency_type = request.args.get('type')
    emergency_subtype = request.args.get('subtype')
    district = request.args.get('district')  # Frontend sends 'district'
    source_filter = request.args.get('source', 'all')

    # Build WHERE conditions (need to handle both column names)
    where_conditions = []
    params = []

    if date:
        where_conditions.append("DATE(timestamp) = %s")
        params.append(date)
    if emergency_type:
        where_conditions.append("emergency_type = %s")
        params.append(emergency_type)
    if emergency_subtype:
        where_conditions.append("emergency_subtype = %s")
        params.append(emergency_subtype)

    # Build query based on source
    if source_filter == 'live':
        # enriched_calls uses 'district' column
        if district:
            where_conditions.append("district = %s")
            params.append(district)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT 
                id, timestamp, emergency_type, emergency_subtype, 
                district, latitude, longitude, description,
                zipcode, address, priority_flag, caller_gender,
                caller_age, response_time, source, 'live' as data_source
            FROM enriched_calls 
            WHERE {where_clause}
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
        """
        
    elif source_filter == 'historical':
        # emergency_data uses 'township' column - alias it as 'district'
        if district:
            where_conditions.append("township = %s")
            params.append(district)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT 
                id, timestamp, emergency_type, emergency_subtype,
                township AS district, latitude, longitude, description, emergency_title,
                zipcode, address, priority_flag, caller_gender,
                caller_age, response_time, source, 'historical' as data_source
            FROM emergency_data 
            WHERE {where_clause}
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
        """
        
    else: 
        # CRITICAL: UNION queries need DUPLICATE parameters (one set per SELECT)
        live_params = list(params)  # Copy base filters for first SELECT
        historical_params = list(params)  # Copy base filters for second SELECT

        # Build WHERE clause lists
        live_where = list(where_conditions)
        historical_where = list(where_conditions)
    
    # Add district filter to both if present
    if district:
        live_where.append("district = %s")
        historical_where.append("township = %s")
        live_params.append(district)
        historical_params.append(district)
    
    # Build final WHERE clauses
    live_clause = " AND ".join(live_where) if live_where else "1=1"
    historical_clause = " AND ".join(historical_where) if historical_where else "1=1"
    
    query = f"""
        SELECT * FROM (
            SELECT 
                id, timestamp, emergency_type, emergency_subtype,
                district, latitude, longitude, description,
                NULL as emergency_title,
                zipcode, address, priority_flag, caller_gender,
                caller_age, response_time, source, 'live' as data_source
            FROM enriched_calls
            WHERE {live_clause}
            
            UNION ALL
            
            SELECT 
                id, timestamp, emergency_type, emergency_subtype,
                township AS district, latitude, longitude, description, emergency_title,
                zipcode, address, priority_flag, caller_gender,
                caller_age, response_time, source, 'historical' as data_source
            FROM emergency_data
            WHERE {historical_clause}
        ) AS combined_data
        ORDER BY timestamp DESC
        LIMIT %s OFFSET %s
    """
    
    # Combine: live_params + historical_params
    params = live_params + historical_params

    params.extend([limit, offset])

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()

        return jsonify({
            "page": page, 
            "limit": limit, 
            "count": len(results), 
            "results": results
        })
    except Exception as e:
        print(f"❌ Error in /calls: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/calls/latest', methods=['GET'])
def get_latest_calls():
    limit = request.args.get('limit', 10)
    source_filter = request.args.get('source', 'all')
    
    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    if source_filter == 'live':
        query = """
            SELECT 
                id, timestamp, emergency_type, emergency_subtype, 
                district, latitude, longitude, description, 
                caller_gender, caller_age, response_time, source,
                'live' as data_source
            FROM enriched_calls
            ORDER BY timestamp DESC 
            LIMIT %s
        """
    elif source_filter == 'historical':
        query = """
            SELECT 
                id, timestamp, emergency_type, emergency_subtype,
                township AS district, latitude, longitude, description,
                caller_gender, caller_age, response_time, source,
                'historical' as data_source
            FROM emergency_data
            ORDER BY timestamp DESC 
            LIMIT %s
        """
    else:  # 'all'
        query = """
            SELECT * FROM (
                SELECT 
                    id, timestamp, emergency_type, emergency_subtype,
                    district, latitude, longitude, description,
                    caller_gender, caller_age, response_time, source,
                    'live' as data_source
                FROM enriched_calls
                
                UNION ALL
                
                SELECT 
                    id, timestamp, emergency_type, emergency_subtype,
                    township AS district, latitude, longitude, description,
                    caller_gender, caller_age, response_time, source,
                    'historical' as data_source
                FROM emergency_data
            ) AS combined
            ORDER BY timestamp DESC
            LIMIT %s
        """

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (limit,))
                results = cursor.fetchall()

        return jsonify(results)
    except Exception as e:
        print(f"❌ Error in /calls/latest: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/calls', methods=['POST'])
def ingest_call():
    data = request.json

    print("📥 Received data:", data)

    required_fields = ['timestamp', 'description', 'latitude', 'longitude', 'district', 'gender', 'age']

    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    for field in required_fields:
        if field not in data:
            print(f"❌ Missing field: {field}")
            return jsonify({"error": f"Missing field: {field}"}), 400
    # CONVERT ISO timestamp to MySQL format
    try:
        iso_timestamp = data['timestamp']
        # Remove 'Z' and convert to MySQL datetime format
        mysql_timestamp = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return jsonify({"error": f"Invalid timestamp format: {str(e)}"}), 400

    insert_query = """
        INSERT INTO raw_calls (timestamp, description, latitude, longitude, district, gender, age, caller_name, caller_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        mysql_timestamp, 
        data['description'], 
        data['latitude'], 
        data['longitude'],
        data['district'],  
        data['gender'], 
        data['age'],
        data.get('caller_name'), 
        data.get('caller_number')
    )

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(insert_query, values)
                raw_id = cursor.lastrowid
                conn.commit()

                print(f"✅ Inserted into raw_calls with ID: {raw_id}")  # ← ADD THIS
                print(f"   caller_name: {data.get('caller_name')}")      # ← ADD THIS
                print(f"   caller_number: {data.get('caller_number')}")  # ← ADD THIS

        # Enqueue classification job in background
        job = q.enqueue(process_emergency_call, raw_id)
        print(f"✅ Call {raw_id} enqueued for processing. Job ID: {job.id}")

        return jsonify({"message": "Call successfully ingested (enrichment pending)", "raw_id": raw_id}), 201
    except Exception as e:
        print(f" Database error: {str(e)}")  # Added for debugging
        return jsonify({"error": str(e)}), 500
# ------------------------- Stats Endpoints -------------------------
@app.route('/stats/counts', methods=['GET'])
def get_type_counts():
    query = """
        SELECT emergency_type, emergency_subtype, COUNT(*) as count
        FROM emergency_data
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
        FROM emergency_data
        GROUP BY DATE(timestamp)
        ORDER BY date
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    return jsonify(results)


@app.route('/stats/township', methods=['GET'])
def get_township_counts():
    query = """
        SELECT township, COUNT(*) AS count
        FROM emergency_data
        GROUP BY township
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
            SELECT forecast_date, township as district, emergency_type, emergency_subtype,
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


# Simple cache: stores results for 5 minutes
cluster_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 300  # 5 minutes in seconds

# ------------------------- Clustering Endpoints -------------------------
@app.route('/clusters', methods=['GET'])
def get_clusters():
    """
    DBSCAN clustering analysis endpoint.
    Query params: time_range ('day'/'night'/'all'), min_severity (float)
    """
    try:
        time_range = request.args.get('time_range', 'all')
        min_severity = request.args.get('min_severity', type=float)
        
        # Create cache key from parameters
        cache_key = f"{time_range}_{min_severity}"
        
        # Check cache first
        if (cluster_cache["data"] and 
            cluster_cache["params"] == cache_key and 
            (time() - cluster_cache["timestamp"]) < CACHE_DURATION):
            return jsonify(cluster_cache["data"]), 200
        
        # Fetch data from database (last 30 days for performance)
        query = """
          SELECT latitude as lat, longitude as lon, 
           COALESCE(emergency_type, 'Unknown') as call_type,
           COALESCE(response_time, 10) as response_time, 
           timestamp,
           CASE COALESCE(emergency_type, 'Unknown')
               WHEN 'Fire' THEN 9
               WHEN 'Medical Emergency' THEN 8
               WHEN 'Accident' THEN 7
               WHEN 'Assault' THEN 7
               WHEN 'Robbery' THEN 6
               WHEN 'Burglary' THEN 5
               ELSE 3
           END as severity
    FROM emergency_data
    WHERE latitude IS NOT NULL 
      AND longitude IS NOT NULL
    LIMIT 50000
        """
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        
        df = pd.DataFrame(results)
        
        if df.empty:
            return jsonify({"error": "No data available for clustering"}), 404
        
        # Apply time filter if specified
        if time_range == 'day':
            df = df.copy()  # Prevent SettingWithCopyWarning
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df = df[(df['hour'] >= 6) & (df['hour'] < 18)].copy()
        elif time_range == 'night':
            df = df.copy()
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df = df[(df['hour'] < 6) | (df['hour'] >= 18)].copy()

        # Check if we still have data after filtering
        if df.empty:
            return jsonify({"error": "No data available for selected time range"}), 404
        
        # Run clustering analysis
        results = analyze_emergency_clusters(df)
        
        # Apply severity filter if specified
        if min_severity:
            results['clusters'] = [
                c for c in results['clusters'] 
                if c['severity_score'] >= min_severity
            ]
        
        # Cache the results
        cluster_cache["data"] = results
        cluster_cache["params"] = cache_key
        cluster_cache["timestamp"] = time()
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clusters/heatmap-data', methods=['GET'])
def get_heatmap_data():
    """Endpoint for heatmap visualization intensity data."""
    try:
        query = """
            SELECT latitude as lat, longitude as lon,
                   CASE emergency_type
                       WHEN 'Fire' THEN 0.9
                       WHEN 'Medical Emergency' THEN 0.85
                       WHEN 'Accident' THEN 0.7
                       WHEN 'Assault' THEN 0.75
                       WHEN 'Robbery' THEN 0.65
                       ELSE 0.4
                   END as intensity
            FROM emergency_data
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            LIMIT 5000
        """
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        
        # Format for Leaflet heatmap: [lat, lon, intensity]
        heatmap_data = [
            [float(row['lat']), float(row['lon']), float(row['intensity'])]
            for row in results
        ]
        
        return jsonify({"data": heatmap_data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------- Entry Point -------------------------
if __name__ == '__main__':
    app.run(debug=True)
