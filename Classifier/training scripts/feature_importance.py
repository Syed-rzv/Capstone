# feature_importance.py
import os
import joblib
import matplotlib.pyplot as plt
import numpy as np

# Paths
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

RF_MODEL = os.path.join(MODEL_DIR, "RandomForest_B_word1-3_char3-5.pkl")
XGB_MODEL = os.path.join(MODEL_DIR, "XGBoost_B_word1-3_char3-5.pkl")

# --- Load models and vectorizer ---
if not os.path.exists(RF_MODEL) or not os.path.exists(XGB_MODEL):
    raise FileNotFoundError("Check that your models exist in 'models/'")

rf_bundle = joblib.load(RF_MODEL)
xgb_bundle = joblib.load(XGB_MODEL)

rf = rf_bundle["model"]
xgb = xgb_bundle["model"]
vectorizer = rf_bundle["vect"]  # Both models use the same vectorizer

feature_names = np.array(vectorizer.get_feature_names_out())

# --- Random Forest ---
rf_importances = rf.feature_importances_
top_rf_idx = np.argsort(rf_importances)[-20:][::-1]

print("Top 20 RF features:")
for idx in top_rf_idx:
    print(f"{feature_names[idx]}: {rf_importances[idx]:.4f}")

# --- XGBoost ---
xgb_importances = xgb.feature_importances_
top_xgb_idx = np.argsort(xgb_importances)[-20:][::-1]

print("\nTop 20 XGBoost features:")
for idx in top_xgb_idx:
    print(f"{feature_names[idx]}: {xgb_importances[idx]:.4f}")

# --- Plot XGBoost top features ---
plt.figure(figsize=(10, 6))
plt.barh(range(len(top_xgb_idx)), xgb_importances[top_xgb_idx][::-1], align="center", color="skyblue")
plt.yticks(range(len(top_xgb_idx)), feature_names[top_xgb_idx][::-1])
plt.xlabel("Importance")
plt.title("XGBoost Top 20 Features")
plt.tight_layout()
plt.show()
