# backend/models.py

from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    retrieved_chunks: List[dict]
    answer: str

class IngestResponse(BaseModel):
    status: str
    message: Optional[str]
    data: Optional[dict] = None
    error: Optional[str] = None
    