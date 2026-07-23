from sqlalchemy.orm import Session, joinedload
from datetime import datetime, UTC

from database.model.conversation import Conversation
from database.model.message import Message

def create_conversation(
    db: Session,
    title: str
) -> Conversation:
    """
    Create a new conversation.
    """

    conversation = Conversation(
        title=title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

def get_conversation_by_id(
    db: Session,
    conversation_id: int
) -> Conversation | None:
    """
    Get a conversation by its ID.
    """

    return (
        db.query(Conversation)
        .options(joinedload(Conversation.messages))
        .filter(Conversation.id == conversation_id)
        .first()
    )

def get_all_conversations(
    db: Session
) -> list[Conversation]:
    """
    Get all conversations.
    """

    return (
        db.query(Conversation)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

def delete_conversation(
    db: Session,
    conversation: Conversation
) -> None:
    """
    Delete a conversation.
    """

    db.delete(conversation)
    db.commit()

def update_conversation_title(
    db: Session,
    conversation: Conversation,
    new_title: str
) -> Conversation:
    """
    Update the title of a conversation.
    """

    conversation.title = new_title
    conversation.updated_at = datetime.now(UTC)
    db.commit()

    return conversation