from sqlalchemy.orm import Session

from database.model.message import Message

def create_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    Create a new message.
    """

    message = Message(
        conversation_id=conversation_id,
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

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )