# Phase 2B Inspection Report

## Raw CSV Analysis

The following files in `ml/data/raw/` were inspected before any development occurred.

### 1. `symptom_Description.csv`
- **Rows**: 41
- **Columns**: `['Disease', 'Description']`
- **Missing Values**: None
- **Summary**: Contains short paragraphs describing 41 unique conditions (e.g., Malaria, Drug Reaction).

### 2. `symptom_precaution.csv`
- **Rows**: 41
- **Columns**: `['Disease', 'Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']`
- **Missing Values**: 1 missing in `Precaution_3`, 1 missing in `Precaution_4`.
- **Summary**: Contains general health precautions. Missing values must be filtered out when retrieving precautions.

### 3. `Symptom-severity.csv`
- **Rows**: 133
- **Columns**: `['Symptom', 'weight']`
- **Missing Values**: None
- **Summary**: Contains severity weights (integers). The `Symptom` strings in this file often contain underscores (`_`), such as `skin_rash`. 

## Integration Strategy
To guarantee a match between the predictions and the severity data:
1. `medical_info_service.py` will read the CSV files once and store them in memory dictionaries.
2. The severity lookup dictionary will pre-clean the `Symptom` column strings (stripping whitespace and replacing underscores with spaces). This perfectly aligns the CSV data with the normalized symptoms identified by Phase 2A `symptom_vocabulary.json`.
3. The descriptions and precautions will lookup by `Disease` using an exact match, ignoring leading/trailing whitespace.
4. No data will be modified on disk.
