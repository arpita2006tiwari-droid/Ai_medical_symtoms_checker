# AI Medical Symptom Checker - Data Dictionary

This document explains the columns and meanings for the primary training datasets included in this folder.

## 01_Original_Kaggle_Dataset.csv
This is the raw format of the data sourced originally from Kaggle.

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| **Disease** | String (Categorical) | The target condition/diagnosis assigned to this simulated patient case. | `Fungal infection`, `Hepatitis C` |
| **Symptom_1** to **Symptom_17** | String (Categorical) | A variable-width array of symptoms reported for the case. Each column contains a single symptom string (e.g., `itching`). Unused columns in cases with fewer than 17 symptoms are left empty (NaN/null). | ` skin_rash`, ` nodal_skin_eruptions` |

## 02_Processed_Training_Dataset.csv
This is the feature matrix passed into the Scikit-Learn `RandomForestClassifier`. It resolves the variable-width array from the original dataset into a standard one-hot encoded matrix.

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| **Disease** | String (Categorical) | The target condition/diagnosis. (Target/Label Column) | `Fungal infection`, `Hepatitis C` |
| **[Symptom Names]** *(e.g., `itching`, `skin rash`, `chills`)* | Integer (Binary 0/1) | 131 columns representing each unique recognized symptom. A value of `1` indicates the presence of the symptom in the patient case, and `0` indicates its absence. Underscores have been stripped and casing lowercased compared to the raw data. | `0`, `1` |

---
## Supplementary Dataset Notes

*   **07_Kaggle_Symptom_Descriptions.csv**: `Disease` (Target mapping), `Description` (Paragraph text describing the illness).
*   **08_Kaggle_Symptom_Severities.csv**: `Symptom` (String mapping), `weight` (Integer 1-7 denoting how severe a symptom usually is).
*   **09_Kaggle_Symptom_Precautions.csv**: `Disease` (Target mapping), `Precaution_1` through `Precaution_4` (Strings offering immediate advice for the illness).
