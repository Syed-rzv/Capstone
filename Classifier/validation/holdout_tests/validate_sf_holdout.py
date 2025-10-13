import pandas as pd
import joblib
from sklearn.metrics import classification_report, confusion_matrix

print("=== SF Held-Out Validation ===\n")

# Load combined model
model_bundle = joblib.load('models/XGBoost_Combined_MultiJurisdiction.pkl')
model = model_bundle['model']
vect = model_bundle['vect']
le = model_bundle['label_encoder']

# Load FULL SF dataset
sf_full = pd.read_csv('C:/Capstone/Data/sf_montgomery_format.csv')
print(f"Full SF dataset: {len(sf_full)} rows")

# Sample 50K that were NOT in training (use different seed)
# Training used random_state=42, so use 123 for held-out
sf_holdout = sf_full.sample(n=50000, random_state=123)
print(f"Held-out sample: {len(sf_holdout)} rows\n")

# Prepare data
X_sf = sf_holdout['emergency_title'].astype(str)
y_sf = sf_holdout['emergency_type']

# Transform
X_sf_vec = vect.transform(X_sf)

# Predict
y_pred_enc = model.predict(X_sf_vec)
y_pred = le.inverse_transform(y_pred_enc)

# Metrics
print("=== XGBoost Combined Model on SF Held-Out Data ===")
print(classification_report(y_sf, y_pred, digits=4))

# Confusion matrix
cm = confusion_matrix(y_sf, y_pred, labels=['EMS', 'Fire', 'Traffic'])
print("\nConfusion Matrix:")
print("             Predicted")
print("           EMS    Fire  Traffic")
for i, true_label in enumerate(['EMS', 'Fire', 'Traffic']):
    print(f"{true_label:>8} | {cm[i]}")

# Compare to baseline (Montgomery-only model)
print("\n" + "="*60)
print("COMPARISON")
print("="*60)
print("Baseline (Montgomery-only XGBoost):")
print("  - Overall accuracy: 96%")
print("  - Traffic recall: 1.5% (31/2035)")
print("\nCombined Model (this run):")
traffic_mask = y_sf == 'Traffic'
traffic_correct = (y_pred[traffic_mask] == 'Traffic').sum()
traffic_total = traffic_mask.sum()
traffic_recall = traffic_correct / traffic_total
print(f"  - Overall accuracy: {(y_pred == y_sf).mean():.4f}")
print(f"  - Traffic recall: {traffic_recall:.4f} ({traffic_correct}/{traffic_total})")

if traffic_recall > 0.50:
    print("\n🎉 MAJOR IMPROVEMENT! Traffic recall fixed by multi-jurisdiction training.")
else:
    print("\n⚠️ Traffic recall still low. Further investigation needed.")