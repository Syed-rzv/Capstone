import pandas as pd

# Load SF data
print("Loading SF data...")
sf = pd.read_csv('C:/Capstone/SF_data.csv', low_memory=False)
print(f"Loaded {len(sf)} rows")

# Map SF CallType to Montgomery-style emergency_title format
def create_montgomery_format(call_type):
    """
    Convert SF CallType to Montgomery emergency_title format.
    Example: "Medical Incident" → "EMS: MEDICAL INCIDENT"
             "Structure Fire" → "Fire: STRUCTURE FIRE"
    """
    call_type_clean = str(call_type).strip().upper()
    
    # EMS mappings
    ems_keywords = [
        'MEDICAL', 'ILLNESS', 'INJURY', 'CARDIAC', 'OVERDOSE', 
        'SEIZURE', 'BREATHING', 'UNCONSCIOUS', 'CHEST PAIN'
    ]
    
    # Fire mappings
    fire_keywords = [
        'FIRE', 'EXPLOSION', 'SMOKE', 'ALARM', 'HAZMAT', 'GAS LEAK',
        'ELECTRICAL HAZARD', 'FUEL SPILL', 'ODOR'
    ]
    
    # Traffic mappings
    traffic_keywords = [
        'VEHICLE', 'ACCIDENT', 'COLLISION', 'TRAFFIC', 'EXTRICATION'
    ]
    
    # Determine category and format like Montgomery
    if any(kw in call_type_clean for kw in fire_keywords):
        return f"Fire: {call_type_clean}"
    elif any(kw in call_type_clean for kw in ems_keywords):
        return f"EMS: {call_type_clean}"
    elif any(kw in call_type_clean for kw in traffic_keywords):
        return f"Traffic: {call_type_clean}"
    else:
        return None  # Incompatible type

# Create Montgomery-style emergency_title
print("\nCreating Montgomery-format titles...")
sf['emergency_title'] = sf['CallType'].apply(create_montgomery_format)

# Filter out incompatible types (None values)
sf_compatible = sf[sf['emergency_title'].notna()].copy()

# Extract emergency_type from the prefix
sf_compatible['emergency_type'] = sf_compatible['emergency_title'].str.split(':', n=1).str[0]

print(f"\n=== Preprocessing Results ===")
print(f"Original SF rows: {len(sf)}")
print(f"Compatible rows: {len(sf_compatible)} ({len(sf_compatible)/len(sf)*100:.1f}%)")
print(f"\nDistribution:")
print(sf_compatible['emergency_type'].value_counts())

print(f"\nSample transformed titles:")
for et in ['EMS', 'Fire', 'Traffic']:
    print(f"\n{et} examples:")
    samples = sf_compatible[sf_compatible['emergency_type'] == et]['emergency_title'].unique()[:3]
    for s in samples:
        print(f"  {s}")

# Save processed data
output_path = 'C:/Capstone/Data/sf_montgomery_format.csv'
sf_compatible[['emergency_title', 'emergency_type']].to_csv(output_path, index=False)
print(f"\nSaved to: {output_path}")