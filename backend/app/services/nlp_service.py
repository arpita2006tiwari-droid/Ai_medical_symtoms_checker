import re
import json
import os
from app.config import settings
from app.utils.paths import get_project_root

from app.services.symptom_ontology import SYMPTOM_ONTOLOGY

class NLPService:
    def __init__(self):
        self.pattern = None
        self.model_vocabulary = set()
        self.symptom_map = {}
        self.is_loaded = False
        
        # Negation/uncertainty cues
        self.negation_pattern = re.compile(
            r'\b(no|not|don\'t|doesn\'t|didn\'t|without|never|hardly|cannot|can\'t)\b', 
            re.IGNORECASE
        )
        self.uncertainty_pattern = re.compile(
            r'\b(unsure|don\'t know|might|maybe|possibly|not sure)\b',
            re.IGNORECASE
        )
        self.past_pattern = re.compile(
            r'\b(last week|past|used to|previously|yesterday|days ago|but not now)\b',
            re.IGNORECASE
        )

    def load_data(self):
        if self.is_loaded:
            return

        vocab_full_path = os.path.join(get_project_root(), settings.VOCABULARY_PATH)
        
        try:
            with open(vocab_full_path, 'r') as f:
                vocabulary = json.load(f)['symptoms']
            
            self.model_vocabulary = set(vocabulary)
            
            # Combine vocabulary and extended symptoms
            self.symptom_map = {}
            # 1. Add extended symptoms from ontology
            for canonical, data in SYMPTOM_ONTOLOGY.items():
                for phrase in data["synonyms"]:
                    self.symptom_map[phrase.lower()] = canonical
                
            # 2. Add model vocabulary (overrides or supplements)
            for sym in vocabulary:
                self.symptom_map[sym.lower()] = sym
                
            # Sort phrases by length descending
            sorted_phrases = sorted(self.symptom_map.keys(), key=len, reverse=True)
            
            escaped_phrases = [re.escape(phrase) for phrase in sorted_phrases]
            regex_str = r'\b(' + '|'.join(escaped_phrases) + r')\b'
            self.pattern = re.compile(regex_str, re.IGNORECASE)
            
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading vocabulary in NLPService: {e}")
            self.is_loaded = False

    def is_negated(self, text: str, match_start: int, match_end: int) -> bool:
        # Check window before the match
        window_start = max(0, match_start - 35) # approx 5-6 words
        window_text_before = text[window_start:match_start]
        
        # Check window after the match (for "but not now")
        window_end = min(len(text), match_end + 35)
        window_text_after = text[match_end:window_end]

        if self.negation_pattern.search(window_text_before):
            return True
        if self.uncertainty_pattern.search(window_text_before):
            return True
        if self.past_pattern.search(window_text_before):
            return True
            
        # Post-match checks
        if "but not now" in window_text_after.lower():
            return True
            
        return False

    def extract_symptoms_detailed(self, text: str):
        if not self.is_loaded:
            self.load_data()
            if not self.is_loaded:
                raise RuntimeError("NLP Service vocabulary not loaded.")

        if not text or not text.strip():
            return []

        detailed_symptoms = []
        seen_canonical = set()
        
        for match in self.pattern.finditer(text):
            phrase = match.group(0)
            phrase_lower = phrase.lower().strip()
            
            if self.is_negated(text, match.start(), match.end()):
                continue
                
            canonical = self.symptom_map.get(phrase_lower, phrase_lower)
            
            if canonical not in seen_canonical:
                seen_canonical.add(canonical)
                is_model_supported = canonical in self.model_vocabulary
                
                # Fetch ontology metadata if available
                ontology_data = SYMPTOM_ONTOLOGY.get(canonical, {})
                category = ontology_data.get("category", "General")
                source = ontology_data.get("source", "Model Vocabulary")
                
                detailed_symptoms.append({
                    "canonical": canonical,
                    "original_phrase": phrase,
                    "category": category,
                    "source": source,
                    "is_model_supported": is_model_supported
                })
                
        return detailed_symptoms

    def extract_symptoms(self, text: str) -> list[str]:
        # Backward compatibility method
        detailed = self.extract_symptoms_detailed(text)
        return [d["canonical"] for d in detailed]

nlp_service = NLPService()
