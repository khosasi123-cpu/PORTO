from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from services.chat import chat as chat_with_AI
from schemas.chat import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/", response_model=ChatResponse)
def create_chat(question :  ChatRequest, db : Session = Depends(get_db)):
    return chat_with_AI(
        user_request=question,
        db=db
    )   