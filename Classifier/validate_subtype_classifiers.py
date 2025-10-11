import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import os

# Create output directory
os.makedirs('validation_results', exist_ok=True)

print("="*70)
print("SUBTYPE CLASSIFIER VALIDATION")
print("5-Fold Cross-Validation + Confusion Matrices")
print("="*70)

# Load Montgomery data
print("\nLoading Montgomery dataset...")
df = pd.read_csv('C:/Capstone/Data/cleaned_data.csv')
df = df.dropna(subset=['emergency_title', 'emergency_type', 'emergency_subtype'])
print(f"Total records: {len(df):,}")

# ============================================================================
# 1. EMS SUBTYPE VALIDATION
# ============================================================================

print("\n" + "="*70)
print("1. EMS SUBTYPE CLASSIFIER VALIDATION")
print("="*70)

# Filter EMS calls
ems_df = df[df['emergency_type'] == 'EMS'].copy()
subtype_counts = ems_df['emergency_subtype'].value_counts()
valid_subtypes = subtype_counts[subtype_counts >= 100].index
ems_df = ems_df[ems_df['emergency_subtype'].isin(valid_subtypes)]

print(f"\nEMS calls for validation: {len(ems_df):,}")
print(f"Number of classes: {ems_df['emergency_subtype'].nunique()}")

# Prepare data
X_ems = ems_df['emergency_title']
y_ems = ems_df['emergency_subtype']

# Vectorize
vectorizer_ems = TfidfVectorizer(min_df=5, max_features=15000, ngram_range=(1, 3))
X_ems_vec = vectorizer_ems.fit_transform(X_ems)

# Encode labels
le_ems = LabelEncoder()
y_ems_enc = le_ems.fit_transform(y_ems)

# 5-Fold Cross-Validation
print("\nRunning 5-fold cross-validation...")
model_ems = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model_ems, X_ems_vec, y_ems_enc, cv=cv, scoring='accuracy')

print(f"\nCross-Validation Results:")
print(f"  Fold 1: {cv_scores[0]:.4f}")
print(f"  Fold 2: {cv_scores[1]:.4f}")
print(f"  Fold 3: {cv_scores[2]:.4f}")
print(f"  Fold 4: {cv_scores[3]:.4f}")
print(f"  Fold 5: {cv_scores[4]:.4f}")
print(f"  Mean Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Generate confusion matrix
print("\nGenerating confusion matrix...")
X_train, X_test, y_train, y_test = train_test_split(
    X_ems_vec, y_ems_enc, test_size=0.2, random_state=42, stratify=y_ems_enc
)

model_ems.fit(X_train, y_train)
y_pred = model_ems.predict(X_test)

cm = confusion_matrix(y_test, y_pred)

# Plot confusion matrix (simplified view - top 15 classes only for readability)
plt.figure(figsize=(16, 14))
top_15_classes = np.argsort(subtype_counts.values)[-15:][::-1]
top_15_labels = [le_ems.classes_[i] for i in top_15_classes if i < len(le_ems.classes_)]

# Filter confusion matrix for top 15 classes
cm_subset = cm[top_15_classes][:, top_15_classes]

sns.heatmap(cm_subset, annot=True, fmt='d', cmap='Blues', 
            xticklabels=top_15_labels, yticklabels=top_15_labels,
            cbar_kws={'label': 'Count'})
plt.title('EMS Subtype Confusion Matrix (Top 15 Classes)', fontsize=16, pad=20)
plt.xlabel('Predicted Subtype', fontsize=12)
plt.ylabel('True Subtype', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('validation_results/ems_confusion_matrix.png', dpi=300, bbox_inches='tight')
print("✅ Saved: validation_results/ems_confusion_matrix.png")
plt.close()

# ============================================================================
# 2. FIRE SUBTYPE VALIDATION
# ============================================================================

print("\n" + "="*70)
print("2. FIRE SUBTYPE CLASSIFIER VALIDATION")
print("="*70)

# Filter Fire calls
fire_df = df[df['emergency_type'] == 'Fire'].copy()
subtype_counts = fire_df['emergency_subtype'].value_counts()
valid_subtypes = subtype_counts[subtype_counts >= 100].index
fire_df = fire_df[fire_df['emergency_subtype'].isin(valid_subtypes)]

print(f"\nFire calls for validation: {len(fire_df):,}")
print(f"Number of classes: {fire_df['emergency_subtype'].nunique()}")

# Prepare data
X_fire = fire_df['emergency_title']
y_fire = fire_df['emergency_subtype']

# Vectorize
vectorizer_fire = TfidfVectorizer(min_df=5, max_features=15000, ngram_range=(1, 3))
X_fire_vec = vectorizer_fire.fit_transform(X_fire)

# Encode labels
le_fire = LabelEncoder()
y_fire_enc = le_fire.fit_transform(y_fire)

# 5-Fold Cross-Validation
print("\nRunning 5-fold cross-validation...")
model_fire = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)

cv_scores = cross_val_score(model_fire, X_fire_vec, y_fire_enc, cv=cv, scoring='accuracy')

print(f"\nCross-Validation Results:")
print(f"  Fold 1: {cv_scores[0]:.4f}")
print(f"  Fold 2: {cv_scores[1]:.4f}")
print(f"  Fold 3: {cv_scores[2]:.4f}")
print(f"  Fold 4: {cv_scores[3]:.4f}")
print(f"  Fold 5: {cv_scores[4]:.4f}")
print(f"  Mean Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Generate confusion matrix
print("\nGenerating confusion matrix...")
X_train, X_test, y_train, y_test = train_test_split(
    X_fire_vec, y_fire_enc, test_size=0.2, random_state=42, stratify=y_fire_enc
)

model_fire.fit(X_train, y_train)
y_pred = model_fire.predict(X_test)

cm = confusion_matrix(y_test, y_pred)

# Plot confusion matrix (all 18 classes)
plt.figure(figsize=(14, 12))
sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges',
            xticklabels=le_fire.classes_, yticklabels=le_fire.classes_,
            cbar_kws={'label': 'Count'})
plt.title('Fire Subtype Confusion Matrix (All 18 Classes)', fontsize=16, pad=20)
plt.xlabel('Predicted Subtype', fontsize=12)
plt.ylabel('True Subtype', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('validation_results/fire_confusion_matrix.png', dpi=300, bbox_inches='tight')
print("✅ Saved: validation_results/fire_confusion_matrix.png")
plt.close()

# ============================================================================
# 3. TRAFFIC SUBTYPE VALIDATION
# ============================================================================

print("\n" + "="*70)
print("3. TRAFFIC SUBTYPE CLASSIFIER VALIDATION")
print("="*70)

# Filter Traffic calls
traffic_df = df[df['emergency_type'] == 'Traffic'].copy()
subtype_counts = traffic_df['emergency_subtype'].value_counts()
valid_subtypes = subtype_counts[subtype_counts >= 100].index
traffic_df = traffic_df[traffic_df['emergency_subtype'].isin(valid_subtypes)]

print(f"\nTraffic calls for validation: {len(traffic_df):,}")
print(f"Number of classes: {traffic_df['emergency_subtype'].nunique()}")

# Prepare data
X_traffic = traffic_df['emergency_title']
y_traffic = traffic_df['emergency_subtype']

# Vectorize
vectorizer_traffic = TfidfVectorizer(min_df=5, max_features=15000, ngram_range=(1, 3))
X_traffic_vec = vectorizer_traffic.fit_transform(X_traffic)

# Encode labels
le_traffic = LabelEncoder()
y_traffic_enc = le_traffic.fit_transform(y_traffic)

# 5-Fold Cross-Validation
print("\nRunning 5-fold cross-validation...")
model_traffic = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)

cv_scores = cross_val_score(model_traffic, X_traffic_vec, y_traffic_enc, cv=cv, scoring='accuracy')

print(f"\nCross-Validation Results:")
print(f"  Fold 1: {cv_scores[0]:.4f}")
print(f"  Fold 2: {cv_scores[1]:.4f}")
print(f"  Fold 3: {cv_scores[2]:.4f}")
print(f"  Fold 4: {cv_scores[3]:.4f}")
print(f"  Fold 5: {cv_scores[4]:.4f}")
print(f"  Mean Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Generate confusion matrix
print("\nGenerating confusion matrix...")
X_train, X_test, y_train, y_test = train_test_split(
    X_traffic_vec, y_traffic_enc, test_size=0.2, random_state=42, stratify=y_traffic_enc
)

model_traffic.fit(X_train, y_train)
y_pred = model_traffic.predict(X_test)

cm = confusion_matrix(y_test, y_pred)

# Plot confusion matrix (all 6 classes)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=le_traffic.classes_, yticklabels=le_traffic.classes_,
            cbar_kws={'label': 'Count'})
plt.title('Traffic Subtype Confusion Matrix (All 6 Classes)', fontsize=16, pad=20)
plt.xlabel('Predicted Subtype', fontsize=12)
plt.ylabel('True Subtype', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('validation_results/traffic_confusion_matrix.png', dpi=300, bbox_inches='tight')
print("✅ Saved: validation_results/traffic_confusion_matrix.png")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("VALIDATION COMPLETE")
print("="*70)
print("\n✅ All validations completed successfully!")
print("\nGenerated files in validation_results/:")
print("   - ems_confusion_matrix.png")
print("   - fire_confusion_matrix.png")
print("   - traffic_confusion_matrix.png")
print("="*70)