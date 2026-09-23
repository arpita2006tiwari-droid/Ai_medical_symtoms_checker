import os
import pandas as pd
from collections import defaultdict
from app.config import settings
from app.utils.paths import get_project_root
from app.services.symptom_service import clean_symptom
from app.services.nlp_service import nlp_service

class FollowUpService:
    def __init__(self):
        self.cooccurrence = defaultdict(lambda: defaultdict(int))
        self.is_loaded = False
        self.MAX_FOLLOW_UP_QUESTIONS = 3

    def load_data(self):
        if self.is_loaded:
            return

        dataset_path = os.path.join(get_project_root(), "ml/data/raw/dataset.csv")
        try:
            df = pd.read_csv(dataset_path)
            
            for _, row in df.iterrows():
                symptoms = set()
                # Skip the Disease column (index 0)
                for col in df.columns[1:]:
                    c = clean_symptom(row[col])
                    if c:
                        symptoms.add(c)
                
                symptoms_list = list(symptoms)
                for i in range(len(symptoms_list)):
                    for j in range(i + 1, len(symptoms_list)):
                        s1 = symptoms_list[i]
                        s2 = symptoms_list[j]
                        self.cooccurrence[s1][s2] += 1
                        self.cooccurrence[s2][s1] += 1
                        
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading dataset in FollowUpService: {e}")
            self.is_loaded = False

    def get_next_question(self, recognized_symptoms: list[str], asked_questions: list[str]) -> dict | None:
        """
        Determines the next best follow-up question based on symptom co-occurrence.
        Returns a question dictionary or None if no more questions should be asked.
        """
        if not self.is_loaded:
            self.load_data()

        # Score candidate symptoms
        scores = defaultdict(int)
        
        for current_sym in recognized_symptoms:
            if current_sym in self.cooccurrence:
                for candidate_sym, count in self.cooccurrence[current_sym].items():
                    if candidate_sym not in recognized_symptoms and candidate_sym not in asked_questions:
                        scores[candidate_sym] += count
                        
        if not scores:
            return None
            
        # Select highest scoring candidate
        best_candidate = max(scores.items(), key=lambda x: x[1])[0]
        
        # Simple formatting
        text = f"Are you experiencing {best_candidate}?"
        if best_candidate.startswith("a ") or best_candidate.startswith("an "):
            text = f"Are you experiencing {best_candidate}?"
        elif not best_candidate.endswith("s"):
            # A bit of lightweight grammar adjustment, not perfect but controlled
            text = f"Are you experiencing {best_candidate}?"

        return {
            "id": best_candidate,
            "type": "yes_no",
            "text": f"Are you experiencing {best_candidate}?"
        }

    def process_answer(self, state, question_id: str, answer_text: str):
        """
        Processes the user's answer, updates the state with newly recognized symptoms,
        and manages basic negation.
        """
        ans_lower = answer_text.lower().strip()
        
        # Basic negation check
        negation_phrases = ["no", "n", "nope", "not experiencing", "do not have", "don't have"]
        is_negative = any(negation in ans_lower for negation in negation_phrases)
        
        # Basic affirmation check
        affirmation_phrases = ["yes", "y", "yeah", "yep"]
        is_affirmative = any(ans_lower == aff or ans_lower.startswith(aff + " ") or ans_lower.startswith(aff + ",") for aff in affirmation_phrases)
        
        # Free-text NLP extraction
        extracted = nlp_service.extract_symptoms(answer_text)
        
        # If it's explicitly negative, we do NOT add the question_id even if NLP extracted it 
        # (e.g. "I do not have headache" extracts "headache" but shouldn't add it)
        if is_negative:
            # We record the answer as false
            state.answers[question_id] = False
            # We filter out the negated symptom if NLP accidentally picked it up
            extracted = [sym for sym in extracted if sym != question_id]
        elif is_affirmative:
            state.answers[question_id] = True
            if question_id not in extracted:
                extracted.append(question_id)
        else:
            # Unclear or free-text without explicit yes/no. 
            # If the NLP found the question_id, we consider it a yes.
            state.answers[question_id] = question_id in extracted
            
        # Merge extracted symptoms that aren't already recognized
        for sym in extracted:
            if sym not in state.recognized_symptoms:
                state.recognized_symptoms.append(sym)
                
        state.asked_questions.append(question_id)
        state.follow_up_count += 1
        
        return state

followup_service = FollowUpService()
