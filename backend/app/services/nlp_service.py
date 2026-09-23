import re
import json
import os
from app.config import settings
from app.utils.paths import get_project_root

class NLPService:
    def __init__(self):
        self.pattern = None
        self.is_loaded = False

    def load_data(self):
        if self.is_loaded:
            return

        vocab_full_path = os.path.join(get_project_root(), settings.VOCABULARY_PATH)
        
        try:
            with open(vocab_full_path, 'r') as f:
                vocabulary = json.load(f)['symptoms']
                
            # Sort by length descending to match longest phrases first (e.g., "high fever" before "fever")
            sorted_vocab = sorted(vocabulary, key=len, reverse=True)
            
            # Escape vocabulary items to ensure regex safety (handling hyphens, etc.)
            escaped_vocab = [re.escape(sym) for sym in sorted_vocab]
            
            # Construct a word-bounded regex pattern, joined by OR
            regex_str = r'\b(' + '|'.join(escaped_vocab) + r')\b'
            self.pattern = re.compile(regex_str, re.IGNORECASE)
            
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading vocabulary in NLPService: {e}")
            self.is_loaded = False

    def extract_symptoms(self, text: str) -> list[str]:
        """
        Extracts recognized symptoms from natural language text using a deterministic
        regex pattern compiled from the exact ML vocabulary.
        """
        if not self.is_loaded:
            self.load_data()
            if not self.is_loaded:
                raise RuntimeError("NLP Service vocabulary not loaded.")

        if not text or not text.strip():
            return []

        # Find all matching phrases
        matches = self.pattern.findall(text)
        
        # Lowercase and deduplicate while preserving discovery order
        seen = set()
        recognized_symptoms = []
        for match in matches:
            sym_clean = match.lower().strip()
            if sym_clean not in seen:
                seen.add(sym_clean)
                recognized_symptoms.append(sym_clean)
                
        return recognized_symptoms

# Singleton instance
nlp_service = NLPService()
