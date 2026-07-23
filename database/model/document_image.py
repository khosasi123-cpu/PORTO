from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class DocumentImage(Base):
    __tablename__ = "documentimage"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    document_id = Column(
        String,
        ForeignKey("document.id", ondelete="CASCADE")
    )
    filename = Column(
        String,
        nullable=False
    )

    document = relationship(
        "Document",
        back_populates="images"
    )