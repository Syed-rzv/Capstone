# suspicion_check.py
import os
import joblib
import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "XGBoost_B_word1-3_char3-5.pkl")
DATA_PATH = r"C:\Capstone\Data\cleaned_data.csv"

# --- Load CSV ---
df = pd.read_csv(DATA_PATH)

# Extract titles and labels
titles = df["emergency_title"].astype(str)  # your CSV has 'emergency_title'
labels = df["emergency_type"].astype(str)   # your CSV has 'emergency_type'

# --- Encode string labels to integers ---
le = LabelEncoder()
labels_encoded = le.fit_transform(labels)

# --- Load model + vectorizer ---
bundle = joblib.load(MODEL_PATH)
vectorizer = bundle["vect"]

# --- Transform titles to TF-IDF vectors ---
X = vectorizer.transform(titles)

# --- Shuffle labels to break mapping ---
y_shuffled = shuffle(labels_encoded, random_state=42)

# --- Train/test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y_shuffled, test_size=0.2, random_state=42, stratify=y_shuffled
)

# --- Train a quick XGBoost ---
xgb = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    n_jobs=-1,
    random_state=42,
    use_label_encoder=False,
    eval_metric="mlogloss"
)
xgb.fit(X_train, y_train)

# --- Evaluate ---
y_pred = xgb.predict(X_test)
y_pred_labels = le.inverse_transform(y_pred)
y_test_labels = le.inverse_transform(y_test)

print("=== Suspicion Check (Shuffled Labels) ===")
print(classification_report(y_test_labels, y_pred_labels))
