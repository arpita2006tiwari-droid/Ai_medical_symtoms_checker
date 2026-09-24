from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.conversation import Conversation
from app.schemas import ConversationResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.get("", response_model=list[ConversationResponse])
def get_conversations(limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # To prevent over-fetching, you might not return 'messages' here or load them lazily
    # But for simplicity we return them based on the schema mapping
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id)\
                      .order_by(Conversation.updated_at.desc())\
                      .offset(offset).limit(limit).all()
    return conversations

@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return {"success": True, "message": "Conversation deleted"}
