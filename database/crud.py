from sqlalchemy.orm import Session

from database.model import Document


def create_document(
    db: Session,
    document_name: str,
    path: str
) -> Document:
    """
    Create new document metadata.
    """

    document = Document(
        document_name=document_name,
        path=str(path)
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document(
    db: Session,
    document_id: str
) -> Document | None:
    """
    Get document by id.
    """

    return (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )


def get_document_by_name(
    db: Session,
    document_name: str
) -> Document | None:
    """
    Get document by filename.
    """

    return (
        db.query(Document)
        .filter(Document.document_name == document_name)
        .first()
    )


def get_all_documents(
    db: Session
) -> list[Document]:
    """
    Get all documents.
    """

    return (
        db.query(Document)
        .order_by(Document.document_name)
        .all()
    )


def update_document(
    db: Session,
    document: Document,
    document_name: str | None = None,
    path: str | None = None
) -> Document:
    """
    Update document metadata.
    """

    if document_name is not None:
        document.document_name = document_name

    if path is not None:
        document.path = path

    db.commit()
    db.refresh(document)

    return document


def delete_document(
    db: Session,
    document: Document
) -> None:
    """
    Delete document metadata.
    """

    db.delete(document)
    db.commit()