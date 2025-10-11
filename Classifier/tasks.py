# tasks.py
"""
Background task for processing emergency calls.
This is imported by worker.py and executed by RQ workers.
"""
import os
import sys
from datetime import datetime
import random

# Add paths so we can import from other modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crisislens-API'))

# Import database config and classifier
from db_config import get_connection
from Classifier.classifier_service import classify_call, classify_subtype


def calculate_age_group(age):
    """Categorize age into groups."""
    if age is None:
        return None
    age = int(age)
    if age < 18:
        return 'Child'
    elif age < 35:
        return 'Young Adult'
    elif age < 55:
        return 'Adult'
    else:
        return 'Senior'


def generate_response_time(emergency_type):
    """Generate realistic response times based on emergency type (in minutes)."""
    if emergency_type == 'Fire':
        return random.randint(4, 8)
    elif emergency_type == 'EMS':
        return random.randint(6, 12)
    else:  # Traffic
        return random.randint(8, 15)


def process_emergency_call(raw_call_id):
    """
    Main processing function for emergency calls.
    
    Steps:
    1. Fetch raw call from raw_calls table
    2. Classify main type using ML model (EMS/Fire/Traffic)
    3. Classify subtype using cascading ML models
    4. Enrich with additional data
    5. Insert into enriched_calls table
    6. Mark raw call as processed
    """
    try:
        print(f"\n{'='*60}")
        print(f"Processing call ID: {raw_call_id}")
        print(f"{'='*60}")
        
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Step 1: Fetch raw call
            cursor.execute("SELECT * FROM raw_calls WHERE id = %s", (raw_call_id,))
            raw_call = cursor.fetchone()
            
            if not raw_call:
                print(f"❌ Raw call {raw_call_id} not found")
                return
            
            description = raw_call['description']
            print(f"📞 Call: {description[:100]}...")
            
            # Step 2: Classify main emergency type
            emergency_type = classify_call(description)
            print(f"🏷️  Main Type: {emergency_type}")
            
            # Step 3: Classify subtype using cascading classifier
            emergency_subtype = classify_subtype(description, emergency_type)
            print(f"🏷️  Subtype: {emergency_subtype}")
            
            # Step 4: Enrich
            age_group = calculate_age_group(raw_call.get('age'))
            response_time = generate_response_time(emergency_type)
            
            print(f"📊 Age Group: {age_group}, Response Time: {response_time} min")
            
            # Step 5: Insert into enriched_calls
            insert_query = """
                INSERT INTO enriched_calls (
                    raw_call_id, latitude, longitude, description, zipcode,
                    timestamp, district, address, priority_flag, 
                    emergency_type, emergency_subtype, caller_gender, 
                    caller_age, response_time, age_group, source, processed_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """
            
            values = (
                raw_call_id,
                raw_call['latitude'],
                raw_call['longitude'],
                description,
                raw_call.get('zipcode'),
                raw_call['timestamp'],
                raw_call.get('district'),
                raw_call.get('address'),
                raw_call.get('priority_flag', 0),
                emergency_type,
                emergency_subtype,
                raw_call.get('gender'),
                raw_call.get('age'),
                response_time,
                age_group,
                'WebForm'
            )
            
            cursor.execute(insert_query, values)
            enriched_id = cursor.lastrowid
            
            # Step 6: Mark as processed
            cursor.execute("UPDATE raw_calls SET processed = 1 WHERE id = %s", (raw_call_id,))
            
            conn.commit()
            
            print(f"✅ Enriched call inserted with ID: {enriched_id}")
            print(f"✅ Raw call {raw_call_id} marked as processed")
            print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Error processing call {raw_call_id}: {str(e)}")
        raise