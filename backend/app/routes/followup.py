from fastapi import APIRouter
from app.schemas import (
    FollowUpStartRequest,
    FollowUpAnswerRequest,
    FollowUpResponse,
    FollowUpState,
    FollowUpQuestion
)
from app.services.followup_service import followup_service

router = APIRouter()

@router.post("/api/follow-up/start", response_model=FollowUpResponse)
def start_followup(request: FollowUpStartRequest):
    """Initializes the follow-up state and returns the first question if applicable."""
    state = FollowUpState(
        recognized_symptoms=request.symptoms,
        asked_questions=[],
        answers={},
        follow_up_count=0
    )
    
    question_dict = followup_service.get_next_question(state.recognized_symptoms, state.asked_questions)
    
    if not question_dict:
        return FollowUpResponse(state=state, question=None, complete=True)
        
    question = FollowUpQuestion(**question_dict)
    return FollowUpResponse(state=state, question=question, complete=False)

@router.post("/api/follow-up/answer", response_model=FollowUpResponse)
def answer_followup(request: FollowUpAnswerRequest):
    """Processes the answer, updates state, and returns the next question or completion."""
    # Process the answer
    updated_state = followup_service.process_answer(
        request.state,
        request.question_id,
        request.answer
    )
    
    # Check limit
    if updated_state.follow_up_count >= followup_service.MAX_FOLLOW_UP_QUESTIONS:
        return FollowUpResponse(state=updated_state, question=None, complete=True)
        
    # Get next question
    question_dict = followup_service.get_next_question(
        updated_state.recognized_symptoms,
        updated_state.asked_questions
    )
    
    if not question_dict:
        return FollowUpResponse(state=updated_state, question=None, complete=True)
        
    question = FollowUpQuestion(**question_dict)
    return FollowUpResponse(state=updated_state, question=question, complete=False)
