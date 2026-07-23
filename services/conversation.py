from sqlalchemy.orm import Session
from fastapi import HTTPException
from database.model.conversation import Conversation
from database.crud.conversation import create_conversation, get_conversation_by_id, get_all_conversations, delete_conversation, update_conversation_name
from database.crud.messages import create_message, get_recent_messages

def create_new_conversation(db: Session, name: str = "New Conversation") -> Conversation:
    """
    Create a new conversation.
    """
    return create_conversation(db, title=name)

def get_conversation(db: Session, conversation_id: int) -> Conversation:
    """
    Get a conversation by its ID.
    """
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

def get_all_conversations(db: Session) -> list[Conversation]:
    """
    Get all conversations.
    """
    return get_all_conversations(db)

def delete_conversation(db: Session, conversation: Conversation) -> None:
    """
    Delete a conversation.
    """
    coversation = get_conversation_by_id(db, conversation.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")  
    delete_conversation(db, conversation)

def update_conversation_title(db: Session, conversation: Conversation, new_title: str) -> Conversation:
    """
    Update the title of a conversation.
    """
    conversation = get_conversation_by_id(db, conversation.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return update_conversation_name(db, conversation, new_title)

def create_new_message(db: Session, conversation_id: int, role: str, content: str):
    """
    Create a new message in a conversation.
    """
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return create_message(db, conversation_id, role, content)

def get_recent_messages_for_conversation(db: Session, conversation_id: int, limit: int = 10):
    """
    Get the most recent messages for a conversation.
    """
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return get_recent_messages(db, conversation_id, limit)