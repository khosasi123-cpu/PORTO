from pydantic import BaseModel, Field

class RetrievalResult(BaseModel):
    score : float
    document_name : str
    chunk_id : str
    text : str

class RetrievalRequest(BaseModel):
    query : str

class RetrievalResponse(BaseModel):
    results : list[RetrievalResult]