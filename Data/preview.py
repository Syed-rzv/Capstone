import pandas as pd

# Load the dataset
df = pd.read_csv('911.csv', nrows=150000)

# Show a sample
print(df.head())

# Show column names
print(f"loaded {len(df)} rows")

