import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import sys 
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_split import train_test_split_by_title

def train_classifier(data_path="C:/Capstone/Data/cleaned_data.csv", model_path="models/classifier_svm.pkl"):
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["emergency_title", "emergency_type"])

    print("=== DATA CHECK ===")
    print("Total rows:", len(df))
    print("Unique emergency_titles:", df["emergency_title"].nunique())
    print("Label counts:\n", df["emergency_type"].value_counts())
    print("=" * 40)

    X_train, X_test, y_train, y_test = train_test_split_by_title(
        df, text_col="emergency_title", label_col="emergency_type", test_size=0.2, random_state=42
    )
    overlap = set(X_train) & set(X_test)
    print("Train/test overlap (should be 0):", len(overlap))
    print("=" * 40)

    clf = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 3),
            max_features=15000,
            min_df=5
        )),
        ("svm", LinearSVC(class_weight="balanced", max_iter=5000))
    ])

    print("Training Support Vector Machine model...")
    clf.fit(X_train, y_train)

    acc = clf.score(X_test, y_test)
    y_pred = clf.predict(X_test)

    print(f"\nSVM Results:")
    print(f"Validation Accuracy: {acc:.3f}")
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    print("\nConfusion Matrix:")
    print("Predicted ->", clf.classes_)
    for i, true_class in enumerate(clf.classes_):
        print(f"{true_class:>8} | {cm[i]}")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(clf, model_path)
    print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    train_classifier()
