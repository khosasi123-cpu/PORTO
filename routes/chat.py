from fastapi import APIRouter
from services.chat import chat as chat_with_AI
from schemas.chat import ChatRequest, ChatResult

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/", response_model=ChatResult)
def create_chat(question :  ChatRequest):
    response = chat_with_AI(question)
    return response