# Phase 2D Inspection Report

## Objective
Implement a dynamic follow-up question engine that collects additional relevant information from the user before generating final predictions. The engine must operate deterministically without Large Language Models (LLMs) and rely strictly on the existing ML vocabulary.

## Follow-up Architecture & Dataset Co-occurrence Methodology
The engine operates by determining symptom co-occurrence probabilities from the existing training data (`ml/data/raw/dataset.csv`).

During startup (in `followup_service.py`):
1. The raw dataset is loaded.
2. The columns (`Symptom_1` to `Symptom_17`) are normalized using the same `clean_symptom` utility as the rest of the backend.
3. A sparse co-occurrence matrix is constructed: for every unique symptom pair `(S1, S2)` occurring in the same row, `matrix[S1][S2]` is incremented.

## Question Selection Algorithm
When a user provides an initial set of symptoms, the algorithm:
1. Iterates over all known vocabulary symptoms that the user *has not* yet reported (and hasn't already been asked about).
2. Calculates a relevance score by summing the co-occurrence frequencies between the candidate symptom and *all* currently recognized user symptoms.
3. Ranks candidates descending by score.
4. Selects the top-ranked candidate and formats it into a simple yes/no question (e.g., "Are you experiencing headache?").

## Question Limits
The system enforces a `MAX_FOLLOW_UP_QUESTIONS` limit (default: 3) to prevent conversational fatigue and keep data collection concise.

## Session/State Design
The engine is completely stateless on the server side. The client receives and passes a structured `FollowUpState` object:
- `recognized_symptoms`: List of known symptoms (e.g., `["high fever", "cough"]`).
- `asked_questions`: List of previously asked candidate symptom IDs.
- `answers`: Dictionary mapping asked candidates to `bool` or string representations.
- `follow_up_count`: Integer tracking iteration depth.

## Answer Processing & NLP Integration
When the user submits an answer:
1. The engine checks for basic affirmations (`yes`, `y`, `yeah`, `yep`) and negations (`no`, `n`, `nope`).
2. If free-form text is provided (e.g., "Yes, and I also have a headache"), the text is passed to the existing `NLPService.extract_symptoms()`.
3. If the answer explicitly negates a symptom (e.g., "I do not have a headache"), a basic heuristic traps the negation. Otherwise, any symptoms extracted by the `NLPService` are merged into the `recognized_symptoms` list.

## Confirmation
No LLMs or external AI APIs were integrated. The Random Forest model was untouched, and raw datasets remained unmodified. Medical diagnostic rules were completely avoided.
