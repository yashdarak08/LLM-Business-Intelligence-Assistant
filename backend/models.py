# backend/models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class QueryRequest(BaseModel):
    query: str
    structured_output: bool = Field(default=False, description="Return response in structured JSON format")

class ChunkData(BaseModel):
    file_path: Optional[str] = None
    chunk_index: Optional[int] = None
    text: str
    title: Optional[str] = None
    relevance_score: Optional[float] = None

class StructuredResponse(BaseModel):
    summary: str
    key_insights: List[str]
    recommendations: List[str]
    sources: Optional[List[str]] = None
    error: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    retrieved_chunks: List[Dict[str, Any]]
    answer: Union[str, StructuredResponse]
    processing_time_ms: Optional[float] = None

class IngestResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DocumentStats(BaseModel):
    total_documents: int
    total_chunks: int
    average_chunks_per_doc: float
    indexed_documents: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    components: Dict[str, str]
    database: Optional[Dict[str, Any]] = None

class MetricResponse(BaseModel):
    query_count: int
    average_response_time_ms: float
    documents_count: int
    chunks_count: int