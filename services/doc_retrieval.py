from pathlib import Path

DOCUMENT_DIR = (Path(__file__).parent.parent / "data" / "troubleshooting").resolve()

def get_document_path(document_name: str) -> Path:
    path = DOCUMENT_DIR / document_name

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {document_name}"
        )

    return path

if __name__=="__main__":
    print(get_document_path("HUMS_installation.md"))