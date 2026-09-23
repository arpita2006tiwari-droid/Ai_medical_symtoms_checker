import pandas as pd
import os

def inspect_datasets():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'raw')
    report_path = os.path.join(base_dir, 'reports', 'dataset_inspection.txt')
    
    # Load datasets
    df_main = pd.read_csv(os.path.join(data_dir, 'dataset.csv'))
    df_desc = pd.read_csv(os.path.join(data_dir, 'symptom_Description.csv'))
    df_prec = pd.read_csv(os.path.join(data_dir, 'symptom_precaution.csv'))
    df_sev = pd.read_csv(os.path.join(data_dir, 'Symptom-severity.csv'))
    
    with open(report_path, 'w') as f:
        # Main dataset
        f.write("## Main dataset\n")
        f.write("File: dataset.csv\n")
        f.write(f"Rows: {len(df_main)}\n")
        f.write(f"Columns: {len(df_main.columns)}\n")
        f.write(f"Target: Disease\n") # Check if it's 'Disease'
        if 'Disease' in df_main.columns:
            f.write(f"Number of conditions: {df_main['Disease'].nunique()}\n")
        else:
            f.write("Number of conditions: Target column 'Disease' not found\n")
            
        symptom_cols = [c for c in df_main.columns if 'Symptom' in c]
        f.write(f"Number of symptom columns: {len(symptom_cols)}\n")
        
        # Get unique symptoms across all symptom columns
        unique_symptoms = set()
        for col in symptom_cols:
            unique_symptoms.update(df_main[col].dropna().unique())
        f.write(f"Number of unique symptoms: {len(unique_symptoms)}\n")
        
        f.write(f"Missing values: {df_main.isnull().sum().sum()}\n")
        f.write(f"Duplicate rows: {df_main.duplicated().sum()}\n\n")
        
        # Description dataset
        f.write("## Description dataset\n")
        f.write(f"Rows: {len(df_desc)}\n")
        f.write(f"Columns: {len(df_desc.columns)}\n")
        if 'Disease' in df_desc.columns:
            f.write(f"Number of conditions: {df_desc['Disease'].nunique()}\n")
        else:
            f.write("Number of conditions: Unknown (no 'Disease' col)\n")
        f.write(f"Missing values: {df_desc.isnull().sum().sum()}\n\n")
        
        # Precaution dataset
        f.write("## Precaution dataset\n")
        f.write(f"Rows: {len(df_prec)}\n")
        f.write(f"Columns: {len(df_prec.columns)}\n")
        if 'Disease' in df_prec.columns:
            f.write(f"Number of conditions: {df_prec['Disease'].nunique()}\n")
        else:
            f.write("Number of conditions: Unknown (no 'Disease' col)\n")
        f.write(f"Missing values: {df_prec.isnull().sum().sum()}\n\n")
        
        # Severity dataset
        f.write("## Severity dataset\n")
        f.write(f"Rows: {len(df_sev)}\n")
        f.write(f"Columns: {len(df_sev.columns)}\n")
        if 'Symptom' in df_sev.columns:
            f.write(f"Number of symptoms: {df_sev['Symptom'].nunique()}\n")
        else:
            f.write("Number of symptoms: Unknown (no 'Symptom' col)\n")
        f.write(f"Missing values: {df_sev.isnull().sum().sum()}\n")
        if 'weight' in df_sev.columns:
            f.write(f"Severity range: {df_sev['weight'].min()} to {df_sev['weight'].max()}\n\n")
        else:
            f.write("Severity range: Unknown (no 'weight' col)\n\n")
            
        # Match disease names
        if 'Disease' in df_main.columns and 'Disease' in df_desc.columns and 'Disease' in df_prec.columns:
            main_diseases = set(df_main['Disease'].str.strip())
            desc_diseases = set(df_desc['Disease'].str.strip())
            prec_diseases = set(df_prec['Disease'].str.strip())
            
            f.write("## Disease Name Matches\n")
            missing_in_desc = main_diseases - desc_diseases
            missing_in_prec = main_diseases - prec_diseases
            if not missing_in_desc and not missing_in_prec:
                f.write("All diseases match perfectly across main, description, and precaution datasets.\n")
            else:
                f.write(f"Diseases in main but missing in description: {len(missing_in_desc)}\n")
                if missing_in_desc: f.write(f"Examples: {list(missing_in_desc)[:5]}\n")
                f.write(f"Diseases in main but missing in precaution: {len(missing_in_prec)}\n")
                if missing_in_prec: f.write(f"Examples: {list(missing_in_prec)[:5]}\n")
            
if __name__ == "__main__":
    inspect_datasets()
