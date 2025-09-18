# classifier/classifier_tester.py
from classifier_service import classify_incident

# Updated samples that match our EMS/Traffic/Fire dispatch system
samples = [
    "Vehicle fire on highway with flames",           # Should be Traffic (vehicle fire)
    "Building fire with smoke and flames",           # Should be Fire (structural fire)
    "Chest pain and difficulty breathing",           # Should be EMS
    "Multi-car accident with injuries",              # Could be Traffic or EMS
    "Car leaking fuel on interstate",                # Should be Traffic
    "Heart attack victim unconscious",               # Should be EMS
    "House fire spreading to neighbors",             # Should be Fire
    "Disabled vehicle blocking traffic lanes",       # Should be Traffic
    "Apartment building fire, residents evacuating", # Should be Fire
    "Overdose patient needs immediate attention"     # Should be EMS
]

print("Testing classifier with appropriate examples for EMS/Traffic/Fire dispatch:")
print("=" * 70)

for s in samples:
    result = classify_incident(s)
    print(f"{s:<50} -> {result}")