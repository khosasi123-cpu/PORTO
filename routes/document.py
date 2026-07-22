from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
import shutil
from sqlalchemy.orm import Session
from pathlib import Path
from services.retrieval import retrieval
from services.document import get_document_path, DOCUMENT_DIR, add_document, delete_document as del_doc
from database.crud import get_all_documents
from schemas import retrieval as retrieval_schemas
from database.database import get_db


router = APIRouter(
    prefix="/document",
    tags=["document"]
)


@router.post("/search", response_model=retrieval_schemas.RetrievalResponse)
def retrieve_document(question : str):
    """
    fungsi untuk cari dokumen berdasarkan vector
    """
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

@router.get("/{document_name}")
def download_document(document_name: str): 
    """
    fungsi untuk download document
    """
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
@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    DOCUMENT_DIR.mkdir(
    parents=True,
    exist_ok=True
)
    destination = DOCUMENT_DIR / file.filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    return add_document(
        db=db,
        doc_path=destination
    )

@router.get(
    "/",
)
def get_documents(
    db: Session = Depends(get_db)
):

    documents = get_all_documents(db)

    return {
        "documents": documents
    }

@router.delete("/{document_name}")
def delete_document(
    document_name : str,
    db: Session = Depends(get_db),
                    ):
    del_doc(
        db=db,
        document_name=document_name
    )
    return {
        "message": "Document deleted successfully."
    }
