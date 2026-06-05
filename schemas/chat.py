from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id : str
    question : str

class ChatResult(BaseModel):
    answear : str
    source : list[str]