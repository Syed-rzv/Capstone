import pandas as pd
import random

# Load the dataset (only first 150k rows for now)
df = pd.read_csv('C:/Users/97150/OneDrive/Desktop/archive/Data/911.csv', nrows=150000)

# Show basic info
print(df.head())
print(f"Loaded {len(df)} rows")

# Display column names
print("Columns:", df.columns)

# Check for missing values
print("\nMissing values:\n", df.isnull().sum())

# Get data types
print("\nData types:\n", df.dtypes)

# Check unique values in 'title' (emergency types)
print("\nUnique emergency titles:\n", df['title'].unique())

# Renaming columns for clarity

df.rename(columns={
    'lat': 'latitude',
    'lng': 'longitude',
    'desc': 'description',
    'zip': 'zipcode',
    'title': 'emergency_title',
    'timeStamp': 'timestamp',
    'twp': 'township',
    'addr': 'address',
    'e': 'priority_flag'
}, inplace=True)

# Split the emergency title into main category and subcategory
df[['emergency_type', 'emergency_subtype']] = df['emergency_title'].str.split(pat=':', n=1, expand=True)


# Removing whitespaces
df['emergency_type'] = df['emergency_type'].str.strip()
df['emergency_subtype'] = df['emergency_subtype'].str.strip()


# Add simulated columns to your existing DataFrame
df['caller_gender'] = [random.choice(['Male', 'Female']) for _ in range(len(df))]
df['caller_age'] = [random.randint(18, 65) for _ in range(len(df))]
df['response_time'] = [random.randint(5, 30) for _ in range(len(df))]

# Confirm the new columns were added
print(df[['caller_gender', 'caller_age', 'response_time']].head())

# Clean timestamp: remove '@' and convert to datetime
df['timestamp'] = df['timestamp'].str.replace(';', '', regex=False).str.replace('@', '', regex=False).str.strip()
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

print(df['timestamp'].head(10))

# Drop rows where conversion failed (invalid format)
df = df.dropna(subset=['timestamp'])

# Convert back to string format MySQL accepts
df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')


df.to_csv('cleaned_data.csv', index=False)
print("Data saved to cleaned_data.csv")
