from pathlib import Path
from sqlalchemy.orm import Session
from tools.docx_parser import parse_docx
from services.ingest import ingest_new_document
from database.crud import create_document, create_document_images
from langchain_core.documents import Document

DOCUMENT_DIR = (Path(__file__).parent.parent / "storage" / "document").resolve()

def get_document_path(document_name: str) -> Path:
    path = DOCUMENT_DIR / document_name

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {document_name}"
        )

    return path

def add_document(db : Session, doc_path:Path):
    doc = parse_docx(doc_path)
    document_db = create_document(
        db,
        document_name= doc_path.name,
        path=doc_path
    )
    images_db = create_document_images(
        db,
        document_db.id,
        doc.images
    )
    document = [Document(
        page_content =doc.text,
        metadata = {"source" : str(doc_path),
                    "document_name" : doc_path.name,
                    "document_id" : document_db.id}
    )]
    ingest_new_document(document)


if __name__=="__main__":
    print(get_document_path("HUMS_installation.md"))