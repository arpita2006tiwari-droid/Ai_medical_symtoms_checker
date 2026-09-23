# AI Medical Symptom Checker (ML Pipeline)

This folder contains the Phase 1 Artificial Intelligence and Machine Learning pipeline for the AI Medical Symptom Checker project.

## 1. Dataset
The project relies on four datasets provided in `data/raw/`:
- `dataset.csv`: The main symptom-to-disease mapping dataset containing 4920 rows (304 unique simulated cases) for 41 medical conditions. Each case lists up to 17 symptoms.
- `symptom_Description.csv`: Descriptions of the 41 medical conditions.
- `symptom_precaution.csv`: Precautionary steps for the 41 medical conditions.
- `Symptom-severity.csv`: Contains severity weights (1-7) for 132 unique symptoms, to be used as supporting data in later phases.

## 2. Preprocessing
The dataset cleaning is performed by `src/preprocess.py`. 
- Duplicate simulated patient records are dropped to prevent train/test data leakage.
- Symptom text is normalized: trailing whitespaces are removed, underscores are replaced with spaces, and text is converted to lowercase.
- Empty cells (`NaN`) are ignored and not treated as a symptom.

## 3. Feature engineering
The raw dataset structures symptoms across multiple columns (`Symptom_1` to `Symptom_17`). 
This was converted into a multi-hot binary symptom feature matrix where every unique normalized symptom (131 total) represents a single feature column (0 or 1). 
The output is saved as `data/processed/processed_symptom_dataset.csv`.

## 4. Models
We trained three baseline models in `src/train.py`:
- **Random Forest**: The primary model, trained with 100 estimators and balanced class weights to handle condition frequency differences.
- **Naive Bayes**: A MultinomialNB classifier suitable for binary feature vectors.
- **Decision Tree**: A single decision tree classifier serving as another baseline.

## 5. Evaluation
The models are evaluated using a 20% held-out test set in `src/evaluate.py`. Because the classification problem is multiclass with some class imbalance after deduplication, a **weighted average** was used for Precision, Recall, and F1-Score calculations.

Results (Weighted Average):
- **Random Forest**: Accuracy: 1.0000, Precision: 1.0000, Recall: 1.0000, F1: 1.0000
- **Naive Bayes**: Accuracy: 0.9672, Precision: 0.9617, Recall: 0.9672, F1: 0.9596
- **Decision Tree**: Accuracy: 0.6557, Precision: 0.6878, Recall: 0.6557, F1: 0.6430

*(Note: Random Forest achieved perfect classification on the deduplicated test set due to the deterministic rule-based nature of the original dataset generation.)*

## 6. Model files
Trained models and preprocessing artifacts are stored for the inference pipeline:
- `models/symptom_random_forest.joblib`: The primary Random Forest model.
- `artifacts/symptom_vocabulary.json`: The deterministic ordering of the 131 symptom features.
- `artifacts/symptom_normalization.json`: The mapping of raw symptom strings to normalized feature strings.

## 7. Running the pipeline
To reproduce the pipeline, use the virtual environment and run the following commands:
```bash
# 1. Inspect data
python src/inspect_dataset.py

# 2. Preprocess data and generate features
python src/preprocess.py

# 3. Train models
python src/train.py

# 4. Evaluate models
python src/evaluate.py

# 5. Test prediction persistence
python src/predict.py
```
