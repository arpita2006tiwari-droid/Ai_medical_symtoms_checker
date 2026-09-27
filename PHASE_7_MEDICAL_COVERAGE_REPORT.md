# Phase 7: Medical Coverage & Expansion Report

## Overview
This phase expanded the Symptom Checker application's medical coverage, safety rules, and terminology management.

Due to the strict mandate avoiding the use of unverified Kaggle datasets and the inability to auto-sign Data Use Agreements for genuine clinical records (like MIMIC-IV), **Phase C (ML Model Expansion) was blocked**. The existing Random Forest model is retained while the frontend and ontology layers have been heavily expanded to support 12 major bodily systems safely.

## 1. Datasets & Model
- **Datasets Acquired:** None downloaded. See `PHASE_7_DATA_SOURCE_AUDIT.md` for the audit of potential future sources (e.g., SymCat, Columbia DBMI).
- **License & Provenance:** Existing Kaggle-derived dataset retained.
- **Model Version:** `0.1.0 (Phase 7 - Ontology Expansion)`
- **Artifact Path:** `ml/models/symptom_random_forest.joblib` (Unchanged)
- **Model Performance:** Original 98%+ on synthetic test set. (Cannot claim real-world clinical accuracy).
- **Comparison with Original:** Identical model parameters. Terminology resolution improved.

## 2. Symptom Coverage (Before and After)
- **Before:** ~50 basic phrases mapped directly to vocabulary.
- **After:** Over 100 synonym phrases across 12 categories in `symptom_ontology.py` (Neurological, Cardiovascular, Respiratory, Gastrointestinal, ENT, Dermatology, Musculoskeletal, Urinary, Reproductive, Endocrine, General, Mental).

## 3. Safety Changes
- Overhauled `safety_rules.json` using authoritative CDC and Mayo Clinic guidelines.
- Created Rule SR001 and SR002 for emergency warning signs (chest pain, shortness of breath, severe neurological signs).
- Enhanced safety UI messaging to explicitly warn users rather than just suggest "urgent attention".

## 4. Test Results
- **Command:** `venv/bin/pytest`
- **Result:** 67 tests passed, 0 failures.
- Includes tests for safety rule precedence, natural language negation, backward compatibility, and feature parity.

## 5. Unsupported Symptoms and Conditions
- The newly added ontology symptoms (e.g., "seizures", "vision changes") are recognized by the NLP system but are **unsupported** by the current ML model (which only has 131 features). 
- The frontend explicitly warns the user: `"Recognized, but not supported by our current prediction model."`

## 6. Known Limitations & Future Work
- **Limitation:** The ML model feature space is static and synthetic.
- **Future Work:** The user must manually approve and import a legitimate statistical dataset (e.g., SymCat) into `ml/data/raw/`. Once imported, Phase C can proceed to align the 131 features with the newly expanded ontology.
