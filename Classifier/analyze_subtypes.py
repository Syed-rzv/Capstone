import pandas as pd

# Load Montgomery data
df = pd.read_csv('C:/Capstone/Data/cleaned_data.csv')

print("="*60)
print("SUBTYPE DISTRIBUTION ANALYSIS")
print("="*60)

# Overall counts
print(f"\nTotal records: {len(df):,}")
print(f"Unique emergency_types: {df['emergency_type'].nunique()}")
print(f"Unique emergency_subtypes: {df['emergency_subtype'].nunique()}")

print("\n" + "="*60)
print("MAIN TYPE DISTRIBUTION")
print("="*60)
type_counts = df['emergency_type'].value_counts()
for etype, count in type_counts.items():
    pct = (count / len(df)) * 100
    print(f"{etype:12s}: {count:6,} ({pct:5.2f}%)")

print("\n" + "="*60)
print("SUBTYPE DISTRIBUTION BY MAIN TYPE")
print("="*60)

for main_type in ['EMS', 'Fire', 'Traffic']:
    print(f"\n{main_type} SUBTYPES:")
    print("-" * 50)
    
    subset = df[df['emergency_type'] == main_type]
    subtype_counts = subset['emergency_subtype'].value_counts()
    
    print(f"Total {main_type} calls: {len(subset):,}")
    print(f"Unique subtypes: {len(subtype_counts)}")
    print(f"\nTop 15 subtypes:")
    
    for i, (subtype, count) in enumerate(subtype_counts.head(15).items(), 1):
        pct = (count / len(subset)) * 100
        print(f"{i:2d}. {subtype:45s}: {count:5,} ({pct:5.2f}%)")
    
    # Check for rare subtypes
    rare = subtype_counts[subtype_counts < 50]
    if len(rare) > 0:
        print(f"\n⚠️  {len(rare)} rare subtypes with <50 examples (might exclude)")

print("\n" + "="*60)
print("RECOMMENDATIONS")
print("="*60)

for main_type in ['EMS', 'Fire', 'Traffic']:
    subset = df[df['emergency_type'] == main_type]
    subtype_counts = subset['emergency_subtype'].value_counts()
    
    # Filter to subtypes with sufficient data
    sufficient = subtype_counts[subtype_counts >= 100]
    
    print(f"\n{main_type}:")
    print(f"  - Total subtypes: {len(subtype_counts)}")
    print(f"  - Subtypes with ≥100 examples: {len(sufficient)}")
    print(f"  - Coverage: {sufficient.sum() / len(subset) * 100:.1f}% of {main_type} calls")
    print(f"  - Recommended for training: {len(sufficient)} classes")