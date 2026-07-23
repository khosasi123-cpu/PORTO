from datetime import datetime

from pydantic import BaseModel, Field

from schemas.message import MessageResponse


class ConversationUpdateRequest(BaseModel):
    """
    Request body for updating a conversation title.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Conversation title."
    )


class ConversationSummaryResponse(BaseModel):
    """
    Conversation information for sidebar.
    """

    id: int
    title: str
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ConversationResponse(BaseModel):
    """
    Full conversation with messages.
    """

    id: int
    title: str
    updated_at: datetime
    messages: list[MessageResponse]

    model_config = {
        "from_attributes": True
    }