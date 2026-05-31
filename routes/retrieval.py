from fastapi import APIRouter
from services.retriveal import retriveal


router = APIRouter(
    prefix="/retriveal",
    tags=["retriveal"]
)

@router.get("/retrieval")
def retriveal_document(question : str):
    return retriveal(question)
