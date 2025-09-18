# classifier_train_NB.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

def train_classifier(data_path="C:/Capstone/Data/cleaned_data.csv", model_path="models/classifier_nb.pkl"):
    # Load data

    df = pd.read_csv(data_path)

    # Safety: drop rows missing description or emergency_type
    df = df.dropna(subset=["description", "emergency_type"])

    # ADD THE DEBUG LINES HERE 
    print("Unique labels in data:", df["emergency_type"].unique())
    print("Label counts:\n", df["emergency_type"].value_counts())
    print(f"Total samples: {len(df)}")
    print("-" * 50)  # Just a separator line for clarity

    X = df["description"]       # input text
    y = df["emergency_type"]    # label (Fire/EMS/Traffic)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build pipeline
    clf = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english")),
        ("nb", MultinomialNB())
    ])

    # Train
    clf.fit(X_train, y_train)

    # Evaluate
    acc = clf.score(X_test, y_test)
    print(f"Validation Accuracy: {acc:.2f}")

    # Save model
    joblib.dump(clf, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_classifier()
