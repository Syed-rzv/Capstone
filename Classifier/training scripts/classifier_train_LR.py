# classifier_train_LR.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import sys 
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_split import train_test_split_by_title

def train_classifier(data_path="C:/Capstone/Data/cleaned_data.csv", model_path="models/classifier_lr.pkl"):
    # Load data
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["emergency_title", "emergency_type"])  # ensure required cols exist

    # Quick dataset diagnostics
    print("=== DATA CHECK ===")
    print("Total rows:", len(df))
    print("Unique emergency_titles:", df["emergency_title"].nunique())
    print("Label counts:\n", df["emergency_type"].value_counts())
    print("=" * 40)

    # SAFE SPLIT: by unique titles (prevents leakage)
    X_train, X_test, y_train, y_test = train_test_split_by_title(
        df, text_col="emergency_title", label_col="emergency_type", test_size=0.2, random_state=42      # Start of Selection
    )
    # Verify no leakage
    overlap = set(X_train) & set(X_test)
    print("Train/test overlap (should be 0):", len(overlap))
    print("=" * 40)


    # SAMPLE EXAMPLES (optional, informative)
    print("=== SAMPLE EMERGENCY TITLES ===")
    for category in ['EMS', 'Fire', 'Traffic']:
        print(f"\n{category} examples:")
        samples = df[df['emergency_type'] == category]['emergency_title'].head(5)
        for i, desc in enumerate(samples, 1):
            print(f"  {i}. {desc}")
    print("=" * 40)

    print("Unique labels in data:", df["emergency_type"].unique())
    print(f"Total samples: {len(df)}")
    print("-" * 50)

    # Pipeline (TF-IDF + Logistic Regression)   
    clf = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english", 
            ngram_range=(1, 3),      # Include short phrases
            max_features=15000,
            min_df=5
        )),
        ("lr", LogisticRegression(
            class_weight='balanced',
            max_iter=1000
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
