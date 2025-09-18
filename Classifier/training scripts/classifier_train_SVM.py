# classifier_train_svm.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def train_classifier(data_path="C:/Capstone/Data/cleaned_data.csv", model_path="models/classifier_svm.pkl"):
    # Load data
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["description", "emergency_type"])

    print("Unique labels in data:", df["emergency_type"].unique())
    print("Label counts:\n", df["emergency_type"].value_counts())
    print(f"Total samples: {len(df)}")
    print("-" * 50)

    X = df["description"]
    y = df["emergency_type"]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Pipeline
    clf = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=10000, min_df=2)),
        ("svm", LinearSVC(class_weight="balanced"))
    ])

    print("Training SVM model...")
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    print("\nSVM Results:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    print("Predicted ->", clf.classes_)
    for i, true_class in enumerate(clf.classes_):
        print(f"{true_class:>8} | {cm[i]}")

    # Save
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(clf, model_path)
    print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    train_classifier()
