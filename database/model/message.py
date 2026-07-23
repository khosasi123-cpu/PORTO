from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role = Column(
        String,
        nullable=False
    )
    content = Column(
        String,
        nullable=False
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )