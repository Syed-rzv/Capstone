# classifier_service.py
import joblib
import os

# Choose which model to load
# Options: "nb", "lr", "svm", "dt"
MODEL_TYPE = "lr"  

MODEL_PATHS = {
    "nb": "models/classifier_nb.pkl",
    "lr": "models/classifier_lr.pkl",
    "svm": "models/classifier_svm.pkl",
    "dt": "models/classifier_dt.pkl"
}

if MODEL_TYPE not in MODEL_PATHS:
    raise ValueError(f"Unknown MODEL_TYPE '{MODEL_TYPE}'. Choose from: {list(MODEL_PATHS.keys())}")

MODEL_PATH = MODEL_PATHS[MODEL_TYPE]

# Load model once
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Model not trained yet at {MODEL_PATH}. Run the appropriate training script first.")
model = joblib.load(MODEL_PATH)

def classify_incident(description: str) -> str:
    """Classify incident description into Fire/EMS/Traffic"""
    return model.predict([description])[0]

if __name__ == "__main__":
    # Quick demo
    samples = [
        "House on fire with smoke",
        "Person injured in car accident",
        "Suspicious person breaking into home"
    ]
    for s in samples:
        print(s, "->", classify_incident(s))
