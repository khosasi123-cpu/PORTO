from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.retrieval import retrieval
from services.doc_retrieval import get_document_path
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

@router.get("/documents/{document_name}")
def download_document(document_name: str):

    try:
        path = get_document_path(document_name)

        return FileResponse(
            path=path,
            filename=path.name
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
