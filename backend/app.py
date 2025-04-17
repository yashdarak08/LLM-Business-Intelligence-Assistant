# backend/app.py

import logging
import time
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import pkg_resources
from backend.models import (
    QueryRequest, QueryResponse, IngestResponse, 
    StructuredResponse, HealthResponse, MetricResponse,
    DocumentStats
)
from backend.retrieval import retrieve_relevant_chunks
from backend.llm_integration import generate_response, generate_structured_response
from backend.data_preprocessing import preprocess_and_index_documents
from backend.logging_config import setup_logging  # ensures logging is configured
from backend.monitoring import router as metrics_router
from backend.database import get_db, Document, DocumentChunk, Query
from prometheus_client import Counter, Histogram
import sqlalchemy as sa
from backend.config import API_PORT
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter("request_count", "App Request Count", ["method", "endpoint", "http_status"])
RESPONSE_TIME = Histogram("response_time", "Response Time in seconds", ["endpoint"])

# Get version from package resources or environment variable
try:
    version = pkg_resources.get_distribution("business-intelligence-assistant").version
except:
    version = os.environ.get("APP_VERSION", "1.0.0")

app = FastAPI(
    title="Business Intelligence Assistant API",
    description="An API that ingests business documents, performs semantic retrieval, and generates insights using LLMs.",
    version=version
)

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the metrics router
app.include_router(metrics_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to track request processing time and update Prometheus metrics."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Record metrics
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    if hasattr(RESPONSE_TIME, '_labels'):  # Check if the endpoint label exists
        RESPONSE_TIME.labels(request.url.path).observe(process_time)
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to provide consistent error responses."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An unexpected error occurred", "detail": str(exc)}
    )

@app.get("/", response_model=Dict[str, Any])
def root():
    return {"message": "Welcome to the Business Intelligence Assistant API!", "version": version}

@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify the service status."""
    try:
        # Check database connection
        db_status = "healthy"
        db_version = db.execute(sa.text("SELECT version()")).scalar()
        doc_count = db.query(Document).count()
        
        # Check components
        components = {
            "database": "connected",
            "embedding_model": "loaded",
            "llm_model": "loaded"
        }
        
        return HealthResponse(
            status="healthy",
            version=version,
            components=components,
            database={
                "status": db_status,
                "version": db_version,
                "document_count": doc_count
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")

@app.get("/stats", response_model=DocumentStats)
def get_stats(db: Session = Depends(get_db)):
    """Get statistics about ingested documents."""
    try:
        # Get document counts
        total_documents = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        
        # Calculate average chunks per document
        avg_chunks = total_chunks / total_documents if total_documents > 0 else 0
        
        # Get list of indexed documents
        documents = db.query(
            Document.id, Document.file_path, Document.title, 
            Document.ingestion_date, sa.func.count(DocumentChunk.id).label("chunk_count")
        ).join(Document.chunks).group_by(Document.id).all()
        
        # Format document data
        indexed_docs = [
            {
                "id": doc.id,
                "file_path": doc.file_path,
                "title": doc.title,
                "ingestion_date": doc.ingestion_date.isoformat(),
                "chunk_count": doc.chunk_count
            }
            for doc in documents
        ]
        
        return DocumentStats(
            total_documents=total_documents,
            total_chunks=total_chunks,
            average_chunks_per_doc=avg_chunks,
            indexed_documents=indexed_docs
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/query", response_model=MetricResponse)
def get_query_metrics(db: Session = Depends(get_db)):
    """Get metrics about query performance."""
    try:
        # Get query counts
        query_count = db.query(Query).count()
        
        # Get average response time
        avg_response_time = db.query(sa.func.avg(Query.response_time)).scalar() or 0
        
        # Get document counts
        documents_count = db.query(Document).count()
        chunks_count = db.query(DocumentChunk).count()
        
        return MetricResponse(
            query_count=query_count,
            average_response_time_ms=avg_response_time,
            documents_count=documents_count,
            chunks_count=chunks_count
        )
    except Exception as e:
        logger.error(f"Error getting query metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest", response_model=IngestResponse)
def ingest_documents(background_tasks: BackgroundTasks):
    """
    Endpoint to ingest and index business documents.
    Processes the documents in the background to avoid blocking the API.
    """
    try:
        # Start ingestion in the background
        background_tasks.add_task(preprocess_and_index_documents)
        return IngestResponse(
            status="success", 
            message="Document ingestion started in the background. Check /stats for progress."
        )
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
def query_endpoint(query_request: QueryRequest, db: Session = Depends(get_db)):
    """
    Endpoint to process a business query.
    Retrieves relevant document chunks and generates an LLM-based answer.
    Optionally returns a structured response in JSON format.
    """
    start_time = time.time()
    query = query_request.query
    use_structured_output = query_request.structured_output
    
    try:
        # Retrieve relevant chunks
        retrieved_chunks = retrieve_relevant_chunks(query, db)
        
        if not retrieved_chunks:
            error_msg = "No relevant documents found. Please ensure documents have been ingested."
            logger.warning(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Generate response
        if use_structured_output:
            answer = generate_structured_response(query, retrieved_chunks)
        else:
            answer = generate_response(query, retrieved_chunks)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return QueryResponse(
            query=query,
            retrieved_chunks=retrieved_chunks,
            answer=answer,
            processing_time_ms=processing_time
        )
    except FileNotFoundError:
        error_msg = "No document index found. Please ingest documents first."
        logger.warning(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))