# Phase 2A Inspection Report

## ML Artifacts Location
The backend must load the following files relative to the project root:
- **Random Forest Model**: `ml/models/symptom_random_forest.joblib`
- **Symptom Vocabulary**: `ml/artifacts/symptom_vocabulary.json` (contains the exact list of 131 symptom features in specific order).
- **Symptom Normalization Mapping**: `ml/artifacts/symptom_normalization.json` (maps raw user input to normalized feature strings).

## Preprocessing Logic Details (from ml/src/predict.py)
1. **Symptom Cleaning (`clean_symptom`)**:
   - Each input symptom is cast to a string.
   - Surrounding whitespace is stripped.
   - Underscores (`_`) are replaced with spaces (` `).
   - Text is converted to lowercase.

2. **Normalization**:
   - The cleaned symptom is checked against the keys in `symptom_normalization.json`.
   - If present, it maps to the normalized value.
   - If not in the normalization map, it checks if the cleaned symptom is directly present in the `symptom_vocabulary.json` list. If so, it keeps it.
   - Any remaining unrecognized symptoms are ignored in the ML model features, but the API will track them and report them in the `unknown_symptoms` list as required.

3. **Feature Vector Creation**:
   - The model expects a pandas DataFrame (or equivalent 2D structure) with exactly the same columns in the exact same order as the vocabulary list.
   - It is initialized to `0`.
   - For each recognized normalized symptom, the corresponding feature index/column is set to `1`.

4. **Prediction**:
   - Uses `model.predict_proba(X)` to get probabilities.
   - Combines probabilities with `model.classes_`.
   - Sorts the results to return the top 3 probable conditions.

*No changes will be made to these ML files, and the prediction logic in FastAPI perfectly mirrors this vectorization process.*

## Final Verification (Issue Investigation)

### 1. Why "fever" was unknown
Upon passing `["fever", "cough", "headache"]` to the API, `"fever"` was returned in `unknown_symptoms`. Inspection of `ml/artifacts/symptom_vocabulary.json` reveals that `"fever"` is genuinely **not** present in the vocabulary. The closest representations in the vocabulary are `"high fever"` and `"mild fever"`. `ml/artifacts/symptom_normalization.json` contains keys for `" high_fever"` and `" mild_fever"`, but does not contain a mapping for just `"fever"`.

The original `predict.py` script simply skipped unrecognized symptoms silently, meaning it was effectively ignoring `"fever"` all along. The new API correctly caught this missing feature and surfaced it.

### 2. Resolution
Since the instruction was explicitly to **NOT** invent a new medical synonym mapping and **NOT** retrain the model, the backend was kept exactly as is. `"fever"` is correctly categorized as an unknown symptom.

### 3. Test Symptoms Used
To ensure a valid 1:1 test that perfectly mirrors `predict.py`, the test was updated to use REAL symptoms found in the vocabulary:
`["high fever", "cough", "headache"]`.

### 4. Comparison with `predict.py`
Both `backend POST /api/predict` and `python ml/src/predict.py` were run with the updated symptom list `["high fever", "cough", "headache"]`.
The predictions and model probabilities match identically:
1. Bronchial Asthma — 26.00% (0.26)
2. Paralysis (brain hemorrhage) — 17.00% (0.17)
3. Hypertension — 11.00% (0.11)

### 5. Scikit-learn Version Issue
The environment used to train the model utilized `scikit-learn==1.9.1`. When running the script previously, the system python (`1.8.0`) was inadvertently used, triggering the `InconsistentVersionWarning`. The `backend/requirements.txt` has now been strictly pinned to `scikit-learn==1.9.1` to completely resolve the warning and guarantee consistency across different installations without modifying the model artifact.

### 6. Overall Status
All 6 pytest tests (including health, empty lists, empty strings, duplicates, unknown tracking) are fully passing. Phase 2A is finalized and thoroughly verified.
