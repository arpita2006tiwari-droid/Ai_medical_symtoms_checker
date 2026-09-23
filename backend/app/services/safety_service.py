import json
import os
from app.utils.paths import get_project_root
from app.schemas import UrgencyAssessment, SafetyRuleMatch

class SafetyService:
    def __init__(self):
        self.rules = []
        self.is_loaded = False
        self.PRIORITY_MAP = {
            "routine": 0,
            "medical_attention": 1,
            "urgent_attention": 2
        }
        
    def load_data(self):
        if self.is_loaded:
            return
            
        rules_path = os.path.join(get_project_root(), "backend/app/data/safety_rules.json")
        try:
            with open(rules_path, 'r') as f:
                data = json.load(f)
                self.rules = data.get("rules", [])
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading safety rules: {e}")
            self.is_loaded = False
            
    def assess(self, symptoms: list[str]) -> dict:
        """
        Evaluates recognized symptoms against the safety rules catalog.
        Returns a dictionary representation of an UrgencyAssessment.
        """
        if not self.is_loaded:
            self.load_data()
            
        matched_rules = []
        highest_priority = -1
        highest_level = "routine"
        best_message = "No configured high-risk safety indicators were detected from the symptoms provided. This does not rule out a medical problem. Seek medical advice if symptoms persist, worsen, or concern you."
        
        # We need a quick way to check if any symptom matches the rules.
        # Ensure we're case-insensitively comparing cleanly normalized strings.
        clean_symptoms = {sym.lower().strip() for sym in symptoms}
        
        # Collect all triggered rules
        for rule in self.rules:
            rule_symptoms = {sym.lower().strip() for sym in rule.get("symptoms", [])}
            
            # Intersection means the user has at least one of the trigger symptoms
            if clean_symptoms.intersection(rule_symptoms):
                matched_rules.append(
                    SafetyRuleMatch(
                        rule_id=rule.get("id"),
                        reason=rule.get("reason")
                    )
                )
                
                # Update highest urgency tracking
                level = rule.get("category", "routine")
                priority = self.PRIORITY_MAP.get(level, 0)
                if priority > highest_priority:
                    highest_priority = priority
                    highest_level = level
                    best_message = rule.get("message", best_message)
                    
        # Return structured UrgencyAssessment dictionary
        return UrgencyAssessment(
            level=highest_level,
            message=best_message,
            matched_rules=matched_rules
        ).model_dump()

safety_service = SafetyService()
