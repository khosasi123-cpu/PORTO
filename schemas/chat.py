from pydantic import BaseModel

class Question(BaseModel):
    question : str

class ChatResult(BaseModel):
    answear : str
    source : list[str]