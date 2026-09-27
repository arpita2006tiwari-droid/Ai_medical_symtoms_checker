# Phase 7: Data Source Audit

## 1. Audit of Current Project State

### Datasets
The current ML dataset in `ml/data/raw/` contains:
- `dataset.csv`: 4920 records covering 131 symptom features and 41 diseases. This dataset is a highly structured, binary-encoded matrix. It appears to be synthetic or highly oversampled data commonly found on Kaggle (often derived from Columbia University's 2004 NLP dataset on discharge summaries). 
- **Provenance:** Unclear primary origin. Found on Kaggle. 
- **Bias/Missingness:** Perfectly balanced (exactly 120 samples per disease). This does not reflect real-world clinical prevalence. Symptoms are rigidly encoded.

### Model
- Random Forest model in `ml/models/symptom_random_forest.joblib`.

### NLP Terminology
- Currently mapped to ~50 natural language variations in `nlp_service.py` under 5 major categories.

### Safety Rules & Follow-up
- Follow-up uses a hardcoded co-occurrence matrix.
- Safety rules are hardcoded in `safety_service.py`.

---

## 2. Evaluation of Candidate Datasets for Phase C Expansion

To expand the model with real, evidence-based data, we have evaluated the following reputable public health and research resources:

### Candidate A: Columbia University Disease-Symptom Knowledge Database
*   **Source:** Department of Biomedical Informatics (DBMI), Columbia University (Wang X, et al., 2008).
*   **License/Usage:** Academic/Research use (usually hosted via third-party repositories).
*   **Methodology:** Extracted from clinical discharge summaries from New York-Presbyterian Hospital using the MedLEE NLP system. Maps diseases to UMLS codes.
*   **Population:** Hospitalized patients in New York (2004).
*   **Records:** Statistical association matrix covering ~150 frequent diseases and associated symptoms.
*   **Genuine vs Synthetic:** Genuine clinical observations aggregated into statistical frequencies. Not individual patient records.
*   **Bias/Limitations:** Hospitalized patients only (skews towards severe diseases). Data is older (2004).

### Candidate B: MIMIC-IV (Medical Information Mart for Intensive Care)
*   **Source:** MIT Lab for Computational Physiology.
*   **License/Usage:** Restricted. Requires formal credentialing, CITI training certification, and a signed Data Use Agreement (DUA).
*   **Methodology:** De-identified Electronic Health Records (EHR) from Beth Israel Deaconess Medical Center.
*   **Population:** ICU and Emergency Department patients (2008-2019).
*   **Genuine vs Synthetic:** 100% genuine patient records.
*   **Bias/Limitations:** ICU/ED patients only. Not representative of general practice or mild outpatient symptoms.
*   **Blocker:** Cannot be downloaded or processed by this automated system without human credentialing.

### Candidate C: SymCat (Symptom-Disease Database)
*   **Source:** Derived from CDC National Hospital Ambulatory Medical Care Survey (NHAMCS).
*   **License/Usage:** Public domain data (CDC).
*   **Methodology:** Maps symptoms to ICD-9/10 codes based on emergency department and outpatient visits.
*   **Genuine vs Synthetic:** Statistical aggregates of genuine patient encounters.
*   **Bias/Limitations:** Based on outpatient/ED coding, which can sometimes reflect billing practices over pure clinical presentation.

---

## 3. Conclusions and Execution Strategy

**Data Access Blocker:** 
Acquiring genuine patient-level EHR data (like MIMIC-IV) requires human credentialing and ethical agreements. Relying on open-source Kaggle datasets without verifiable provenance violates the strict safety rules of this academic prototype.

**Next Steps:**
1. **Proceed** with expanding the Symptom Ontology (Phase B), API Contracts (Phase D), Safety/Follow-up (Phase E), and Frontend (Phase F). We will implement a comprehensive taxonomy covering 12 bodily systems.
2. **Block** Phase C (Model Retraining). The existing Random Forest model and dataset will be retained untouched. 
3. **Manual Action Required:** The user must manually approve a specific dataset (e.g., SymCat statistical data) and provide the raw files in `ml/data/raw/` before Phase C can be safely executed.
