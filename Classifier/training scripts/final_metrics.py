# final_metrics.py
import os
import joblib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

RF_MODEL_PATH = os.path.join(MODEL_DIR, "RandomForest_B_word1-3_char3-5.pkl")
XGB_MODEL_PATH = os.path.join(MODEL_DIR, "XGBoost_B_word1-3_char3-5.pkl")
DATA_PATH = r"C:\Capstone\Data\cleaned_data.csv"

# --- Load CSV and extract labels ---
import pandas as pd
df = pd.read_csv(DATA_PATH)
y_test = df["emergency_type"].astype(str)  # string labels
titles = df["emergency_title"].astype(str)

# --- Load models ---
rf_bundle = joblib.load(RF_MODEL_PATH)
xgb_bundle = joblib.load(XGB_MODEL_PATH)

rf_model = rf_bundle["model"]
xgb_model = xgb_bundle["model"]
vectorizer = rf_bundle["vect"]  # assume both use same vectorizer

# --- Transform titles ---
X_test = vectorizer.transform(titles)

# --- Random Forest predictions ---
rf_pred = rf_model.predict(X_test)

print("=== Random Forest Metrics ===")
print(classification_report(y_test, rf_pred, digits=4))

# RF confusion matrix
cm_rf = confusion_matrix(y_test, rf_pred, labels=["EMS", "Fire", "Traffic"])
sns.heatmap(cm_rf, annot=True, fmt="d", cmap="Blues", xticklabels=["EMS","Fire","Traffic"], yticklabels=["EMS","Fire","Traffic"])
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Random Forest Confusion Matrix")
plt.show()

# --- XGBoost predictions ---
xgb_pred_numeric = xgb_model.predict(X_test)
# Map numeric predictions back to string labels
label_map = {0: "EMS", 1: "Fire", 2: "Traffic"}
xgb_pred = [label_map[p] for p in xgb_pred_numeric]

print("\n=== XGBoost Metrics ===")
print(classification_report(y_test, xgb_pred, digits=4))

# XGB confusion matrix
cm_xgb = confusion_matrix(y_test, xgb_pred, labels=["EMS", "Fire", "Traffic"])
sns.heatmap(cm_xgb, annot=True, fmt="d", cmap="Greens", xticklabels=["EMS","Fire","Traffic"], yticklabels=["EMS","Fire","Traffic"])
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("XGBoost Confusion Matrix")
plt.show()
