from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse
from app.services.nlp_service import nlp_service
from app.services.llm_service import llm_service
from app.routes.prediction import _build_prediction_response

router = APIRouter()

@router.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Phase 3: Conversational endpoint.
    Orchestrates the deterministic pipeline and returns a natural language response wrapped around it.
    """
    extracted = nlp_service.extract_symptoms(request.message)
    
    if not extracted:
        # We can still return a fallback saying we didn't understand the symptoms.
        # But we must fulfill the ChatResponse schema which requires PredictionResponse fields.
        # It's safer to raise 422 if no symptoms, as the model needs them to predict.
        raise HTTPException(
            status_code=422,
            detail="No recognized symptoms found in the text. Please provide valid symptoms."
        )
        
    # Run the existing, unified deterministic backend analysis pipeline
    prediction_response = _build_prediction_response(extracted, {"message": request.message})
    
    # Generate natural language
    ai_text = llm_service.generate_response(request.message, prediction_response)
    
    # Bundle the ChatResponse
    return ChatResponse(
        success=prediction_response.success,
        input=prediction_response.input,
        recognized_symptoms=prediction_response.recognized_symptoms,
        unknown_symptoms=prediction_response.unknown_symptoms,
        predictions=prediction_response.predictions,
        symptom_severity=prediction_response.symptom_severity,
        urgency=prediction_response.urgency,
        specialist_recommendation=prediction_response.specialist_recommendation,
        disclaimer=prediction_response.disclaimer,
        response=ai_text
    )
