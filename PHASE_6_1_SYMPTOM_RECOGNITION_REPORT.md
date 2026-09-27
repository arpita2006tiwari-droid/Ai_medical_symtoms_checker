# Phase 6.1: Symptom Recognition Expansion Report

## 1. Original Limitations
The previous NLP symptom extraction service relied on a strict regex built solely from the 131 symptoms present in the trained Random Forest model's vocabulary (e.g., "high fever", "cough"). Because of this strict binding, if a user described a symptom not explicitly in the training set (like "migraine" or "dizziness"), the system would fail to extract any symptoms and return an error: *"No medical symptoms could be extracted from your text. Please be more specific."* This severely limited usability for common medical queries.

## 2. New Supported Symptom Terminology
A new terminology and synonym layer has been implemented in `NLPService` independent of the ML model vocabulary. This supports natural-language variations and maps them to canonical symptoms. Supported groups now include:
- **Head/Neurological:** migraine, headache, head pain, pain in my head, head hurts, dizziness, dizzy, vertigo, numbness, tingling, seizure, seizures
- **Ear/Nose/Throat:** earache, ear ache, ear pain, pain in my ear, sore throat, throat pain, blocked nose, stuffy nose, runny nose, sinus pain, hearing loss
- **Digestive:** stomach ache, stomach pain, abdominal pain, belly pain, nausea, nauseous, vomiting, throwing up, diarrhea, diarrhoea, constipation, bloating, indigestion
- **Musculoskeletal:** back pain, lower back pain, joint pain, muscle pain, body aches, neck pain, shoulder pain, leg pain, stiffness, weakness
- **Respiratory/General:** cough, coughing, high fever, mild fever, fever, chills, shortness of breath, breathlessness, chest pain, fatigue, tiredness, sweating

The new layer handles synonym deduplication, phrase boundaries, and case-insensitive matching. It also applies basic window-based logic to ignore negated or uncertain symptoms (e.g., "no headache", "don't know if I have a fever", "I had a headache last week but not now").

## 3. Current Model-Supported Symptoms
The system maintains the existing integration with the original ML model. Symptoms that match the 131 vocabulary terms (such as "cough", "high fever", "fatigue") are mapped securely and flagged as `is_model_supported = true`. 

## 4. Recognized-but-Unsupported Symptoms
When the user reports a symptom in the extended terminology that the model was never trained on (e.g., "migraine", "dizziness"), it is flagged as `is_model_supported = false`. 
- These symptoms are passed safely into `unknown_symptoms` in the backend and do *not* corrupt the fixed 131-dimension feature vector.
- The frontend has been updated with a new **Review Step** where the user can see exactly which symptoms are supported by the model and which are merely recognized.
- If all extracted symptoms are unsupported, the user sees a specific warning: *"None of the symptoms recognized are directly supported by our current model. You can still proceed to receive an analysis, but the model may have limited coverage and cannot analyze these symptoms directly."* No fake predictions are generated for empty feature vectors.

## 5. API Changes
- **`SymptomExtractionResponse`**: Added a new `detailed_symptoms` field containing a list of `RecognizedSymptom` objects. Each object provides:
  - `canonical` (str)
  - `original_phrase` (str)
  - `is_model_supported` (bool)
- **`/api/predict`**: Updated to properly handle cases where no supported symptoms exist, returning an empty `predictions` list instead of generating false predictions from a zero-vector.

## 6. Limitations and Future Model Retraining Needs
The current implementation allows for a vastly improved UX by acknowledging common symptoms, but it highlights the limitations of the underlying dataset. The model must eventually be retrained on a broader dataset that includes the newly recognized symptoms like "migraine" and "nausea" to provide accurate clinical predictions based on them. Until retrained, the system correctly defers and warns the user about these limitations.

## 7. Exact Tests Run and Results
The `test_nlp.py` suite was expanded and run using `pytest`:
- `test_extract_symptoms_migraine` ("I have migraine") -> Extracted: migraine
- `test_extract_symptoms_a_migraine` ("I have a migraine") -> Extracted: migraine
- `test_extract_symptoms_headache_earache` -> Extracted: headache, earache
- `test_extract_symptoms_head_ear_pain` -> Extracted: headache, earache
- `test_extract_symptoms_stomach_nausea` -> Extracted: stomach pain, nausea
- `test_extract_symptoms_lower_back_dizziness` -> Extracted: back pain, dizziness
- `test_extract_symptoms_cough_fever` -> Extracted: cough, high fever
- `test_extract_symptoms_negation_headache` ("I have no headache") -> Rejected: headache
- `test_extract_symptoms_negation_ear_pain` ("I don't have ear pain") -> Rejected: earache
- `test_extract_symptoms_negation_past` ("I had a headache last week but not now") -> Rejected: headache
- `test_extract_symptoms_negation_uncertain` ("I don't know if I have a fever") -> Rejected: fever
- `test_extract_symptoms_unrelated` ("Hello, how are you?") -> Extracted: none

**Result**: 19 tests passed, 0 failures. The frontend built successfully and the end-to-end integration maintains security and state logic intact.
