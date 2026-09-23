# Phase 2F Inspection Report

## Objective
Add Specialist Recommendation and Provider Information capabilities to the AI Medical Symptom Checker. These must remain strictly informational and completely non-diagnostic, functioning safely alongside the Phase 2E Urgency engine.

## Existing Architecture Inspected
- Reviewed the dataset unique conditions (41 total, spanning exact casing such as `Heart attack`, `GERD`, `(vertigo) Paroymsal  Positional Vertigo`).
- Checked `PredictionResponse` in `schemas.py` and `_build_prediction_response` in `prediction.py`.
- Checked `main.py` lifespan structure to maintain safe startup initializations.

## Specialist Service
The `SpecialistService` takes the highest-probability predicted condition from the ML model and references a deterministic catalog (`backend/app/data/specialist_mapping.json`). 
- **Mapping Structure**: `{"condition": "...", "specialist": "...", "reason": "..."}`
- **Fallback**: If the condition isn't in the mapping, or if there is no prediction available, the service defaults gracefully to `General Physician` with an informational fallback reason.
- **Priority Logic**: Primary recommendation is always based on the absolute top-ranked ML condition string. It avoids assuming multiple specialists to prevent confusing the user.

## Provider Information Architecture
Phase 2F explicitly avoids generating fake healthcare providers, as fabricating hospital names or doctors is hazardous. 
Instead, a separate endpoint (`POST /api/providers/info`) and service (`ProviderService`) have been provisioned. Currently, it acts as an architectural placeholder returning informational availability (`available: false`), making it effortless to drop in an external API like Google Places in a future phase.

## API Changes
- `POST /api/analyze` and `POST /api/predict` now append a `specialist_recommendation` block alongside the `urgency` block.
- `POST /api/providers/info` exposed for provider infrastructure queries.

## Limitations
- **Not a diagnosis**: Model probabilities do not represent real-world medical certainty, and specialist mapping reflects standard informational routing, not a clinical triage directive.
- **Urgency Independence**: A specialist recommendation does not negate the `urgency` safety engine. Both operate in parallel to give distinct types of guidance.
