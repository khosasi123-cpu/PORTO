from pydantic import BaseModel, Field, ConfigDict

class DocumentResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    document_name: str = Field(
        ...,
        description="The name of the document"
    )