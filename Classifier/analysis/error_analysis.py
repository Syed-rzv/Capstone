import joblib

model_bundle = joblib.load('models/XGBoost_A_word1-3.pkl')
le = model_bundle.get('label_encoder')

if le:
    print("Label mapping:")
    for i, label in enumerate(le.classes_):
        print(f"{i} -> {label}")
else:
    print("No label encoder found")