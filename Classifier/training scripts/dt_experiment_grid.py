# dt_experiment_grid.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # add classifier root
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from utils.data_split import train_test_split_by_title
import joblib

DATA_PATH = "C:/Capstone/Data/cleaned_data.csv"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(OUT_DIR, exist_ok=True)

configs = [
    {"name": "DT_unpruned", "max_depth": None, "min_samples_leaf": 1, "min_samples_split": 2},
    {"name": "DT_pruned_light", "max_depth": 30, "min_samples_leaf": 5, "min_samples_split": 10},
    {"name": "DT_pruned_strong", "max_depth": 12, "min_samples_leaf": 20, "min_samples_split": 40},
]

tfidf_cfg = {"ngram_range": (1,3), "min_df": 5, "max_features": 15000}

def run_config(cfg, X_train, X_test, y_train, y_test):
    tfidf = TfidfVectorizer(stop_words="english",
                            ngram_range=tfidf_cfg["ngram_range"],
                            max_features=tfidf_cfg["max_features"],
                            min_df=tfidf_cfg["min_df"])
    clf = Pipeline([
        ("tfidf", tfidf),
        ("dt", DecisionTreeClassifier(
            class_weight="balanced",
            random_state=42,
            max_depth=cfg["max_depth"],
            min_samples_leaf=cfg["min_samples_leaf"],
            min_samples_split=cfg["min_samples_split"]
        ))
    ])
    print(f"\n=== Running {cfg['name']} | max_depth={cfg['max_depth']} min_leaf={cfg['min_samples_leaf']} min_split={cfg['min_samples_split']} ===")
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print("Classification report:")
    print(classification_report(y_test, y_pred, digits=4))
    print("Confusion matrix (rows=true, cols=pred):")
    print(confusion_matrix(y_test, y_pred, labels=clf.classes_))

    # Save model
    joblib.dump(clf, os.path.join(OUT_DIR, f"{cfg['name']}.pkl"))
    print("Saved model to", os.path.join(OUT_DIR, f"{cfg['name']}.pkl"))

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["emergency_title", "emergency_type"])
    X_train, X_test, y_train, y_test = train_test_split_by_title(df, text_col="emergency_title", label_col="emergency_type", test_size=0.2, random_state=42)
    for cfg in configs:
        run_config(cfg, X_train, X_test, y_train, y_test)
