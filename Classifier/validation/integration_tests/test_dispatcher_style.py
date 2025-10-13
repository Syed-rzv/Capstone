import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Classifier.classifier_service import classify_call, classify_subtype

# Test cases using MONTGOMERY-STYLE dispatcher vocabulary
dispatcher_tests = [
    # EMS Cases
    {"description": "EMS - CARDIAC EMERGENCY", "expected_type": "EMS", "expected_subtype": "CARDIAC EMERGENCY"},
    {"description": "EMS - FALL VICTIM", "expected_type": "EMS", "expected_subtype": "FALL VICTIM"},
    {"description": "EMS - RESPIRATORY EMERGENCY", "expected_type": "EMS", "expected_subtype": "RESPIRATORY EMERGENCY"},
    {"description": "EMS - UNCONSCIOUS SUBJECT", "expected_type": "EMS", "expected_subtype": "UNCONSCIOUS SUBJECT"},
    {"description": "EMS - SEIZURES", "expected_type": "EMS", "expected_subtype": "SEIZURES"},
    {"description": "EMS - DIABETIC EMERGENCY", "expected_type": "EMS", "expected_subtype": "DIABETIC EMERGENCY"},
    {"description": "EMS - ABDOMINAL PAINS", "expected_type": "EMS", "expected_subtype": "ABDOMINAL PAINS"},
    {"description": "EMS - HEAD INJURY", "expected_type": "EMS", "expected_subtype": "HEAD INJURY"},
    {"description": "EMS - OVERDOSE", "expected_type": "EMS", "expected_subtype": "OVERDOSE"},
    {"description": "EMS - CVA/STROKE", "expected_type": "EMS", "expected_subtype": "CVA/STROKE"},
    
    # Fire Cases
    {"description": "FIRE - BUILDING FIRE", "expected_type": "Fire", "expected_subtype": "BUILDING FIRE"},
    {"description": "FIRE - FIRE ALARM", "expected_type": "Fire", "expected_subtype": "FIRE ALARM"},
    {"description": "FIRE - VEHICLE FIRE", "expected_type": "Fire", "expected_subtype": "VEHICLE FIRE"},
    {"description": "FIRE - GAS-ODOR/LEAK", "expected_type": "Fire", "expected_subtype": "GAS-ODOR/LEAK"},
    {"description": "FIRE - ELECTRICAL FIRE OUTSIDE", "expected_type": "Fire", "expected_subtype": "ELECTRICAL FIRE OUTSIDE"},
    {"description": "FIRE - CARBON MONOXIDE DETECTOR", "expected_type": "Fire", "expected_subtype": "CARBON MONOXIDE DETECTOR"},
    {"description": "FIRE - TRASH/DUMPSTER FIRE", "expected_type": "Fire", "expected_subtype": "TRASH/DUMPSTER FIRE"},
    {"description": "FIRE - APPLIANCE FIRE", "expected_type": "Fire", "expected_subtype": "APPLIANCE FIRE"},
    {"description": "FIRE - WOODS/FIELD FIRE", "expected_type": "Fire", "expected_subtype": "WOODS/FIELD FIRE"},
    {"description": "FIRE - UNKNOWN TYPE FIRE", "expected_type": "Fire", "expected_subtype": "UNKNOWN TYPE FIRE"},
    
    # Traffic Cases
    {"description": "TRAFFIC - VEHICLE ACCIDENT", "expected_type": "Traffic", "expected_subtype": "VEHICLE ACCIDENT -"},
    {"description": "TRAFFIC - DISABLED VEHICLE", "expected_type": "Traffic", "expected_subtype": "DISABLED VEHICLE -"},
    {"description": "TRAFFIC - ROAD OBSTRUCTION", "expected_type": "Traffic", "expected_subtype": "ROAD OBSTRUCTION -"},
    {"description": "TRAFFIC - HAZARDOUS ROAD CONDITIONS", "expected_type": "Traffic", "expected_subtype": "HAZARDOUS ROAD CONDITIONS -"},
    {"description": "TRAFFIC - VEHICLE FIRE", "expected_type": "Traffic", "expected_subtype": "VEHICLE FIRE -"},
    {"description": "TRAFFIC - VEHICLE LEAKING FUEL", "expected_type": "Traffic", "expected_subtype": "VEHICLE LEAKING FUEL -"},
]

print("="*80)
print("DISPATCHER-STYLE VOCABULARY TEST")
print("Testing model with Montgomery County dispatcher format")
print("="*80)

correct_main = 0
correct_subtype = 0
total = len(dispatcher_tests)

for i, test in enumerate(dispatcher_tests, 1):
    description = test["description"]
    expected_type = test["expected_type"]
    expected_subtype = test["expected_subtype"]
    
    predicted_type = classify_call(description)
    predicted_subtype = classify_subtype(description, predicted_type)
    
    main_match = predicted_type == expected_type
    subtype_match = predicted_subtype == expected_subtype
    
    if main_match:
        correct_main += 1
    if main_match and subtype_match:
        correct_subtype += 1
    
    status_main = "✅" if main_match else "❌"
    status_subtype = "✅" if subtype_match else "❌"
    
    print(f"\n{i}/{total}: {description}")
    print(f"  {status_main} Main: {predicted_type} (Expected: {expected_type})")
    print(f"  {status_subtype} Subtype: {predicted_subtype} (Expected: {expected_subtype})")

print("\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"Main Type Accuracy: {correct_main}/{total} ({correct_main/total*100:.1f}%)")
print(f"Subtype Accuracy: {correct_subtype}/{total} ({correct_subtype/total*100:.1f}%)")
print("="*80)