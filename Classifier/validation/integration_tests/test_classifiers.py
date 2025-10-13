import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Classifier.classifier_service import classify_call, classify_subtype

# Test cases organized by emergency type
test_cases = {
    "EMS": [
        {
            "description": "Male patient experiencing severe chest pain and shortness of breath",
            "expected_type": "EMS",
            "expected_subtype": "CARDIAC EMERGENCY"
        },
        {
            "description": "Elderly woman fell down stairs, possible hip fracture",
            "expected_type": "EMS",
            "expected_subtype": "FALL VICTIM"
        },
        {
            "description": "Child having difficulty breathing, wheezing sounds",
            "expected_type": "EMS",
            "expected_subtype": "RESPIRATORY EMERGENCY"
        },
        {
            "description": "Unconscious man found in park, not responding to voice",
            "expected_type": "EMS",
            "expected_subtype": "UNCONSCIOUS SUBJECT"
        },
        {
            "description": "Woman having seizure, body convulsing",
            "expected_type": "EMS",
            "expected_subtype": "SEIZURES"
        },
        {
            "description": "Diabetic emergency, patient showing signs of low blood sugar",
            "expected_type": "EMS",
            "expected_subtype": "DIABETIC EMERGENCY"
        },
        {
            "description": "Patient complaining of severe abdominal pain and vomiting",
            "expected_type": "EMS",
            "expected_subtype": "ABDOMINAL PAINS"
        },
        {
            "description": "Head injury from sports accident, bleeding from forehead",
            "expected_type": "EMS",
            "expected_subtype": "HEAD INJURY"
        },
        {
            "description": "Overdose suspected, empty pill bottles found",
            "expected_type": "EMS",
            "expected_subtype": "OVERDOSE"
        },
        {
            "description": "Stroke symptoms, facial drooping and slurred speech",
            "expected_type": "EMS",
            "expected_subtype": "CVA/STROKE"
        }
    ],
    "Fire": [
        {
            "description": "Smoke coming out of school building",
            "expected_type": "Fire",
            "expected_subtype": "BUILDING FIRE"
        },
        {
            "description": "Fire alarm activated at residential address",
            "expected_type": "Fire",
            "expected_subtype": "FIRE ALARM"
        },
        {
            "description": "Car on fire on highway shoulder",
            "expected_type": "Fire",
            "expected_subtype": "VEHICLE FIRE"
        },
        {
            "description": "Strong gas smell inside apartment",
            "expected_type": "Fire",
            "expected_subtype": "GAS-ODOR/LEAK"
        },
        {
            "description": "Electrical wires sparking outside house",
            "expected_type": "Fire",
            "expected_subtype": "ELECTRICAL FIRE OUTSIDE"
        },
        {
            "description": "Carbon monoxide detector going off",
            "expected_type": "Fire",
            "expected_subtype": "CARBON MONOXIDE DETECTOR"
        },
        {
            "description": "Trash dumpster on fire behind shopping center",
            "expected_type": "Fire",
            "expected_subtype": "TRASH/DUMPSTER FIRE"
        },
        {
            "description": "Kitchen appliance fire, smoke in kitchen",
            "expected_type": "Fire",
            "expected_subtype": "APPLIANCE FIRE"
        },
        {
            "description": "Woods fire spreading near residential area",
            "expected_type": "Fire",
            "expected_subtype": "WOODS/FIELD FIRE"
        },
        {
            "description": "Unknown type of fire reported in basement",
            "expected_type": "Fire",
            "expected_subtype": "UNKNOWN TYPE FIRE"
        }
    ],
    "Traffic": [
        {
            "description": "Two vehicle collision at intersection",
            "expected_type": "Traffic",
            "expected_subtype": "VEHICLE ACCIDENT -"
        },
        {
            "description": "Car broken down blocking right lane",
            "expected_type": "Traffic",
            "expected_subtype": "DISABLED VEHICLE -"
        },
        {
            "description": "Large tree fallen across roadway",
            "expected_type": "Traffic",
            "expected_subtype": "ROAD OBSTRUCTION -"
        },
        {
            "description": "Black ice on bridge causing hazardous conditions",
            "expected_type": "Traffic",
            "expected_subtype": "HAZARDOUS ROAD CONDITIONS -"
        },
        {
            "description": "Vehicle fire on expressway",
            "expected_type": "Traffic",
            "expected_subtype": "VEHICLE FIRE -"
        },
        {
            "description": "Car leaking fuel after minor accident",
            "expected_type": "Traffic",
            "expected_subtype": "VEHICLE LEAKING FUEL -"
        }
    ]
}

def run_tests():
    """Run all test cases and generate report."""
    
    print("="*80)
    print("EMERGENCY CLASSIFIER TESTING SUITE")
    print("="*80)
    print(f"\nTotal test cases: {sum(len(cases) for cases in test_cases.values())}")
    print()
    
    # Track results
    results = {
        "total": 0,
        "main_correct": 0,
        "main_incorrect": 0,
        "subtype_correct": 0,
        "subtype_incorrect": 0,
        "failures": []
    }
    
    # Test each category
    for category, cases in test_cases.items():
        print("="*80)
        print(f"{category.upper()} TESTS ({len(cases)} cases)")
        print("="*80)
        
        for i, test in enumerate(cases, 1):
            results["total"] += 1
            description = test["description"]
            expected_type = test["expected_type"]
            expected_subtype = test["expected_subtype"]
            
            print(f"\nTest {i}/{len(cases)}: {description[:60]}...")
            
            try:
                # Classify main type
                predicted_type = classify_call(description)
                
                # Classify subtype
                predicted_subtype = classify_subtype(description, predicted_type)
                
                # Check main type
                main_correct = predicted_type == expected_type
                if main_correct:
                    results["main_correct"] += 1
                    print(f"  ✅ Main Type: {predicted_type}")
                else:
                    results["main_incorrect"] += 1
                    print(f"  ❌ Main Type: {predicted_type} (Expected: {expected_type})")
                
                # Check subtype (only if main type is correct)
                if main_correct:
                    subtype_correct = predicted_subtype == expected_subtype
                    if subtype_correct:
                        results["subtype_correct"] += 1
                        print(f"  ✅ Subtype: {predicted_subtype}")
                    else:
                        results["subtype_incorrect"] += 1
                        print(f"  ❌ Subtype: {predicted_subtype} (Expected: {expected_subtype})")
                        results["failures"].append({
                            "description": description,
                            "expected_type": expected_type,
                            "predicted_type": predicted_type,
                            "expected_subtype": expected_subtype,
                            "predicted_subtype": predicted_subtype
                        })
                else:
                    # If main type is wrong, subtype is automatically wrong
                    results["subtype_incorrect"] += 1
                    print(f"  ⚠️  Subtype: {predicted_subtype} (Skipped - main type wrong)")
                    results["failures"].append({
                        "description": description,
                        "expected_type": expected_type,
                        "predicted_type": predicted_type,
                        "expected_subtype": expected_subtype,
                        "predicted_subtype": predicted_subtype
                    })
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                results["failures"].append({
                    "description": description,
                    "expected_type": expected_type,
                    "predicted_type": "ERROR",
                    "expected_subtype": expected_subtype,
                    "predicted_subtype": str(e)
                })
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    main_accuracy = (results["main_correct"] / results["total"]) * 100
    subtype_accuracy = (results["subtype_correct"] / results["total"]) * 100
    
    print(f"\nTotal Tests: {results['total']}")
    print(f"\nMain Type Classification:")
    print(f"  ✅ Correct: {results['main_correct']}/{results['total']} ({main_accuracy:.1f}%)")
    print(f"  ❌ Incorrect: {results['main_incorrect']}/{results['total']} ({100-main_accuracy:.1f}%)")
    
    print(f"\nSubtype Classification:")
    print(f"  ✅ Correct: {results['subtype_correct']}/{results['total']} ({subtype_accuracy:.1f}%)")
    print(f"  ❌ Incorrect: {results['subtype_incorrect']}/{results['total']} ({100-subtype_accuracy:.1f}%)")
    
    # Print failures
    if results["failures"]:
        print("\n" + "="*80)
        print(f"FAILED CASES ({len(results['failures'])})")
        print("="*80)
        
        for i, failure in enumerate(results["failures"], 1):
            print(f"\n{i}. Description: {failure['description']}")
            print(f"   Expected: {failure['expected_type']} → {failure['expected_subtype']}")
            print(f"   Predicted: {failure['predicted_type']} → {failure['predicted_subtype']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    
    # Return results for further analysis
    return results


if __name__ == "__main__":
    results = run_tests()