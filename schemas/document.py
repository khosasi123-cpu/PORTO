from pydantic import BaseModel, Field

class DocumentResult(BaseModel):
    document_name: str = Field(
        ...,
        description="The name of the document"
    )