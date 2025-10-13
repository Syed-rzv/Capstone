import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

print("=== Multi-Jurisdiction Training ===\n")

# Load datasets
print("Loading datasets...")
montgomery = pd.read_csv('C:/Capstone/Data/cleaned_data.csv')
sf = pd.read_csv('C:/Capstone/Data/sf_montgomery_format.csv')
us_accidents = pd.read_csv('C:/Capstone/Data/us_accidents_montgomery_format.csv')

print(f"Montgomery: {len(montgomery)} rows")
print(f"SF: {len(sf)} rows")
print(f"US Accidents: {len(us_accidents)} rows")

# Sample SF to balance dataset size (SF is huge)
print("\nBalancing dataset sizes...")
sf_sample = sf.sample(n=200000, random_state=42)
print(f"SF sampled to: {len(sf_sample)} rows")

# Combine datasets
print("\nCombining datasets...")
combined = pd.concat([
    montgomery[['emergency_title', 'emergency_type']],
    sf_sample[['emergency_title', 'emergency_type']],
    us_accidents[['emergency_title', 'emergency_type']]
], ignore_index=True)

# Clean
combined = combined.dropna(subset=['emergency_title', 'emergency_type'])
combined = combined[combined['emergency_type'].isin(['EMS', 'Fire', 'Traffic'])]

print(f"\n=== Combined Dataset ===")
print(f"Total rows: {len(combined)}")
print(f"\nDistribution:")
print(combined['emergency_type'].value_counts())
print(f"\nPercentages:")
print(combined['emergency_type'].value_counts(normalize=True) * 100)

# Train/test split (80/20)
print("\n=== Train/Test Split ===")
X = combined['emergency_title']
y = combined['emergency_type']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {len(X_train)} rows")
print(f"Test: {len(X_test)} rows")

# TF-IDF Vectorization (same config as your best model)
print("\n=== TF-IDF Vectorization ===")
vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    min_df=5,
    max_features=15000
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")

# Label encoding
le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

print(f"Classes: {le.classes_}")

# Train XGBoost
print("\n=== Training XGBoost ===")
model = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42
)

model.fit(X_train_vec, y_train_enc)
print("✅ Training complete")

# Predict
y_pred_enc = model.predict(X_test_vec)
y_pred = le.inverse_transform(y_pred_enc)
y_test_arr = le.inverse_transform(y_test_enc)

# Overall metrics
print("\n=== Overall Test Results ===")
print(classification_report(y_test_arr, y_pred, digits=4))

# Confusion matrix
cm = confusion_matrix(y_test_arr, y_pred, labels=['EMS', 'Fire', 'Traffic'])
print("\nConfusion Matrix:")
print("             Predicted")
print("           EMS    Fire  Traffic")
for i, true_label in enumerate(['EMS', 'Fire', 'Traffic']):
    print(f"{true_label:>8} | {cm[i]}")

# Save model
model_bundle = {
    'model': model,
    'vect': vectorizer,
    'label_encoder': le
}

output_path = 'models/XGBoost_Combined_MultiJurisdiction.pkl'
joblib.dump(model_bundle, output_path)
print(f"\n✅ Model saved to: {output_path}")

# Test on each dataset separately
print("\n" + "="*60)
print("=== Validation on Individual Datasets ===")
print("="*60)

# Montgomery validation
print("\n--- Montgomery Validation ---")
mont_test = montgomery.sample(n=10000, random_state=42)
X_mont = vectorizer.transform(mont_test['emergency_title'])
y_mont_true = mont_test['emergency_type']
y_mont_pred_enc = model.predict(X_mont)
y_mont_pred = le.inverse_transform(y_mont_pred_enc)
print(classification_report(y_mont_true, y_mont_pred, digits=4))

# SF validation
print("\n--- SF Validation ---")
sf_test = sf.sample(n=10000, random_state=42)
X_sf = vectorizer.transform(sf_test['emergency_title'])
y_sf_true = sf_test['emergency_type']
y_sf_pred_enc = model.predict(X_sf)
y_sf_pred = le.inverse_transform(y_sf_pred_enc)
print(classification_report(y_sf_true, y_sf_pred, digits=4))

# US Accidents validation
print("\n--- US Accidents Validation ---")
us_test = us_accidents.sample(n=10000, random_state=42)
X_us = vectorizer.transform(us_test['emergency_title'])
y_us_true = us_test['emergency_type']
y_us_pred_enc = model.predict(X_us)
y_us_pred = le.inverse_transform(y_us_pred_enc)
print(classification_report(y_us_true, y_us_pred, digits=4))

print("\n" + "="*60)
print("🎉 Multi-jurisdiction training complete!")
print("="*60)