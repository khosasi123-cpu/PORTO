from fastapi import APIRouter
from services.retrieval import retrieval
from schemas import retrieval as retrieval_schemas


router = APIRouter(
    prefix="/retrieve",
    tags=["retrieve"]
)

@router.post("/", response_model=retrieval_schemas.RetrievalResponse)
def retrieve_document(question : str):
    data = []
    points = retrieval(question)
    for point, scores in points:
        data.append({
            "score" : scores,
            "document_name" : point.payload["document_name"],
            "chunk_id" : point.payload["chunk_id"],
            "text" : point.payload["text"]
        })
    return {"results" : data}


