import pandas as pd
import json
import os

def clean_symptom(symptom):
    if pd.isna(symptom):
        return None
    # Strip whitespace and replace spaces/underscores with spaces
    cleaned = str(symptom).strip().replace('_', ' ').lower()
    return cleaned if cleaned else None

def preprocess():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'raw')
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    artifacts_dir = os.path.join(base_dir, 'artifacts')
    
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Load raw dataset
    df = pd.read_csv(os.path.join(data_dir, 'dataset.csv'))
    
    # The dataset contains duplicate rows, but these represent different simulated patient cases.
    # We will keep them as they provide class weights/frequencies to some extent, 
    # but dropping them might be better to prevent data leakage in train/test splits.
    # Let's drop exact duplicates to ensure test set uniqueness.
    df = df.drop_duplicates().reset_index(drop=True)
    
    # Target column
    y = df['Disease'].str.strip()
    
    symptom_cols = [col for col in df.columns if 'Symptom' in col]
    
    # Build vocabulary and normalization rules
    symptom_normalization = {}
    unique_symptoms = set()
    
    for col in symptom_cols:
        for val in df[col].dropna():
            cleaned = clean_symptom(val)
            if cleaned:
                symptom_normalization[str(val)] = cleaned
                unique_symptoms.add(cleaned)
                
    # Sort vocabulary deterministically
    vocab = sorted(list(unique_symptoms))
    
    # Save artifacts
    with open(os.path.join(artifacts_dir, 'symptom_normalization.json'), 'w') as f:
        json.dump(symptom_normalization, f, indent=4)
        
    with open(os.path.join(artifacts_dir, 'symptom_vocabulary.json'), 'w') as f:
        json.dump({"symptoms": vocab}, f, indent=4)
        
    # Create Feature Matrix
    # Initialize matrix with zeros
    X = pd.DataFrame(0, index=df.index, columns=vocab)
    
    for idx, row in df.iterrows():
        for col in symptom_cols:
            val = row[col]
            if pd.notna(val):
                cleaned = clean_symptom(val)
                if cleaned in vocab:
                    X.at[idx, cleaned] = 1
                    
    # Combine target and features
    processed_df = pd.concat([y, X], axis=1)
    
    # Save processed dataset
    processed_path = os.path.join(processed_dir, 'processed_symptom_dataset.csv')
    processed_df.to_csv(processed_path, index=False)
    
    print(f"Processed dataset saved to: {processed_path}")
    print(f"Total features: {len(vocab)}")
    print(f"Total rows: {len(processed_df)}")

if __name__ == "__main__":
    preprocess()
