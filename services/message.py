from fastapi import HTTPException
from sqlalchemy.orm import Session

from services.conversation import _require_conversation
from database.model.message import Message
from database.crud import messages as message_crud


def create_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    Create a new message.
    """

    _require_conversation(
        db,
        conversation_id
    )

    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    return message_crud.create_message(
        db=db,
        conversation_id=conversation_id,
        role=role,
        content=content
    )


def get_recent_messages(
    db: Session,
    conversation_id: int,
    limit: int = 10
) -> list[Message]:
    """
    Get recent messages in a conversation.
    """

    _require_conversation(
        db,
        conversation_id
    )

    return message_crud.get_recent_messages(
        db=db,
        conversation_id=conversation_id,
        limit=limit
    )