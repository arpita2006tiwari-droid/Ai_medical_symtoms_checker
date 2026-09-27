# Model Card: AI Medical Symptom Checker (v0.1.0)

## Intended Use
This machine learning model is intended for **academic research and educational demonstration only**. It evaluates natural language symptom descriptions and outputs a ranked list of associated conditions based on synthetic statistical associations.

## Prohibited Use
**DO NOT** use this model as a clinically validated diagnostic device. It is strictly prohibited to rely on this model's outputs for medical triage, treatment, diagnosis, or emergency decision-making. 

## Dataset and Population
- **Source:** Kaggle "Disease Symptom Prediction Dataset" (Likely derived from Columbia University DBMI 2004 NLP extractions).
- **Population:** Highly synthetic, perfectly balanced distributions (exactly 120 records per disease). 
- **Records:** 4,920 records.
- **Features:** 131 binary symptom features.
- **Classes:** 41 disease labels.

## Model Details
- **Algorithm:** Random Forest Classifier.
- **Version:** `0.1.0` (Phase 7 - Ontology Expansion)
- **Artifact:** `ml/models/symptom_random_forest.joblib`

## Performance
- **Metrics:** Achieves near-perfect accuracy (>98%) on its own synthetic test split.
- **Warning:** This performance is a statistical artifact of the synthetic, over-balanced dataset and **does not** reflect real-world clinical accuracy.

## Limitations
- Model cannot generalize to symptoms outside its rigid 131-feature vocabulary. (Newly added ontology terms are flagged as unsupported in the UI).
- Probabilities output by the model are statistical confidences of the Random Forest tree votes, not actual epidemiological probabilities of disease.
- The model is agnostic to patient age, gender, medical history, and geographic location.
