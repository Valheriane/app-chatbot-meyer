from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message


router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("")
def list_conversations(db: Session = Depends(get_db)):
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()

    return [
        {
            "id": conv.id,
            "title": conv.title,
            "mode": conv.mode,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
        }
        for conv in conversations
    ]


@router.get("/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)

    if conversation is None:
        return {"error": "Conversation introuvable."}

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return {
        "id": conversation.id,
        "title": conversation.title,
        "mode": conversation.mode,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }