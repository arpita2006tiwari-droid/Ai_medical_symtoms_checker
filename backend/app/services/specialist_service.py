import json
import os
from typing import Optional
from app.utils.paths import get_project_root
from app.schemas import SpecialistRecommendation

class SpecialistService:
    def __init__(self):
        self.mappings = {}
        self.is_loaded = False
        self.fallback = {
            "specialist": "General Physician",
            "reason": "A general medical evaluation may be an appropriate starting point because the available information does not support a more specific specialist recommendation.",
            "basis": "general_fallback"
        }

    def load_data(self):
        if self.is_loaded:
            return

        mapping_path = os.path.join(get_project_root(), "backend/app/data/specialist_mapping.json")
        try:
            with open(mapping_path, 'r') as f:
                data = json.load(f)
                
            for mapping in data.get("mappings", []):
                cond = mapping.get("condition", "").strip()
                if cond:
                    self.mappings[cond] = {
                        "specialist": mapping.get("specialist", ""),
                        "reason": mapping.get("reason", "")
                    }
                    
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading specialist mappings: {e}")
            self.is_loaded = False

    def recommend(self, top_condition: Optional[str]) -> SpecialistRecommendation:
        """
        Determines the appropriate specialist recommendation based on the provided top condition.
        Returns a structured SpecialistRecommendation.
        """
        if not self.is_loaded:
            self.load_data()
            
        if not top_condition:
            return SpecialistRecommendation(**self.fallback)
            
        top_condition_clean = top_condition.strip()
        
        # Check explicit condition mapping
        if top_condition_clean in self.mappings:
            mapped_data = self.mappings[top_condition_clean]
            return SpecialistRecommendation(
                specialist=mapped_data["specialist"],
                reason=mapped_data["reason"],
                basis="predicted_condition",
                condition=top_condition_clean
            )
            
        # Fallback if unknown or unmapped
        return SpecialistRecommendation(
            **self.fallback,
            condition=top_condition_clean
        )

specialist_service = SpecialistService()
