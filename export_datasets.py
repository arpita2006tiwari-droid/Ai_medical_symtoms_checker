import os
import sys
import shutil
import json
import csv
import pandas as pd
import joblib

# Add backend to path to import ontology
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from app.services.symptom_ontology import SYMPTOM_ONTOLOGY

output_dir = "PROJECT_DATA_DOCUMENTATION"
base_dir = os.path.dirname(__file__)

def validate_csv(source_path, dest_path):
    df_src = pd.read_csv(source_path)
    df_dst = pd.read_csv(dest_path)
    assert df_src.shape == df_dst.shape, f"Shape mismatch: {df_src.shape} vs {df_dst.shape}"
    assert list(df_src.columns) == list(df_dst.columns), "Columns mismatch"
    return df_src.shape

# 1. Copy original datasets
src_dataset = os.path.join(base_dir, "ml/data/raw/dataset.csv")
dst_dataset = os.path.join(output_dir, "01_Original_Kaggle_Dataset.csv")
shutil.copy2(src_dataset, dst_dataset)
s1 = validate_csv(src_dataset, dst_dataset)
print(f"Verified 01_Original_Kaggle_Dataset.csv: {s1}")

src_processed = os.path.join(base_dir, "ml/data/processed/processed_symptom_dataset.csv")
dst_processed = os.path.join(output_dir, "02_Processed_Training_Dataset.csv")
shutil.copy2(src_processed, dst_processed)
s2 = validate_csv(src_processed, dst_processed)
print(f"Verified 02_Processed_Training_Dataset.csv: {s2}")

src_desc = os.path.join(base_dir, "ml/data/raw/symptom_Description.csv")
dst_desc = os.path.join(output_dir, "07_Kaggle_Symptom_Descriptions.csv")
shutil.copy2(src_desc, dst_desc)
s3 = validate_csv(src_desc, dst_desc)
print(f"Verified 07_Kaggle_Symptom_Descriptions.csv: {s3}")

src_sev = os.path.join(base_dir, "ml/data/raw/Symptom-severity.csv")
dst_sev = os.path.join(output_dir, "08_Kaggle_Symptom_Severities.csv")
shutil.copy2(src_sev, dst_sev)
s4 = validate_csv(src_sev, dst_sev)
print(f"Verified 08_Kaggle_Symptom_Severities.csv: {s4}")

src_prec = os.path.join(base_dir, "ml/data/raw/symptom_precaution.csv")
dst_prec = os.path.join(output_dir, "09_Kaggle_Symptom_Precautions.csv")
shutil.copy2(src_prec, dst_prec)
s5 = validate_csv(src_prec, dst_prec)
print(f"Verified 09_Kaggle_Symptom_Precautions.csv: {s5}")


# 3. Export Vocabulary
vocab_path = os.path.join(base_dir, "ml/artifacts/symptom_vocabulary.json")
dst_vocab = os.path.join(output_dir, "03_Symptom_Vocabulary.csv")
with open(vocab_path, "r", encoding="utf-8") as f:
    vocab_data = json.load(f)["symptoms"]

with open(dst_vocab, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Index", "Symptom_Name"])
    for i, sym in enumerate(vocab_data):
        writer.writerow([i, sym])
print(f"Exported 03_Symptom_Vocabulary.csv: ({len(vocab_data)}, 2)")

# 4. Export Ontology
dst_ont = os.path.join(output_dir, "04_Symptom_Ontology.csv")
with open(dst_ont, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Canonical_Symptom", "Category", "Synonyms", "Source"])
    count = 0
    for canonical, details in SYMPTOM_ONTOLOGY.items():
        synonyms = ", ".join(details.get("synonyms", []))
        category = details.get("category", "")
        source = details.get("source", "")
        writer.writerow([canonical, category, synonyms, source])
        count += 1
print(f"Exported 04_Symptom_Ontology.csv: ({count}, 4)")

# 5. Extract Model Features & Classes
model_path = os.path.join(base_dir, "ml/models/symptom_random_forest.joblib")
rf_model = joblib.load(model_path)

dst_features = os.path.join(output_dir, "05_Model_Feature_Names.csv")
try:
    features = list(rf_model.feature_names_in_)
    with open(dst_features, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Feature_Index", "Feature_Name"])
        for i, feat in enumerate(features):
            writer.writerow([i, feat])
    print(f"Exported 05_Model_Feature_Names.csv: ({len(features)}, 2)")
except Exception as e:
    print(f"Could not extract feature names: {e}")

dst_classes = os.path.join(output_dir, "06_Model_Disease_Classes.csv")
try:
    classes = list(rf_model.classes_)
    with open(dst_classes, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Class_Index", "Disease_Class"])
        for i, cls in enumerate(classes):
            writer.writerow([i, cls])
    print(f"Exported 06_Model_Disease_Classes.csv: ({len(classes)}, 2)")
except Exception as e:
    print(f"Could not extract classes: {e}")

print("Validation completed successfully.")
