# rf_xgb_experiments.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.pipeline import FeatureUnion
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE
from utils.data_split import train_test_split_by_title
import joblib
import numpy as np
import time
from sklearn.preprocessing import LabelEncoder

DATA_PATH = "C:/Capstone/Data/cleaned_data.csv"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(OUT_DIR, exist_ok=True)

# TF-IDF vectorizers factory
def make_tfidf(cfg):
    if cfg.get("char_ngrams"):
        from sklearn.feature_extraction.text import TfidfVectorizer as TV
        wu = FeatureUnion([
            ("word", TV(stop_words="english",
                        ngram_range=cfg["word_ngram"],
                        max_features=cfg["max_features"],
                        min_df=cfg["min_df"])),
            ("char", TV(analyzer="char_wb",
                        ngram_range=cfg["char_ngram"],
                        max_features=cfg["char_max_features"],
                        min_df=cfg["min_df"]))
        ])
        return wu
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer as TV
        return TV(stop_words="english",
                  ngram_range=cfg["word_ngram"],
                  max_features=cfg["max_features"],
                  min_df=cfg["min_df"])

# Experiment configs
tfidf_configs = [
    {"name": "A_word1-3", "word_ngram": (1, 3), "min_df": 5,
     "max_features": 15000, "char_ngrams": False},
    {"name": "B_word1-3_char3-5", "word_ngram": (1, 3), "min_df": 5,
     "max_features": 15000, "char_ngrams": True,
     "char_ngram": (3, 5), "char_max_features": 5000}
]

models = [
    ("RandomForest", RandomForestClassifier(
        n_estimators=200, class_weight="balanced",
        n_jobs=-1, random_state=42)),
    ("XGBoost", XGBClassifier(
        use_label_encoder=False, eval_metric="mlogloss",
        random_state=42, verbosity=0))
]

def run_experiment(tf_cfg, model_name, model_obj, use_smote=False):
    print("\n=== EXP:", tf_cfg["name"], model_name, "SMOTE=", use_smote)
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["emergency_title", "emergency_type"])
    X_train, X_test, y_train, y_test = train_test_split_by_title(
        df, text_col="emergency_title",
        label_col="emergency_type",
        test_size=0.2, random_state=42
    )

    # Encode labels if model is XGBoost
    le = None
    if model_name == "XGBoost":
        le = LabelEncoder()
        y_train = le.fit_transform(y_train)
        y_test = le.transform(y_test)

    vect = make_tfidf(tf_cfg)
    print("Fitting TF-IDF...")
    X_train_t = vect.fit_transform(X_train)
    X_test_t = vect.transform(X_test)

    if use_smote:
        print("Applying SMOTE on training vectors (may be slow)...")
        sm = SMOTE(random_state=42)  # FIX: removed n_jobs
        X_train_t, y_train = sm.fit_resample(X_train_t, y_train)

    t0 = time.time()
    model = model_obj
    model.fit(X_train_t, y_train)
    train_time = time.time() - t0

    y_pred = model.predict(X_test_t)

    # Decode labels if XGBoost
    if le is not None:
        y_pred = le.inverse_transform(y_pred)
        y_test = le.inverse_transform(y_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"Acc: {acc:.4f} | Train time: {train_time:.1f}s")
    print("Classification report:")
    print(classification_report(y_test, y_pred, digits=4))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred, labels=sorted(df["emergency_type"].unique())))

    # save model + vectorizer
    name = f"{model_name}_{tf_cfg['name']}{'_SMOTE' if use_smote else ''}"
    joblib.dump({"model": model, "vect": vect}, os.path.join(OUT_DIR, f"{name}.pkl"))
    print("Saved:", name)

if __name__ == "__main__":
    for tf_cfg in tfidf_configs:
        for model_name, model_obj in models:
            for use_smote in [False, True]:
                try:
                    run_experiment(tf_cfg, model_name, model_obj, use_smote=use_smote)
                except Exception as e:
                    print("Error in run:", e)
