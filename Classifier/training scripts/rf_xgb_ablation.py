# rf_xgb_ablation_fixed.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder
from utils.data_split import train_test_split_by_title
import joblib
import numpy as np
import time

DATA_PATH = "C:/Capstone/Data/cleaned_data.csv"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(OUT_DIR, exist_ok=True)

# TF-IDF vectorizers factory
def make_tfidf(cfg):
    if cfg.get("char_ngrams"):
        from sklearn.feature_extraction.text import TfidfVectorizer as TV
        wu = FeatureUnion([
            ("word", TV(stop_words="english", ngram_range=cfg["word_ngram"],
                        max_features=cfg["max_features"], min_df=cfg["min_df"])),
            ("char", TV(analyzer="char_wb", ngram_range=cfg["char_ngram"],
                        max_features=cfg["char_max_features"], min_df=cfg["min_df"]))
        ])
        return wu
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer as TV
        return TV(stop_words="english", ngram_range=cfg["word_ngram"],
                  max_features=cfg["max_features"], min_df=cfg["min_df"])

# Experiment configs
tfidf_configs = [
    {"name":"word1-3_df3", "word_ngram":(1,3), "min_df":3, "max_features":15000, "char_ngrams":False},
    {"name":"word1-3_df5", "word_ngram":(1,3), "min_df":5, "max_features":15000, "char_ngrams":False},
    {"name":"word1-3_char3-5_df3", "word_ngram":(1,3), "min_df":3, "max_features":15000,
     "char_ngrams":True, "char_ngram":(3,5), "char_max_features":5000},
    {"name":"word1-3_char3-5_df5", "word_ngram":(1,3), "min_df":5, "max_features":15000,
     "char_ngrams":True, "char_ngram":(3,5), "char_max_features":5000}
]

models = [
    ("RandomForest", RandomForestClassifier(n_estimators=200, class_weight="balanced", n_jobs=-1, random_state=42)),
    ("XGBoost", XGBClassifier(use_label_encoder=False, eval_metric="mlogloss", random_state=42, verbosity=0))
]

def run_experiment(tf_cfg, model_name, model_obj):
    print(f"\n=== EXP: {tf_cfg['name']} {model_name} ===")
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["emergency_title","emergency_type"])
    X_train, X_test, y_train, y_test = train_test_split_by_title(df,
        text_col="emergency_title", label_col="emergency_type", test_size=0.2, random_state=42)

    vect = make_tfidf(tf_cfg)
    print("Fitting TF-IDF...")
    X_train_t = vect.fit_transform(X_train)
    X_test_t = vect.transform(X_test)

    # Encode labels if XGBoost
    if model_name == "XGBoost":
        le = LabelEncoder()
        y_train_enc = le.fit_transform(y_train)
        y_test_enc = le.transform(y_test)
    else:
        y_train_enc, y_test_enc = y_train, y_test

    t0 = time.time()
    model = model_obj
    model.fit(X_train_t, y_train_enc)
    train_time = time.time() - t0

    y_pred = model.predict(X_test_t)
    acc = accuracy_score(y_test_enc, y_pred)
    print(f"Acc: {acc:.4f} | Train time: {train_time:.1f}s")
    print("Classification report:")
    print(classification_report(y_test_enc, y_pred, digits=4))
    print("Confusion matrix:")
    print(confusion_matrix(y_test_enc, y_pred))

    # Save model + vectorizer
    name = f"{model_name}_{tf_cfg['name']}"
    joblib.dump({"model": model, "vect": vect, "label_encoder": le if model_name=="XGBoost" else None},
                os.path.join(OUT_DIR, f"{name}.pkl"))
    print("Saved:", name)

if __name__ == "__main__":
    for tf_cfg in tfidf_configs:
        for model_name, model_obj in models:
            try:
                run_experiment(tf_cfg, model_name, model_obj)
            except Exception as e:
                print("Error in run:", e)
