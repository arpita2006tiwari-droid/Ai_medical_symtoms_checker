import os
import json
import joblib
import pandas as pd
import numpy as np

def clean_symptom(symptom):
    if pd.isna(symptom):
        return None
    cleaned = str(symptom).strip().replace('_', ' ').lower()
    return cleaned if cleaned else None

def predict_conditions(user_symptoms):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'models')
    artifacts_dir = os.path.join(base_dir, 'artifacts')
    
    # Load required artifacts
    vocab_path = os.path.join(artifacts_dir, 'symptom_vocabulary.json')
    norm_path = os.path.join(artifacts_dir, 'symptom_normalization.json')
    model_path = os.path.join(models_dir, 'symptom_random_forest.joblib')
    
    with open(vocab_path, 'r') as f:
        vocab = json.load(f)['symptoms']
        
    with open(norm_path, 'r') as f:
        normalization_map = json.load(f)
        
    model = joblib.load(model_path)
    
    # Normalize input
    normalized_input = set()
    for sym in user_symptoms:
        cleaned = clean_symptom(sym)
        # Assuming the input is already normalized from some NLP layer, but just in case
        if cleaned in normalization_map:
            normalized_input.add(normalization_map[cleaned])
        elif cleaned in vocab:
            normalized_input.add(cleaned)
            
    # Create feature vector
    X = pd.DataFrame(0, index=[0], columns=vocab)
    for sym in normalized_input:
        if sym in vocab:
            X.at[0, sym] = 1
            
    # Predict
    probabilities = model.predict_proba(X)[0]
    classes = model.classes_
    
    # Get top 3 predictions
    top_3_idx = np.argsort(probabilities)[-3:][::-1]
    
    print("Possible conditions identified by the model:")
    print("(Note: This is not a medical diagnosis.)\n")
    
    for i, idx in enumerate(top_3_idx, 1):
        condition = classes[idx]
        prob = probabilities[idx] * 100
        print(f"{i}. {condition} — {prob:.2f}%")
        
    return [(classes[idx], probabilities[idx]) for idx in top_3_idx]

if __name__ == "__main__":
    # Persistence and prediction test
    test_symptoms = [
        "fever",
        "cough",
        "headache"
    ]
    print(f"Testing input symptoms: {test_symptoms}\n")
    predict_conditions(test_symptoms)
