import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

print("="*70)
print("RETRAINING MAIN CLASSIFIER WITH NATURAL LANGUAGE")
print("="*70)

# Load combined dataset
print("\nLoading combined dataset...")
df = pd.read_csv('C:/Capstone/Data/montgomery_with_natural_language.csv')
print(f"Total records: {len(df):,}")

# Clean data
df = df.dropna(subset=['emergency_title', 'emergency_type'])
df = df[df['emergency_type'].isin(['EMS', 'Fire', 'Traffic'])]

print(f"\nAfter cleaning: {len(df):,} records")
print("\nDistribution:")
print(df['emergency_type'].value_counts())

# Train/test split
print("\n" + "="*70)
print("TRAIN/TEST SPLIT")
print("="*70)

X = df['emergency_title']
y = df['emergency_type']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {len(X_train):,} records")
print(f"Test: {len(X_test):,} records")

# TF-IDF Vectorization (same config as before)
print("\n" + "="*70)
print("TF-IDF VECTORIZATION")
print("="*70)

vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    min_df=5,
    max_features=15000,
    strip_accents='unicode',
    lowercase=True
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"Vocabulary size: {len(vectorizer.vocabulary_):,}")

# Label encoding
le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

print(f"Classes: {le.classes_}")

# Train XGBoost
print("\n" + "="*70)
print("TRAINING XGBOOST")
print("="*70)

model = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)

print("Training model...")
model.fit(X_train_vec, y_train_enc)
print("✅ Training complete")

# Evaluate
print("\n" + "="*70)
print("EVALUATION")
print("="*70)

y_pred_enc = model.predict(X_test_vec)
y_pred = le.inverse_transform(y_pred_enc)
y_test_arr = le.inverse_transform(y_test_enc)

accuracy = accuracy_score(y_test_arr, y_pred)
print(f"\nTest Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

print("\nClassification Report:")
print(classification_report(y_test_arr, y_pred, digits=4))

# Save model
print("\n" + "="*70)
print("SAVING MODEL")
print("="*70)

model_bundle = {
    'model': model,
    'vect': vectorizer,
    'label_encoder': le
}

# Backup old model first
import shutil
old_model = 'models/XGBoost_Combined_MultiJurisdiction.pkl'
backup_model = 'models/XGBoost_Combined_MultiJurisdiction_OLD.pkl'

try:
    shutil.copy(old_model, backup_model)
    print(f"✅ Backed up old model to: {backup_model}")
except:
    pass

# Save new model
joblib.dump(model_bundle, old_model)
print(f"✅ Saved new model to: {old_model}")

print("\n" + "="*70)
print("MAIN CLASSIFIER RETRAINING COMPLETE")
print("="*70)