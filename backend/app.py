# backend/app.py

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.models import QueryRequest, QueryResponse, IngestResponse
from backend.retrieval import retrieve_relevant_chunks
from backend.llm_integration import generate_response
from backend.data_preprocessing import preprocess_and_index_documents
from backend.logging_config import setup_logging  # ensures logging is configured
from backend.monitoring import router as metrics_router
from prometheus_client import Counter

logger = logging.getLogger(__name__)

# Prometheus metric to count requests
REQUEST_COUNT = Counter("request_count", "App Request Count", ["method", "endpoint", "http_status"])

app = FastAPI(
    title="Business Intelligence Assistant API",
    description="An API that ingests business documents, performs semantic retrieval, and generates insights using LLMs.",
    version="1.0.0"
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
async def add_prometheus_metrics(request: Request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code)
    return response

@app.get("/")
def root():
    return {"message": "Welcome to the Business Intelligence Assistant API!"}

@app.post("/ingest", response_model=IngestResponse)
def ingest_documents():
    """
    Endpoint to ingest and index business documents.
    """
    try:
        preprocess_and_index_documents()
        return IngestResponse(status="success", message="Documents ingested and indexed successfully.")
    except Exception as e:
        logger.error("Error during ingestion: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
def query_endpoint(query_request: QueryRequest):
    """
    Endpoint to process a business query.
    Retrieves relevant document chunks and generates an LLM-based answer.
    """
    query = query_request.query
    retrieved_chunks = retrieve_relevant_chunks(query)
    
    if not retrieved_chunks:
        error_msg = "No relevant documents found. Please ensure documents have been ingested."
        logger.warning(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)

    answer = generate_response(query, retrieved_chunks)
    return QueryResponse(query=query, retrieved_chunks=retrieved_chunks, answer=answer)
