# Data Source Audit and Provenance

## Current Data Structure
- `dataset.csv`: 4920 rows. 131 symptoms as binary columns. 41 conditions as the target `Disease` column. Likely synthetically augmented or derived from the Columbia University NLP dataset, popularized on Kaggle.
- `Symptom-severity.csv`: Weights for symptoms.
- `symptom_Description.csv`: Text descriptions for diseases.
- `symptom_precaution.csv`: Precautions for diseases.

## Authorized Reputable Sources
Any future dataset acquisitions must meet strict provenance and usage criteria. Refer to `PHASE_7_DATA_SOURCE_AUDIT.md` in the project root for the detailed audit of potential external sources to be used for model retraining.

**Warning:** Do not commit PHI (Protected Health Information) or unauthorized medical datasets to this repository. All datasets must be legally accessible and properly licensed for research.
