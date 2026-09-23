# Phase 3 Inspection Report

## Objective
Integrate Conversational AI using Google Gemini (`google-genai` SDK) to act purely as a natural language presentation layer.

## Existing Architecture Inspected
- Evaluated `backend/app/config.py` and `backend/requirements.txt`.
- Determined that `LLMService` must sit on top of the deterministic analysis pipeline (`NLPService -> MLService -> SafetyService -> SpecialistService`).
- Reused existing JSON structure and `PredictionResponse` from `_build_prediction_response` in `prediction.py` to avoid duplicate ML calls.

## LLM Architecture
- **Dependency**: Used `google-genai>=0.1.0`.
- **Environment**: Keys (`GEMINI_API_KEY`) and models (`GEMINI_MODEL`) are securely configured via environment variables.
- **Service Abstraction**: `backend/app/services/llm_service.py` houses all LLM specific logic, decoupling Gemini from the API routing layer.

## Prompt Architecture
- **System Prompt**: Created `backend/app/prompts/medical_assistant_prompt.py` which explicitly forbids the AI from diagnosing, overwriting Urgency (`SafetyService`), or fabricating Provider data.
- **Structured Context**: The LLM parses a JSON dump of the deterministic response and wraps it in a conversational reply.

## Fallback Behavior & Error Handling
- If `GEMINI_API_KEY` is not present, the `llm_service` smoothly falls back to returning a static conversational response without failing the request.
- Handles external API errors (like timeouts) by generating the same deterministic fallback message, preventing server 500 errors when communicating with Google.

## Tests Strategy
- Created mock-driven testing in `test_llm.py` and `test_chat.py` to simulate missing keys, model failures, and successful outputs.
- Confirmed that no actual `gemini` request is made during testing to preserve API limits and execution speed.
- Verified that all 40 prior tests ran seamlessly without modification.

## Limitations
- Generative AI is strictly confined. It will summarize medical text, but cannot be relied on to generate novel clinical advice outside what the raw ML model prescribes.
