from classifier_enricher import classify_incident

test_samples = [
    "Smoke and fire in building",          # Expect: Fire
    "Gunshots heard in neighborhood",      # Expect: Police
    "Person having heart attack",           # Expect: Medical or EMS
    "Car accident on highway",              # Could be Traffic or Police
    "Child with fever and vomiting",        # Medical/EMS
    "Explosion reported at factory",        # Police or Fire
    "Person collapsed, needs ambulance",    # Medical/EMS
]

for desc in test_samples:
    classification = classify_incident(desc)
    print(f"Description: {desc}\nClassified as: {classification}\n")
