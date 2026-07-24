from sqlalchemy.orm import Session
from datetime import datetime, UTC

from database.model.conversation import Conversation
from database.model.message import Message

def create_message(
    db: Session,
    conversation: Conversation,
    role: str,
    content: str
) -> Message:
    """
    Create a new message.
    """
    conversation.updated_at = datetime.now(UTC)

    message = Message(
        conversation_id=conversation.id,
        role=role,
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

def get_recent_messages(
    db: Session,
    conversation_id: int,
    limit: int = 10
) -> list[Message]:
    """
    Get the most recent messages for a conversation.
    """

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return messages