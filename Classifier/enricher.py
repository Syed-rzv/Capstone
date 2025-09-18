# enricher.py
import random

def enrich_record(record: dict) -> dict:
    """Takes a record with 'description' + adds demographics and metadata."""
    # Example enrichments
    record["caller_gender"] = random.choice(["Male", "Female"])
    record["caller_age_group"] = random.choice(["Child", "Adult", "Senior"])
    record["response_time"] = random.randint(3, 15)  # minutes
    return record
