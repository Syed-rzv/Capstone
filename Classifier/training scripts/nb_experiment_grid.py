# nb_experiment_grid.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project classifier root
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from utils.data_split import train_test_split_by_title

DATA_PATH = "C:/Capstone/Data/cleaned_data.csv"

configs = [
    {"name": "NB_baseline", "ngram_range": (1,2), "min_df": 2, "max_features": 10000},
    {"name": "NB_cleaner",  "ngram_range": (1,2), "min_df": 3, "max_features": 10000},
    {"name": "NB_lr_like",  "ngram_range": (1,3), "min_df": 5, "max_features": 15000},
]

def run_config(cfg, X_train, X_test, y_train, y_test):
    tfidf = TfidfVectorizer(stop_words="english",
                            ngram_range=cfg["ngram_range"],
                            max_features=cfg["max_features"],
                            min_df=cfg["min_df"])
    clf = Pipeline([("tfidf", tfidf), ("nb", MultinomialNB())])
    print(f"\n=== Running {cfg['name']} | ngram={cfg['ngram_range']} min_df={cfg['min_df']} max_feat={cfg['max_features']} ===")
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print("Classification report:")
    print(classification_report(y_test, y_pred, digits=4))
    print("Confusion matrix (rows=true, cols=pred):")
    print(confusion_matrix(y_test, y_pred, labels=clf.classes_))
    # Save model (optional)
    out_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    os.makedirs(out_dir, exist_ok=True)
    joblib_path = os.path.join(out_dir, f"{cfg['name']}.pkl")
    try:
        import joblib
        joblib.dump(clf, joblib_path)
        print("Saved model to", joblib_path)
    except Exception:
        pass

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["emergency_title", "emergency_type"])
    X_train, X_test, y_train, y_test = train_test_split_by_title(df, text_col="emergency_title", label_col="emergency_type", test_size=0.2, random_state=42)
    for cfg in configs:
        run_config(cfg, X_train, X_test, y_train, y_test)
