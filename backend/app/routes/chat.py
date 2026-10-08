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
    
    # Run the existing, unified deterministic backend analysis pipeline
    # We pass db and current_user to save the Analysis automatically via _build_prediction_response
    demographics = {"age": request.age, "age_unit": request.age_unit, "gender": request.gender, "patient_type": request.patient_type} if request.age or request.gender or request.patient_type else None
    prediction_response = _build_prediction_response(extracted, {"message": request.message}, db, current_user, "chat", demographics)
    
    conversation_history = []
    patient_context = ""

    # Check for relevant patient context if logged in
    if current_user and db:
        # Get conversation history if continuing a chat
        if request.conversation_id:
            conv = db.query(Conversation).filter(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id).first()
            if conv:
                # get last 8 messages for context
                for msg in conv.messages[-8:]:
                    conversation_history.append({"role": msg.role, "content": msg.content})
        
        # Build patient context based on keywords
        lower_msg = request.message.lower()
        
        # 1. Pain assessments
        if any(k in lower_msg for k in ["pain", "hurt", "ache", "sore", "cramp"]):
            from app.db.models.pain_assessment import PainAssessment
            recent_pain = db.query(PainAssessment).filter(PainAssessment.user_id == current_user.id).order_by(PainAssessment.created_at.desc()).first()
            if recent_pain:
                patient_context += f"Recent Pain Assessment: {recent_pain.body_region} ({recent_pain.pain_type}), Severity: {recent_pain.severity}/10.\n"
                
        # 2. Menstruation
        if any(k in lower_msg for k in ["period", "menstrua", "cycle", "bleed"]):
            from app.db.models.menstruation import MenstrualCycle
            recent_cycle = db.query(MenstrualCycle).filter(MenstrualCycle.user_id == current_user.id).order_by(MenstrualCycle.start_date.desc()).first()
            if recent_cycle:
                patient_context += f"Recent Menstrual Cycle started on: {recent_cycle.start_date}, Flow: {recent_cycle.flow_intensity}.\n"
                
        # 3. Mood
        if any(k in lower_msg for k in ["mood", "sad", "depress", "anxi", "stress", "tired", "sleep"]):
            from app.db.models.mood import MoodCheckin
            recent_mood = db.query(MoodCheckin).filter(MoodCheckin.user_id == current_user.id).order_by(MoodCheckin.created_at.desc()).first()
            if recent_mood:
                patient_context += f"Recent Mood Check-in: {recent_mood.mood} (Intensity: {recent_mood.intensity}/10), Energy: {recent_mood.energy_level}, Sleep: {recent_mood.sleep_quality}.\n"
                
        # 4. Recent Analysis
        from app.db.models.analysis import Analysis
        recent_analysis = db.query(Analysis).filter(Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).first()
        if recent_analysis:
            patient_context += f"Most Recent Symptom Analysis extracted: {', '.join(recent_analysis.recognized_symptoms) if recent_analysis.recognized_symptoms else 'None'}. "
            if recent_analysis.predictions and isinstance(recent_analysis.predictions, list) and len(recent_analysis.predictions) > 0:
                patient_context += f"Top prediction: {recent_analysis.predictions[0].get('condition', 'Unknown')}.\n"
            else:
                patient_context += "No top prediction.\n"

    # Generate natural language
    ai_text = llm_service.generate_response(request.message, prediction_response, conversation_history, patient_context)
    
    # Save the conversation if user is logged in
    if current_user and db:
        if request.conversation_id:
            conv = db.query(Conversation).filter(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id).first()
            if not conv:
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
        
        # Ensure conversation ID is updated for response
        prediction_response = prediction_response.model_dump()
        prediction_response["conversation_id"] = conv.id
    else:
        prediction_response = prediction_response.model_dump()
        prediction_response["conversation_id"] = None
    
    # Bundle the ChatResponse
    return ChatResponse(
        success=prediction_response["success"],
        input=prediction_response["input"],
        recognized_symptoms=prediction_response["recognized_symptoms"],
        unknown_symptoms=prediction_response["unknown_symptoms"],
        predictions=prediction_response["predictions"],
        symptom_severity=prediction_response["symptom_severity"],
        urgency=prediction_response["urgency"],
        specialist_recommendation=prediction_response["specialist_recommendation"],
        disclaimer=prediction_response["disclaimer"],
        response=ai_text,
        conversation_id=prediction_response["conversation_id"]
    )
