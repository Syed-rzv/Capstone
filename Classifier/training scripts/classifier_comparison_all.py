# classifier_comparison_all.py
import joblib

def load_models():
    """Load all trained models from disk."""
    return {
        "Naive Bayes": joblib.load("models/classifier_nb.pkl"),
        "Logistic Regression": joblib.load("models/classifier_lr.pkl"),
        "SVM": joblib.load("models/classifier_svm.pkl"),
        "Decision Tree": joblib.load("models/classifier_dt.pkl")
    }

def compare_models():
    models = load_models()
    test_cases = [
    "Car flipped over on highway, fuel leaking everywhere",
    "Elderly person fainted while shopping at the mall",
    "Kitchen fire spreading quickly through the house",
    "Motorcycle crash with rider unconscious",
    "Explosion reported in apartment basement",
    "Person trapped in elevator, difficulty breathing",
    "Gas leak smell reported in residential building",
    "Massive pileup on the freeway with injuries",
    "Man having severe chest pain at the park",
    "Smoke seen coming from warehouse roof"
]

    print("MODEL COMPARISON RESULTS WITH CONFIDENCE")
    print("=" * 100)
    print(f"{'Test Case':<50} | {'Model':<20} | {'Prediction':<10} | {'Confidence'}")
    print("-" * 100)

    for case in test_cases:
        for name, model in models.items():
            pred = model.predict([case])[0]
            try:
                proba = max(model.predict_proba([case])[0])
            except AttributeError:
                # Some models like Decision Tree may not have predict_proba if trained otherwise
                proba = "N/A"
            print(f"{case[:49]:<50} | {name:<20} | {pred:<10} | {proba}")
        print("-" * 100)

if __name__ == "__main__":
    compare_models()
