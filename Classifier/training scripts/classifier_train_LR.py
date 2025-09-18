# classifier_train.py (Logistic Regression Version)
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def train_classifier(data_path="C:/Capstone/Data/cleaned_data.csv", model_path="models/classifier_lr.pkl"):
    # Load data
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["emergency_title", "emergency_type"])  # Changed to emergency_title
    
    # ADD DUPLICATE CHECKS HERE:
    print("=== DUPLICATE CHECK ===")
    print("Total rows:", len(df))
    print("Unique emergency_titles:", df["emergency_title"].nunique())  # Changed to emergency_title
    
    duplicates = df[df.duplicated("emergency_title")]  # Changed to emergency_title
    print("Duplicate rows:", len(duplicates))
    
    # Check train/test overlap
    X = df["emergency_title"]  # CHANGED: Now using actual emergency descriptions
    y = df["emergency_type"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    overlap = set(X_train) & set(X_test)
    print("Train/test overlap:", len(overlap))
    print("=" * 30)
    
    # ADD SAMPLE DESCRIPTIONS CHECK HERE:
    print("=== SAMPLE EMERGENCY TITLES ===")
    for category in ['EMS', 'Fire', 'Traffic']:
        print(f"\n{category} examples:")
        samples = df[df['emergency_type'] == category]['emergency_title'].head(5)  # Changed to emergency_title
        for i, desc in enumerate(samples, 1):
            print(f"  {i}. {desc}")
    print("=" * 40)
    
    print("Unique labels in data:", df["emergency_type"].unique())
    print("Label counts:\n", df["emergency_type"].value_counts())
    print(f"Total samples: {len(df)}")
    print("-" * 50)
    
    # Improved pipeline for imbalanced data
    clf = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english", 
            ngram_range=(1, 2),      # Include phrases like "heart attack"
            max_features=10000,      # More vocabulary
            min_df=2                 # Ignore very rare words
        )),
        ("lr", LogisticRegression(
            class_weight='balanced', # Handle class imbalance
            max_iter=1000           # Ensure convergence
        ))
    ])
    
    # Train
    print("Training Logistic Regression model...")
    clf.fit(X_train, y_train)
    
    # Evaluate
    acc = clf.score(X_test, y_test)
    y_pred = clf.predict(X_test)
    
    print(f"\nLogistic Regression Results:")
    print(f"Validation Accuracy: {acc:.3f}")
    print("\nDetailed Performance:")
    print(classification_report(y_test, y_pred))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    print("Predicted ->", clf.classes_)
    for i, true_class in enumerate(clf.classes_):
        print(f"{true_class:>8} | {cm[i]}")
    
    # Save model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(clf, model_path)
    print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    train_classifier()