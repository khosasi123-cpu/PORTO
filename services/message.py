from fastapi import HTTPException
from sqlalchemy.orm import Session

from services.conversation import _require_conversation
from database.model.message import Message
from database.crud import messages as message_crud

VALID_ROLES = {
    "user",
    "assistant"
}

def create_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    Create a new message.
    """

    conversation = _require_conversation(
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
        conversation=conversation,
        role=role,
        content=content
    )


def get_recent_messages(
    db: Session,
    conversation_id: int,
    limit: int = 10
) -> list[dict]:
    """
    Get recent messages in a conversation.
    """

    _require_conversation(
        db,
        conversation_id
    )

    message_db = message_crud.get_recent_messages(
        db=db,
        conversation_id=conversation_id,
        limit=limit
    )
    return [{
        "role": message.role,
        "content": message.content
    } for message in message_db]
