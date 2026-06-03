from fastapi import APIRouter
from services.chat import chat as chat_with_AI
from schemas.chat import Question, ChatResult

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/", response_model=ChatResult)
def create_chat(question :  Question):
    response = chat_with_AI(question.question)
    return response