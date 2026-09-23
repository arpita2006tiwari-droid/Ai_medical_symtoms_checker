import os
import json
import joblib
import pandas as pd
import numpy as np
from app.config import settings
from app.services.symptom_service import clean_symptom

class MLService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
            cls._instance._load_model_and_artifacts()
        return cls._instance

    def _load_model_and_artifacts(self):
        try:
            model_full_path = os.path.join(settings.PROJECT_ROOT, settings.MODEL_PATH)
            vocab_full_path = os.path.join(settings.PROJECT_ROOT, settings.VOCABULARY_PATH)
            norm_full_path = os.path.join(settings.PROJECT_ROOT, settings.NORMALIZATION_PATH)

            self.model = joblib.load(model_full_path)
            
            with open(vocab_full_path, 'r') as f:
                self.vocabulary = json.load(f)['symptoms']
                
            with open(norm_full_path, 'r') as f:
                self.normalization_map = json.load(f)

            self.classes = self.model.classes_
            self.is_loaded = True
        except Exception as e:
            self.is_loaded = False
            self.load_error = str(e)
            print(f"Error loading ML artifacts: {e}")

    def predict(self, symptoms: list[str]):
        if not self.is_loaded:
            raise RuntimeError("ML model and artifacts are not loaded.")

        normalized_input = set()
        recognized_symptoms = []
        unknown_symptoms = []

        for sym in symptoms:
            cleaned = clean_symptom(sym)
            if not cleaned:
                unknown_symptoms.append(sym)
                continue

            if cleaned in self.normalization_map:
                normalized_value = self.normalization_map[cleaned]
                normalized_input.add(normalized_value)
                if sym not in recognized_symptoms:
                    recognized_symptoms.append(sym)
            elif cleaned in self.vocabulary:
                normalized_input.add(cleaned)
                if sym not in recognized_symptoms:
                    recognized_symptoms.append(sym)
            else:
                if sym not in unknown_symptoms:
                    unknown_symptoms.append(sym)

        # Create feature vector matching EXACT vocabulary ordering
        X = pd.DataFrame(0, index=[0], columns=self.vocabulary)
        for sym in normalized_input:
            if sym in self.vocabulary:
                X.at[0, sym] = 1

        # Predict
        probabilities = self.model.predict_proba(X)[0]
        
        # Get top 3 predictions
        top_3_idx = np.argsort(probabilities)[-3:][::-1]
        
        predictions = []
        for idx in top_3_idx:
            predictions.append({
                "condition": str(self.classes[idx]),
                "model_probability": float(probabilities[idx])
            })

        return {
            "recognized_symptoms": recognized_symptoms,
            "unknown_symptoms": unknown_symptoms,
            "predictions": predictions
        }

ml_service = MLService()
