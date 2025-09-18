# Emergency Classification Model Experiments

## Experiment 1: Baseline (Naive Bayes)
- **Algorithm:** Naive Bayes + TF-IDF
- **Result:** 90% accuracy
- **Problem Discovered:** Model predicting EMS for everything (class imbalance bias)
- **Evidence:** Debug showed identical probabilities for different emergencies

## Experiment 2: Improved Model (Logistic Regression)
- **Algorithm:** Logistic Regression + class_weight='balanced' + bigrams
- **Reasoning:** Better handling of imbalanced data and overlapping features
- **Result:** [You'll fill this in after training]
- **Improvement:** [Compare confusion matrices]