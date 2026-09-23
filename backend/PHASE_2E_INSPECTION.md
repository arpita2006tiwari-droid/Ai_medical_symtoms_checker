# Phase 2E Inspection Report

## Objective
Implement a Safety & Urgency Classification Engine that operates independently of the ML prediction model. It provides purely informational guidance (e.g., routine, medical attention, urgent attention) by evaluating user symptoms against a controlled catalog of safety rules.

## Architecture
- **Rules File**: `backend/app/data/safety_rules.json` contains a structured catalog of rules.
- **Safety Service**: `backend/app/services/safety_service.py` evaluates normalized symptoms against these rules at runtime.
- **Integration**: The safety assessment is seamlessly injected into the existing `PredictionResponse` during `POST /api/analyze` and `POST /api/predict`.

## Safety Rule Format and Urgency Categories
Rules use an ID, urgency category, matching symptom triggers, message, reason, and source. 
Priority overrides: `urgent_attention` > `medical_attention` > `routine`.

## Limitations and Disclaimer
- **Vocabulary Constraint**: Safety rules MUST strictly align with `ml/artifacts/symptom_vocabulary.json`. For instance, "fever" is not a recognized generic symptom, only "high fever" or "mild fever" are available. Rules are crafted around these specific constraints.
- **Not Clinically Validated**: This is a simplified academic project. The rule set is not a clinically validated triage system. It does not replace professional medical evaluations.
- **No LLMs / AI Claims**: The system avoids fabricating medical states and does not rely on Large Language Models to diagnose or triage.

## API Changes
No endpoints were broken. `PredictionResponse` was extended with an `urgency` block:
```json
"urgency": {
  "level": "urgent_attention",
  "message": "The symptoms provided match a configured high-risk safety indicator. Prompt medical attention is recommended. This assessment is informational and is not a diagnosis.",
  "matched_rules": [
    {
      "rule_id": "SR001",
      "reason": "Chest pain or breathlessness are critical indicators."
    }
  ]
}
```
