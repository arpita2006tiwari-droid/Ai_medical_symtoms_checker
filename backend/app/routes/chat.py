from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.conversation import Conversation, ConversationMessage
from app.schemas import ChatRequest, ChatResponse
from app.services.nlp_service import nlp_service
from app.services.llm_service import llm_service
from app.routes.prediction import _build_prediction_response
from app.services.auth_service import get_optional_current_user

router = APIRouter()

@router.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_optional_current_user)):
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
    # We pass db and current_user to save the Analysis automatically via _build_prediction_response
    prediction_response = _build_prediction_response(extracted, {"message": request.message}, db, current_user, "chat")
    
    # Generate natural language
    ai_text = llm_service.generate_response(request.message, prediction_response)
    
    # Save the conversation if user is logged in
    if current_user and db:
        if request.conversation_id:
            conv = db.query(Conversation).filter(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id).first()
            if not conv:
                # If they passed an invalid ID, create a new one to be safe, or throw 404. Creating new is safer.
                conv = Conversation(user_id=current_user.id, title=request.message[:50])
                db.add(conv)
                db.commit()
                db.refresh(conv)
        else:
            conv = Conversation(user_id=current_user.id, title=request.message[:50])
            db.add(conv)
            db.commit()
            db.refresh(conv)
            
        # Add messages
        msg_user = ConversationMessage(conversation_id=conv.id, role="user", content=request.message)
        msg_ai = ConversationMessage(conversation_id=conv.id, role="assistant", content=ai_text)
        db.add_all([msg_user, msg_ai])
        db.commit()
    
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
