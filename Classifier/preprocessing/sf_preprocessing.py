import pandas as pd

# Load SF data
sf = pd.read_csv('C:/Capstone/SF_data.csv')

print(f"Total SF rows: {len(sf)}")
print(f"\nUnique CallTypes: {sf['CallType'].nunique()}")
print(f"\nCallType value counts:")
print(sf['CallType'].value_counts().head(20))

# Map SF CallType to your EMS/Fire/Traffic taxonomy
def map_sf_to_taxonomy(call_type):
    call_type = str(call_type).lower()
    
    # Fire mappings
    if any(kw in call_type for kw in ['fire', 'explosion', 'smoke', 'alarm', 'hazmat']):
        return 'Fire'
    
    # EMS mappings
    if any(kw in call_type for kw in ['medical', 'illness', 'injury', 'cardiac', 
                                        'overdose', 'seizure', 'breathing']):
        return 'EMS'
    
    # Traffic mappings
    if any(kw in call_type for kw in ['vehicle', 'accident', 'collision', 'traffic']):
        return 'Traffic'
    
    return 'Other'

# Apply mapping
sf['emergency_type'] = sf['CallType'].apply(map_sf_to_taxonomy)

print(f"\n=== Mapped SF Data ===")
print(sf['emergency_type'].value_counts())
print(f"\nSample mappings:")
for et in ['EMS', 'Fire', 'Traffic']:
    print(f"\n{et} examples:")
    print(sf[sf['emergency_type'] == et]['CallType'].value_counts().head(5))

# Keep only EMS/Fire/Traffic (drop 'Other')
sf_clean = sf[sf['emergency_type'].isin(['EMS', 'Fire', 'Traffic'])].copy()
print(f"\n=== After filtering ===")
print(f"Total compatible rows: {len(sf_clean)}")
print(sf_clean['emergency_type'].value_counts())

# Save for validation
sf_clean[['CallType', 'emergency_type']].to_csv('C:/Capstone/Data/sf_clean_mapped.csv', index=False)
print("\nSaved to C:/Capstone/Data/sf_clean_mapped.csv")