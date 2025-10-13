import pandas as pd
import random

# Natural language templates for each emergency type
# These convert dispatcher codes to conversational descriptions

EMS_TEMPLATES = {
    "CARDIAC EMERGENCY": [
        "patient experiencing severe chest pain",
        "man having heart attack symptoms",
        "woman with chest pressure and shortness of breath",
        "elderly person complaining of cardiac issues",
        "someone having chest pains and difficulty breathing"
    ],
    "FALL VICTIM": [
        "elderly woman fell down stairs",
        "person slipped and fell, injured",
        "someone tripped and can't get up",
        "fall victim with possible fracture",
        "patient fell and is in pain"
    ],
    "RESPIRATORY EMERGENCY": [
        "child having difficulty breathing",
        "patient wheezing and gasping for air",
        "someone experiencing breathing problems",
        "person with severe shortness of breath",
        "respiratory distress, can't breathe properly"
    ],
    "UNCONSCIOUS SUBJECT": [
        "unconscious person found in park",
        "someone passed out and not responding",
        "unresponsive individual needs help",
        "person collapsed and unconscious",
        "found someone not breathing properly"
    ],
    "SEIZURES": [
        "woman having seizure, body convulsing",
        "person experiencing epileptic seizure",
        "someone having convulsions",
        "patient seizing and shaking",
        "child having seizure episode"
    ],
    "DIABETIC EMERGENCY": [
        "diabetic patient with low blood sugar",
        "person showing signs of diabetic shock",
        "diabetic emergency, patient confused",
        "someone with diabetes complications",
        "hypoglycemic patient needs assistance"
    ],
    "ABDOMINAL PAINS": [
        "patient complaining of severe stomach pain",
        "person with intense abdominal cramps",
        "someone experiencing severe belly pain",
        "patient vomiting with stomach pain",
        "acute abdominal pain and nausea"
    ],
    "HEAD INJURY": [
        "head injury from sports accident",
        "person hit head, bleeding from forehead",
        "someone with head trauma",
        "patient injured head in fall",
        "bleeding head wound from accident"
    ],
    "OVERDOSE": [
        "overdose suspected, empty pill bottles found",
        "person took too many medications",
        "suspected drug overdose",
        "someone ingested pills, unresponsive",
        "possible overdose, patient lethargic"
    ],
    "CVA/STROKE": [
        "stroke symptoms, facial drooping",
        "person with slurred speech, possible stroke",
        "someone showing signs of stroke",
        "patient with one-sided weakness",
        "stroke emergency, face drooping"
    ],
    "VEHICLE ACCIDENT": [
        "person injured in car crash",
        "vehicle accident with injuries",
        "car collision, people hurt",
        "auto accident, need medical assistance",
        "injured in traffic accident"
    ],
    "SUBJECT IN PAIN": [
        "person in severe pain",
        "someone complaining of intense pain",
        "patient experiencing extreme discomfort",
        "individual in distress, lots of pain",
        "person needs pain management"
    ],
    "SYNCOPAL EPISODE": [
        "person fainted and fell",
        "someone passed out briefly",
        "patient experienced fainting spell",
        "individual lost consciousness momentarily",
        "person blacked out"
    ],
    "GENERAL WEAKNESS": [
        "elderly person feeling very weak",
        "patient experiencing general weakness",
        "someone too weak to stand",
        "person feeling faint and weak",
        "patient with extreme fatigue"
    ],
    "ALTERED MENTAL STATUS": [
        "person acting confused and disoriented",
        "patient with confusion and memory problems",
        "someone not making sense, confused",
        "altered consciousness, confused behavior",
        "person disoriented and confused"
    ],
    "MEDICAL ALERT ALARM": [
        "medical alert button pressed",
        "life alert activated",
        "emergency medical alarm triggered",
        "medical pendant alarm going off",
        "personal alarm system activated"
    ],
    "HEMORRHAGING": [
        "severe bleeding that won't stop",
        "person hemorrhaging, heavy blood loss",
        "uncontrolled bleeding injury",
        "someone bleeding profusely",
        "massive bleeding, needs immediate help"
    ],
    "NAUSEA/VOMITING": [
        "patient vomiting continuously",
        "severe nausea and throwing up",
        "person can't stop vomiting",
        "persistent vomiting and nausea",
        "someone very sick, vomiting"
    ],
    "LACERATIONS": [
        "deep cut that needs stitches",
        "person with large laceration",
        "severe cut, bleeding wound",
        "someone cut badly, needs treatment",
        "deep gash requiring medical attention"
    ],
    "FRACTURE": [
        "broken bone, possible fracture",
        "person with suspected fracture",
        "limb appears broken",
        "bone fracture from accident",
        "broken arm or leg"
    ],
    "MATERNITY": [
        "pregnant woman in labor",
        "woman about to give birth",
        "maternity emergency, baby coming",
        "pregnant patient having contractions",
        "childbirth imminent"
    ],
    "DIZZINESS": [
        "person experiencing severe dizziness",
        "patient feeling dizzy and lightheaded",
        "someone with vertigo symptoms",
        "extreme dizziness, can't stand",
        "person feeling faint and dizzy"
    ],
    "CHOKING": [
        "person choking on food",
        "someone can't breathe, choking",
        "choking victim needs help",
        "individual choking, airway blocked",
        "person gagging and choking"
    ],
    "DEHYDRATION": [
        "severe dehydration symptoms",
        "person extremely dehydrated",
        "patient needs fluids, dehydrated",
        "dehydration emergency",
        "someone severely dehydrated"
    ],
    "ALLERGIC REACTION": [
        "severe allergic reaction, swelling",
        "person having allergic reaction",
        "anaphylaxis symptoms present",
        "allergic response, difficulty breathing",
        "someone reacting to allergen"
    ],
    "BACK PAINS/INJURY": [
        "severe back pain, can't move",
        "person with back injury",
        "someone hurt their back",
        "back pain, needs medical attention",
        "patient with spinal pain"
    ],
    "FEVER": [
        "high fever, very hot",
        "person with dangerous fever",
        "child burning up with fever",
        "patient has high temperature",
        "severe fever symptoms"
    ],
    "CARDIAC ARREST": [
        "cardiac arrest, no pulse",
        "heart stopped, needs CPR",
        "person in cardiac arrest",
        "heart attack, not breathing",
        "someone collapsed, no heartbeat"
    ],
    "ASSAULT VICTIM": [
        "person assaulted, injured",
        "assault victim needs help",
        "someone attacked and hurt",
        "patient injured in assault",
        "victim of violent attack"
    ],
    "ANIMAL BITE": [
        "bitten by dog, needs treatment",
        "animal bite wound",
        "person bitten by animal",
        "dog attack victim",
        "someone bitten, bleeding"
    ],
    "UNRESPONSIVE SUBJECT": [
        "unresponsive person, not waking",
        "someone won't respond to voice",
        "person completely unresponsive",
        "individual not conscious",
        "found someone unresponsive"
    ],
    "EMS SPECIAL SERVICE": [
        "ems assistance needed",
        "special medical service required",
        "need paramedic support",
        "ems help requested",
        "medical service assistance"
    ],
    "UNKNOWN MEDICAL EMERGENCY": [
        "medical emergency, unsure what's wrong",
        "person needs help, unknown issue",
        "medical situation, unclear symptoms",
        "someone sick, not sure what",
        "unclear medical problem"
    ],
    "BUILDING FIRE": [
        "building on fire, smoke visible",
        "structure fire at residence",
        "house fire reported",
        "commercial building burning",
        "smoke coming from building"
    ]
}

FIRE_TEMPLATES = {
    "FIRE ALARM": [
        "fire alarm activated",
        "fire alarm going off",
        "smoke detector beeping",
        "fire alarm system triggered",
        "alarm sounding at building"
    ],
    "BUILDING FIRE": [
        "building on fire",
        "structure fire reported",
        "smoke coming out of house",
        "commercial building burning",
        "residential fire emergency"
    ],
    "VEHICLE FIRE": [
        "car on fire",
        "vehicle burning on roadside",
        "truck fire on highway",
        "automobile fire emergency",
        "vehicle engulfed in flames"
    ],
    "GAS-ODOR/LEAK": [
        "strong gas smell",
        "natural gas leak",
        "odor of gas in building",
        "gas leak at residence",
        "smell of gas, possible leak"
    ],
    "ELECTRICAL FIRE OUTSIDE": [
        "electrical wires sparking",
        "power lines on fire",
        "electrical fire on pole",
        "transformer sparking",
        "outdoor electrical fire"
    ],
    "CARBON MONOXIDE DETECTOR": [
        "carbon monoxide alarm sounding",
        "CO detector going off",
        "carbon monoxide warning",
        "CO alarm activated",
        "carbon monoxide detected"
    ],
    "TRASH/DUMPSTER FIRE": [
        "dumpster on fire",
        "trash fire behind building",
        "garbage bin burning",
        "dumpster fire at business",
        "refuse container fire"
    ],
    "APPLIANCE FIRE": [
        "kitchen appliance fire",
        "stove on fire",
        "oven fire in kitchen",
        "appliance caught fire",
        "kitchen fire from appliance"
    ],
    "WOODS/FIELD FIRE": [
        "woods fire spreading",
        "forest fire near homes",
        "field fire growing",
        "brush fire emergency",
        "wildfire approaching area"
    ],
    "UNKNOWN TYPE FIRE": [
        "fire of unknown origin",
        "some type of fire reported",
        "fire emergency, type unclear",
        "unidentified fire situation",
        "fire reported, nature unknown"
    ],
    "FIRE INVESTIGATION": [
        "suspicious fire needs investigation",
        "investigate possible fire",
        "fire inspection needed",
        "check for fire hazard",
        "fire safety check required"
    ],
    "FIRE SPECIAL SERVICE": [
        "fire department assistance needed",
        "fire service support required",
        "need fire department help",
        "fire crew requested",
        "fire department service call"
    ],
    "FIRE POLICE NEEDED": [
        "fire police required at scene",
        "need traffic control for fire",
        "fire police assistance",
        "traffic management for fire",
        "fire scene traffic control"
    ],
    "RESCUE - ELEVATOR": [
        "person stuck in elevator",
        "elevator rescue needed",
        "someone trapped in elevator",
        "elevator malfunction, person inside",
        "help person stuck in lift"
    ],
    "S/B AT HELICOPTER LANDING": [
        "helicopter landing assistance",
        "medevac helicopter arriving",
        "helicopter pad standby",
        "air ambulance landing",
        "helicopter emergency response"
    ],
    "VEHICLE LEAKING FUEL": [
        "vehicle leaking gasoline",
        "car leaking fuel",
        "fuel spill from vehicle",
        "gas leak from automobile",
        "vehicle fuel leak hazard"
    ]
}

TRAFFIC_TEMPLATES = {
    "VEHICLE ACCIDENT -": [
        "car accident at intersection",
        "two vehicle collision",
        "traffic accident with injuries",
        "auto crash on highway",
        "vehicle collision blocking road"
    ],
    "DISABLED VEHICLE -": [
        "car broken down on road",
        "vehicle stalled in lane",
        "disabled car blocking traffic",
        "broken down vehicle",
        "car won't start, blocking road"
    ],
    "ROAD OBSTRUCTION -": [
        "tree fallen across road",
        "debris blocking highway",
        "road blocked by obstacle",
        "large object in roadway",
        "obstruction blocking traffic"
    ],
    "HAZARDOUS ROAD CONDITIONS -": [
        "black ice on bridge",
        "hazardous icy conditions",
        "dangerous road conditions",
        "slippery road surface",
        "unsafe driving conditions"
    ],
    "VEHICLE FIRE -": [
        "vehicle on fire on expressway",
        "car fire on highway",
        "truck burning on road",
        "automobile fire blocking lane",
        "vehicle engulfed in flames"
    ],
    "VEHICLE LEAKING FUEL -": [
        "car leaking fuel after accident",
        "vehicle fuel spill on road",
        "gas leaking from car",
        "fuel leak from collision",
        "gasoline spill from vehicle"
    ]
}

print("="*70)
print("GENERATING NATURAL LANGUAGE AUGMENTATION DATASET")
print("="*70)

# Load original Montgomery data
print("\nLoading Montgomery dataset...")
df = pd.read_csv('C:/Capstone/Data/cleaned_data.csv')
print(f"Original dataset: {len(df):,} records")

# Create augmented dataset
augmented_records = []

print("\nGenerating natural language variations...")

# Process each row in Montgomery data
for idx, row in df.iterrows():
    emergency_type = row['emergency_type']
    emergency_subtype = row['emergency_subtype']
    
    # Select appropriate template dictionary
    if emergency_type == 'EMS':
        templates = EMS_TEMPLATES
    elif emergency_type == 'Fire':
        templates = FIRE_TEMPLATES
    elif emergency_type == 'Traffic':
        templates = TRAFFIC_TEMPLATES
    else:
        continue
    
    # If we have templates for this subtype, create variations
    if emergency_subtype in templates:
        # Pick 1 random variation for this record (to keep dataset manageable)
        natural_desc = random.choice(templates[emergency_subtype])
        
        # Create augmented record
        augmented_records.append({
            'emergency_title': natural_desc,
            'emergency_type': emergency_type,
            'emergency_subtype': emergency_subtype,
            'latitude': row.get('latitude'),
            'longitude': row.get('longitude'),
            'zipcode': row.get('zipcode'),
            'timestamp': row.get('timestamp'),
            'district': row.get('district')
        })
    
    if (idx + 1) % 10000 == 0:
        print(f"  Processed {idx + 1:,} records...")

# Create augmented dataframe
augmented_df = pd.DataFrame(augmented_records)

print(f"\n✅ Generated {len(augmented_df):,} natural language records")

# Combine original + augmented
combined_df = pd.concat([df, augmented_df], ignore_index=True)

print(f"\n📊 Combined Dataset Statistics:")
print(f"  Original records: {len(df):,}")
print(f"  Augmented records: {len(augmented_df):,}")
print(f"  Total records: {len(combined_df):,}")

print(f"\n  Emergency type distribution:")
for etype in ['EMS', 'Fire', 'Traffic']:
    count = len(combined_df[combined_df['emergency_type'] == etype])
    pct = (count / len(combined_df)) * 100
    print(f"    {etype}: {count:,} ({pct:.1f}%)")

# Save combined dataset
output_path = 'C:/Capstone/Data/montgomery_with_natural_language.csv'
combined_df.to_csv(output_path, index=False)

print(f"\n✅ Saved combined dataset to:")
print(f"   {output_path}")
print("\n" + "="*70)
print("AUGMENTATION COMPLETE")
print("="*70)
print("\nNext step: Retrain classifiers on combined dataset")