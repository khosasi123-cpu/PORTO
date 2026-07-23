from pydantic import BaseModel


class MessageResponse(BaseModel):
    """
    Chat message.
    """

    id: int
    role: str
    content: str

    model_config = {
        "from_attributes": True
    }