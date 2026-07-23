from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime, UTC

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True
    )
    title = Column(
        String,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )