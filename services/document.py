from pathlib import Path
from sqlalchemy.orm import Session
from tools.docx_parser import parse_docx
from tools.delete_images import delete_images, delete_file
from services.ingest import ingest_new_document, delete_document_vector
from database.crud.document import create_document, create_document_images, get_document_by_name, delete_document_db
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()


DOCUMENT_DIR = Path(os.getenv("DOCUMENT_DIRECTORY")).resolve()

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

def delete_document(db: Session,
                    document_name:str
                    ):
    document = get_document_by_name(db,
                                    document_name=document_name)
    if document is None:
        raise

    delete_document_vector(
        document.id
    )
    delete_images(
        document.images
    )
    delete_file(
        document.path
    )
    delete_document_db(db,
           document)

if __name__=="__main__":
    print(get_document_path("HUMS_installation.md"))