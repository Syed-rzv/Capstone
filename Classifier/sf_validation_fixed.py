import pandas as pd
import joblib
from sklearn.metrics import classification_report, confusion_matrix

# Load model
print("Loading XGBoost model...")
model_bundle = joblib.load('models/XGBoost_A_word1-3.pkl')
model = model_bundle['model']
vect = model_bundle['vect']

# Load SF data (now in Montgomery format)
print("Loading preprocessed SF data...")
sf = pd.read_csv('C:/Capstone/Data/sf_montgomery_format.csv')
print(f"Loaded {len(sf)} SF samples")

# Sample 50K for testing
sf_sample = sf.sample(n=50000, random_state=42)
print(f"Testing on {len(sf_sample)} samples\n")

# Prepare data
X_sf = sf_sample['emergency_title'].astype(str)
y_sf = sf_sample['emergency_type']

# Transform with TF-IDF
X_sf_vec = vect.transform(X_sf)

# Predict (numeric output)
y_pred_numeric = model.predict(X_sf_vec)

# Map to labels (alphabetical: 0=EMS, 1=Fire, 2=Traffic)
label_map = {0: 'EMS', 1: 'Fire', 2: 'Traffic'}
y_pred = [label_map.get(p, 'Unknown') for p in y_pred_numeric]

# Metrics
print("=== XGBoost on SF Data (Montgomery Format) ===")
print(classification_report(y_sf, y_pred, digits=4))

# Confusion matrix
cm = confusion_matrix(y_sf, y_pred, labels=['EMS', 'Fire', 'Traffic'])
print("\nConfusion Matrix:")
print("             Predicted")
print("           EMS    Fire  Traffic")
for i, true_label in enumerate(['EMS', 'Fire', 'Traffic']):
    print(f"{true_label:>8} | {cm[i]}")

# Show some example predictions
print("\n=== Sample Predictions ===")
for i in range(5):
    print(f"Text: '{X_sf.iloc[i]}'")
    print(f"True: {y_sf.iloc[i]}, Predicted: {y_pred[i]}\n")