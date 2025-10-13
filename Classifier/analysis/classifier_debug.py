import joblib
import argparse

# -------------------- ARG PARSER --------------------
parser = argparse.ArgumentParser(description="Debug classifier predictions")
parser.add_argument('--model', type=str, default="models/classifier.pkl",
                    help="Path to the trained model .pkl file")
args = parser.parse_args()

# Load the model
model = joblib.load(args.model)

# -------------------- FUNCTION --------------------
def analyze_prediction(text):
    probabilities = model.predict_proba([text])[0]
    classes = model.classes_
    print(f"\nText: '{text}'")
    print("Prediction probabilities:")
    for class_name, prob in zip(classes, probabilities):
        print(f"  {class_name}: {prob:.3f}")
    print(f"Final prediction: {model.predict([text])[0]}")

# -------------------- TEST CASES --------------------
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

if __name__ == "__main__":
    for case in test_cases:
        analyze_prediction(case)
